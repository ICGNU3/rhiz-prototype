"""
Test route for Resend email functionality
Add this to routes.py to test email sending
"""
from flask import request, jsonify
import logging
from utils.email import email_service

def add_test_email_route(app):
    """Add test email route to Flask app"""
    
    @app.route('/test-email')
    def test_email():
        """Test route to send email via Resend"""
        to_email = request.args.get('to')
        
        if not to_email:
            return jsonify({
                'success': False,
                'error': 'Please provide "to" parameter: /test-email?to=you@example.com'
            }), 400
        
        # Test email content
        subject = "OuRhizome Email Test - Resend Integration"
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Email Test</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px;">
                <h1 style="color: #333; margin-bottom: 20px;">🌱 OuRhizome Email Test</h1>
                <p>This is a test email from OuRhizome using Resend.</p>
                <p><strong>✅ Resend integration is working correctly!</strong></p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 6px; margin: 20px 0;">
                    <h3>Test Details:</h3>
                    <ul>
                        <li>Email service: Resend</li>
                        <li>From: info@ourhizome.com</li>
                        <li>Status: Successfully delivered</li>
                    </ul>
                </div>
                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Sent from OuRhizome - Goal in mind. People in reach. Moves in motion.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = """
        OuRhizome Email Test - Resend Integration
        
        This is a test email from OuRhizome using Resend.
        
        ✅ Resend integration is working correctly!
        
        Test Details:
        - Email service: Resend
        - From: info@ourhizome.com
        - Status: Successfully delivered
        
        Sent from OuRhizome - Goal in mind. People in reach. Moves in motion.
        """
        
        try:
            # Send test email
            result = email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            # Log result
            if result['success']:
                logging.info(f"✅ Test email sent successfully to {to_email} via Resend")
                logging.info(f"Email ID: {result.get('email_id', 'unknown')}")
            else:
                logging.error(f"❌ Test email failed: {result.get('error', 'unknown error')}")
            
            return jsonify({
                'success': result['success'],
                'message': result.get('message', 'Email test completed'),
                'method': result.get('method', 'resend'),
                'email_id': result.get('email_id'),
                'to': to_email,
                'timestamp': str(logging.time.time())
            })
            
        except Exception as e:
            error_msg = f"Test email failed with exception: {str(e)}"
            logging.error(error_msg)
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'to': to_email
            }), 500