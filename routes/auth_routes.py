"""
Authentication routes module
Handles signup, login, magic links, and subscription management
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from . import RouteBase, login_required, get_current_user
from stripe_integration import StripePaymentManager, PricingHelper
from utils.email import email_service as resend_email_service
import logging

# Create blueprint
auth_bp = Blueprint('auth_routes', __name__)

class AuthRoutes(RouteBase):
    def __init__(self):
        super().__init__()
        self.stripe_manager = StripePaymentManager(self.db)
        self.pricing_helper = PricingHelper()

auth_routes = AuthRoutes()

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup with email verification"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        subscription_tier = request.form.get('tier', 'explorer')
        
        if not email:
            flash('Email is required', 'error')
            return render_template('signup.html')
        
        try:
            # Create user account
            user_id = auth_routes.auth_manager.create_user(
                email=email, 
                subscription_tier=subscription_tier
            )
            
            if user_id:
                # Create magic link for verification
                magic_token = auth_routes.auth_manager.create_magic_link(email)
                base_url = request.host_url.rstrip('/')
                
                # Send welcome email with magic link
                success = resend_email_service.send_email(
                    to_email=email,
                    subject="Welcome to Rhiz - Verify Your Account",
                    html_content=f"""
                    <h2>Welcome to Rhiz!</h2>
                    <p>Click the link below to verify your account and start building your network:</p>
                    <p><a href="{base_url}/auth/verify/{magic_token}" 
                         style="background: #007bff; color: white; padding: 12px 24px; 
                                text-decoration: none; border-radius: 6px;">
                        Verify Account & Login
                    </a></p>
                    <p>If the button doesn't work, copy this link: {base_url}/auth/verify/{magic_token}</p>
                    """
                )
                
                if success:
                    flash('Account created! Check your email to verify and login.', 'success')
                else:
                    flash('Account created but email delivery failed. Contact support.', 'warning')
                
                return redirect('/login')
            else:
                flash('Failed to create account', 'error')
                
        except Exception as e:
            logging.error(f"Signup error: {e}")
            flash('An error occurred during signup', 'error')
    
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Magic link login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Email is required', 'error')
            return render_template('login.html')
        
        try:
            # Create magic link
            magic_token = auth_routes.auth_manager.create_magic_link(email)
            base_url = request.host_url.rstrip('/')
            
            # Send magic link email
            success = resend_email_service.send_email(
                to_email=email,
                subject="Your Rhiz Login Link",
                html_content=f"""
                <h2>Login to Rhiz</h2>
                <p>Click the link below to login to your account:</p>
                <p><a href="{base_url}/auth/verify/{magic_token}" 
                     style="background: #007bff; color: white; padding: 12px 24px; 
                            text-decoration: none; border-radius: 6px;">
                    Login to Rhiz
                </a></p>
                <p>If the button doesn't work, copy this link: {base_url}/auth/verify/{magic_token}</p>
                <p>This link expires in 30 minutes.</p>
                """
            )
            
            if success:
                flash('Login link sent! Check your email.', 'success')
            else:
                flash('Failed to send login link. Try again.', 'error')
                
        except Exception as e:
            logging.error(f"Login error: {e}")
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/auth/verify/<token>')
def verify_magic_link(token):
    """Verify magic link and login user"""
    try:
        email = auth_routes.auth_manager.verify_magic_link(token)
        
        if email:
            # Get user by email
            user = auth_routes.auth_manager.get_user_by_email(email)
            
            if user:
                # Login user
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                
                flash('Successfully logged in!', 'success')
                return redirect('/dashboard')
            else:
                flash('User account not found', 'error')
        else:
            flash('Invalid or expired login link', 'error')
            
    except Exception as e:
        logging.error(f"Magic link verification error: {e}")
        flash('Login failed. Please try again.', 'error')
    
    return redirect('/login')

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Successfully logged out', 'success')
    return redirect('/')

@auth_bp.route('/pricing')
def pricing():
    """Display pricing page"""
    tier_info = {
        'explorer': auth_routes.subscription_manager.get_tier_info('explorer'),
        'founder_plus': auth_routes.subscription_manager.get_tier_info('founder_plus')
    }
    return render_template('pricing.html', tiers=tier_info)

@auth_bp.route('/upgrade', methods=['POST'])
@login_required
def upgrade_subscription():
    """Handle subscription upgrade"""
    user_id = session.get('user_id')
    tier = request.form.get('tier')
    payment_method = request.form.get('payment_method', 'monthly')
    
    if tier not in ['founder_plus']:
        flash('Invalid subscription tier', 'error')
        return redirect('/pricing')
    
    try:
        # Create Stripe checkout session
        success_url = request.host_url.rstrip('/') + '/dashboard'
        cancel_url = request.host_url.rstrip('/') + '/pricing'
        
        checkout_session = auth_routes.stripe_manager.create_checkout_session(
            user_id=user_id,
            tier=tier,
            payment_method=payment_method,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        if checkout_session:
            return redirect(checkout_session.url)
        else:
            flash('Failed to create checkout session', 'error')
            
    except Exception as e:
        logging.error(f"Upgrade error: {e}")
        flash('An error occurred during upgrade', 'error')
    
    return redirect('/pricing')

@auth_bp.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    signature = request.headers.get('Stripe-Signature')
    
    try:
        success = auth_routes.stripe_manager.handle_webhook(payload, signature)
        
        if success:
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'error'}), 400
            
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({'status': 'error'}), 500

@auth_bp.route('/account')
@login_required
def account():
    """User account management"""
    user_id = session.get('user_id')
    user = auth_routes.subscription_manager.get_user_with_usage(user_id)
    usage_summary = auth_routes.subscription_manager.get_usage_summary(user_id)
    
    return render_template('account.html', 
                         user=user, 
                         usage=usage_summary)