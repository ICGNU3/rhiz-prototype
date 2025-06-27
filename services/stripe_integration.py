"""
Stripe integration for subscription billing and payment processing
Handles Founder+ tier upgrades and webhook processing
"""

import os
import logging
import json
from typing import Dict, Any, Optional
import stripe
from auth import SubscriptionManager

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class StripePaymentManager:
    def __init__(self, db):
        self.db = db
        self.subscription_manager = SubscriptionManager(db)
        
        # Stripe configuration
        self.webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        
        # Product and price configuration
        self.products = {
            'founder_plus_monthly': {
                'name': 'Founder+ Monthly',
                'price': 1900,  # $19.00 in cents
                'interval': 'month',
                'tier': 'founder_plus'
            },
            'founder_plus_yearly': {
                'name': 'Founder+ Yearly',
                'price': 18000,  # $180.00 in cents (save $48)
                'interval': 'year',
                'tier': 'founder_plus'
            }
        }
    
    def create_customer(self, email: str, user_id: str, name: str = None) -> Optional[str]:
        """Create a Stripe customer for the user"""
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={'user_id': user_id},
                name=name
            )
            
            # Update user with Stripe customer ID
            conn = self.db.get_connection()
            try:
                conn.execute(
                    "UPDATE users SET stripe_customer_id = ?, updated_at = datetime('now') WHERE id = ?",
                    (customer.id, user_id)
                )
                conn.commit()
            finally:
                conn.close()
            
            logging.info(f"Created Stripe customer {customer.id} for user {user_id}")
            return customer.id
            
        except stripe.error.StripeError as e:
            logging.error(f"Failed to create Stripe customer: {e}")
            return None
    
    def create_checkout_session(self, user_id: str, plan: str, success_url: str, cancel_url: str) -> Optional[Dict[str, Any]]:
        """Create a Stripe checkout session for subscription upgrade"""
        try:
            # Get or create Stripe customer
            user = self.subscription_manager.get_user_with_usage(user_id)
            if not user:
                return None
            
            customer_id = user.get('stripe_customer_id')
            if not customer_id:
                customer_id = self.create_customer(user['email'], user_id)
                if not customer_id:
                    return None
            
            # Get product configuration
            product_config = self.products.get(plan)
            if not product_config:
                logging.error(f"Unknown plan: {plan}")
                return None
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_config['name'],
                            'description': 'Unlimited goals, contacts, AI outreach, and premium features'
                        },
                        'unit_amount': product_config['price'],
                        'recurring': {
                            'interval': product_config['interval']
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'user_id': user_id,
                    'plan': plan,
                    'tier': product_config['tier']
                }
            )
            
            return {
                'session_id': session.id,
                'url': session.url
            }
            
        except stripe.error.StripeError as e:
            logging.error(f"Failed to create checkout session: {e}")
            return None
    
    def handle_webhook(self, payload: str, signature: str) -> bool:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
        except ValueError:
            logging.error("Invalid payload in Stripe webhook")
            return False
        except stripe.error.SignatureVerificationError:
            logging.error("Invalid signature in Stripe webhook")
            return False
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            self._handle_successful_payment(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            self._handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            self._handle_subscription_canceled(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            self._handle_payment_failed(event['data']['object'])
        else:
            logging.info(f"Unhandled Stripe event type: {event['type']}")
        
        return True
    
    def _handle_successful_payment(self, session):
        """Handle successful payment from checkout session"""
        try:
            user_id = session['metadata'].get('user_id')
            plan = session['metadata'].get('plan')
            tier = session['metadata'].get('tier')
            
            if not all([user_id, plan, tier]):
                logging.error("Missing metadata in successful payment")
                return
            
            # Get the subscription
            subscription_id = session.get('subscription')
            if subscription_id:
                subscription = stripe.Subscription.retrieve(subscription_id)
                
                # Upgrade user subscription
                self.subscription_manager.upgrade_user_subscription(
                    user_id=user_id,
                    new_tier=tier,
                    stripe_customer_id=session['customer'],
                    stripe_subscription_id=subscription_id
                )
                
                logging.info(f"Successfully upgraded user {user_id} to {tier}")
            
        except Exception as e:
            logging.error(f"Error handling successful payment: {e}")
    
    def _handle_subscription_updated(self, subscription):
        """Handle subscription updates"""
        try:
            customer_id = subscription['customer']
            
            # Find user by Stripe customer ID
            conn = self.db.get_connection()
            try:
                user = conn.execute(
                    "SELECT id FROM users WHERE stripe_customer_id = ?",
                    (customer_id,)
                ).fetchone()
                
                if user:
                    status = subscription['status']
                    
                    # Update subscription status
                    conn.execute(
                        """UPDATE users SET 
                           subscription_status = ?, 
                           stripe_subscription_id = ?,
                           updated_at = datetime('now') 
                           WHERE id = ?""",
                        (status, subscription['id'], user['id'])
                    )
                    conn.commit()
                    
                    logging.info(f"Updated subscription status for user {user['id']}: {status}")
            finally:
                conn.close()
                
        except Exception as e:
            logging.error(f"Error handling subscription update: {e}")
    
    def _handle_subscription_canceled(self, subscription):
        """Handle subscription cancellation"""
        try:
            customer_id = subscription['customer']
            
            # Find user by Stripe customer ID
            conn = self.db.get_connection()
            try:
                user = conn.execute(
                    "SELECT id FROM users WHERE stripe_customer_id = ?",
                    (customer_id,)
                ).fetchone()
                
                if user:
                    # Downgrade to free tier
                    conn.execute(
                        """UPDATE users SET 
                           subscription_tier = 'explorer',
                           subscription_status = 'canceled',
                           stripe_subscription_id = NULL,
                           updated_at = datetime('now') 
                           WHERE id = ?""",
                        (user['id'],)
                    )
                    
                    # Log subscription history
                    conn.execute(
                        """INSERT INTO subscription_history (id, user_id, action, from_tier, to_tier, stripe_event_id) 
                           VALUES (?, ?, 'canceled', 'founder_plus', 'explorer', ?)""",
                        (self._generate_uuid(), user['id'], subscription['id'])
                    )
                    
                    conn.commit()
                    logging.info(f"Downgraded user {user['id']} to explorer tier")
            finally:
                conn.close()
                
        except Exception as e:
            logging.error(f"Error handling subscription cancellation: {e}")
    
    def _handle_payment_failed(self, invoice):
        """Handle failed payment"""
        try:
            customer_id = invoice['customer']
            
            # Find user by Stripe customer ID
            conn = self.db.get_connection()
            try:
                user = conn.execute(
                    "SELECT id, email FROM users WHERE stripe_customer_id = ?",
                    (customer_id,)
                ).fetchone()
                
                if user:
                    # Update subscription status to past_due
                    conn.execute(
                        """UPDATE users SET 
                           subscription_status = 'past_due',
                           updated_at = datetime('now') 
                           WHERE id = ?""",
                        (user['id'],)
                    )
                    conn.commit()
                    
                    logging.warning(f"Payment failed for user {user['id']} - status set to past_due")
                    
                    # In production, you might want to send an email notification here
            finally:
                conn.close()
                
        except Exception as e:
            logging.error(f"Error handling payment failure: {e}")
    
    def get_subscription_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed subscription information for a user"""
        try:
            user = self.subscription_manager.get_user_with_usage(user_id)
            if not user or not user.get('stripe_subscription_id'):
                return None
            
            subscription = stripe.Subscription.retrieve(user['stripe_subscription_id'])
            
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'plan_amount': subscription['items']['data'][0]['price']['unit_amount'],
                'plan_interval': subscription['items']['data'][0]['price']['recurring']['interval']
            }
            
        except stripe.error.StripeError as e:
            logging.error(f"Failed to retrieve subscription details: {e}")
            return None
    
    def cancel_subscription(self, user_id: str, at_period_end: bool = True) -> bool:
        """Cancel a user's subscription"""
        try:
            user = self.subscription_manager.get_user_with_usage(user_id)
            if not user or not user.get('stripe_subscription_id'):
                return False
            
            stripe.Subscription.modify(
                user['stripe_subscription_id'],
                cancel_at_period_end=at_period_end
            )
            
            logging.info(f"Scheduled cancellation for user {user_id} subscription")
            return True
            
        except stripe.error.StripeError as e:
            logging.error(f"Failed to cancel subscription: {e}")
            return False
    
    def create_customer_portal_session(self, user_id: str, return_url: str) -> Optional[str]:
        """Create a Stripe customer portal session for subscription management"""
        try:
            user = self.subscription_manager.get_user_with_usage(user_id)
            if not user or not user.get('stripe_customer_id'):
                return None
            
            session = stripe.billing_portal.Session.create(
                customer=user['stripe_customer_id'],
                return_url=return_url
            )
            
            return session.url
            
        except stripe.error.StripeError as e:
            logging.error(f"Failed to create customer portal session: {e}")
            return None
    
    def _generate_uuid(self) -> str:
        """Generate a UUID for database records"""
        import uuid
        return str(uuid.uuid4())

class PricingHelper:
    """Helper class for pricing display and calculations"""
    
    @staticmethod
    def format_price(amount_cents: int) -> str:
        """Format price in cents to dollars"""
        return f"${amount_cents / 100:.0f}"
    
    @staticmethod
    def get_pricing_tiers() -> Dict[str, Any]:
        """Get pricing tier information for display"""
        return {
            'explorer': {
                'name': 'Explorer',
                'tagline': 'Perfect for getting started',
                'price_monthly': 0,
                'price_yearly': 0,
                'features': [
                    'Up to 1 goal',
                    'Up to 50 contacts',
                    '3 AI suggestions',
                    'Basic goal matching',
                    'Contact management'
                ],
                'limitations': [
                    'No email integration',
                    'No calendar sync',
                    'No network visualization',
                    'No conference mode'
                ],
                'cta': 'Get Started Free'
            },
            'founder_plus': {
                'name': 'Founder+',
                'tagline': 'Everything you need to build your network',
                'price_monthly': 19,
                'price_yearly': 180,
                'yearly_savings': 48,
                'features': [
                    'Unlimited goals',
                    'Up to 1,000 contacts',
                    'Unlimited AI outreach',
                    'Email & calendar integration',
                    'Network visualization',
                    'Conference mode',
                    'Analytics dashboard',
                    'CSV import/export',
                    'Background gamification',
                    'Priority support'
                ],
                'cta': 'Upgrade to Founder+'
            }
        }
    
    @staticmethod
    def calculate_savings(monthly_price: int, yearly_price: int) -> int:
        """Calculate yearly savings in cents"""
        return (monthly_price * 12) - yearly_price