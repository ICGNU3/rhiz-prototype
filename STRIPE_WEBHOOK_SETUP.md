# Stripe Webhook Setup Guide

## Step 1: Get Your Stripe Secret Key

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to **Developers** → **API keys**
3. Copy your **Secret key** (starts with `sk_test_` for test mode or `sk_live_` for live mode)
4. Add this to Replit Secrets as `STRIPE_SECRET_KEY`

## Step 2: Create Webhook Endpoint

1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Enter your webhook URL: `https://your-replit-app.replit.app/stripe/webhook`
   - Replace `your-replit-app` with your actual Replit app name
   - If you don't have a deployed URL yet, you can add this after deployment
4. Select these events to listen for:
   - `customer.subscription.created`
   - `customer.subscription.updated` 
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click **Add endpoint**

## Step 3: Get Webhook Secret

1. After creating the webhook, click on it in your webhooks list
2. In the **Signing secret** section, click **Reveal**
3. Copy the webhook secret (starts with `whsec_`)
4. Add this to Replit Secrets as `STRIPE_WEBHOOK_SECRET`

## Step 4: Test Your Setup

After adding both secrets, your health check at `/health` should show:
```json
{
  "checks": {
    "stripe": "configured"
  }
}
```

## Your Webhook Endpoint

Your app expects webhooks at: `/stripe/webhook`

This endpoint will:
- Verify webhook signatures for security
- Handle subscription events (created, updated, cancelled)
- Update user subscription status in your database
- Process payment confirmations

## Next Steps

1. Add both Stripe secrets to Replit
2. Deploy your app to get the webhook URL
3. Update the webhook endpoint URL in Stripe with your deployed URL
4. Test a subscription to ensure everything works

## Test Mode vs Live Mode

- Use `sk_test_` keys for testing
- Use `sk_live_` keys for production
- Make sure webhook and secret key are from the same mode