#!/usr/bin/env python3
"""
Email notification system for trademark alerts
Supports SMTP, SendGrid, and other email providers
"""

import json
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

class EmailNotifier:
    """Send email notifications for trademark alerts"""
    
    def __init__(self, config_file="config/email_config.json"):
        self.config = self.load_config(config_file)
    
    def load_config(self, config_file):
        """Load email configuration"""
        if os.path.exists(config_file):
            with open(config_file) as f:
                return json.load(f)
        
        # Default configuration
        return {
            "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "sender_email": os.getenv("SENDER_EMAIL", "alerts@drgreenthumbtm.com"),
            "sender_password": os.getenv("SENDER_PASSWORD", ""),
            "recipients": {
                "legal_team": os.getenv("LEGAL_EMAIL", "legal@drgreenthumbtm.com").split(","),
                "b_real": os.getenv("BREAL_EMAIL", "breal@drgreenthumbtm.com"),
                "business_dev": os.getenv("BIZDEV_EMAIL", "bizdev@drgreenthumbtm.com")
            }
        }
    
    def send_renewal_alert(self, trademark, days_until, severity="warning"):
        """Send renewal alert email"""
        subject = f"{'🔴 URGENT' if days_until <= 30 else '🟡 REMINDER'}: Trademark Renewal - {trademark['name']}"
        
        body = f"""
        <html>
        <body>
            <h2>Trademark Renewal Alert</h2>
            
            <p><strong>Trademark:</strong> {trademark['name']}</p>
            <p><strong>Jurisdiction:</strong> {trademark['jurisdiction']}</p>
            <p><strong>Renewal Date:</strong> {trademark['renewal_date']}</p>
            <p><strong>Days Until Renewal:</strong> {days_until}</p>
            <p><strong>Registration #:</strong> {trademark.get('registration_number', 'N/A')}</p>
            
            <h3>Action Required:</h3>
            <ul>
                <li>Review renewal requirements</li>
                <li>Prepare filing documents</li>
                <li>Budget for renewal fees</li>
                <li>Submit to trademark office</li>
            </ul>
            
            <p><strong>Priority:</strong> {'HIGH' if days_until <= 30 else 'MEDIUM'}</p>
            
            <p>View in tracker: <a href="https://github.com/raphaelhaddock-blip/dr-greenthumb-trademark-tracker">GitHub</a></p>
            
            <hr>
            <p style="color: #666; font-size: 12px;">This is an automated alert from Dr. Greenthumb Trademark Tracker</p>
        </body>
        </html>
        """
        
        recipients = self.config["recipients"]["legal_team"] + [self.config["recipients"]["b_real"]]
        return self.send_email(recipients, subject, body)
    
    def send_overdue_alert(self, trademark, days_overdue):
        """Send critical overdue alert"""
        subject = f"🚨 CRITICAL: Overdue Trademark Renewal - {trademark['name']}"
        
        body = f"""
        <html>
        <body style="color: #c00;">
            <h2 style="color: #c00;">⚠️ CRITICAL: OVERDUE TRADEMARK RENEWAL</h2>
            
            <p><strong>Trademark:</strong> {trademark['name']}</p>
            <p><strong>Jurisdiction:</strong> {trademark['jurisdiction']}</p>
            <p><strong>Renewal Date:</strong> {trademark['renewal_date']}</p>
            <p><strong>DAYS OVERDUE:</strong> <span style="font-size: 24px; color: #c00;">{days_overdue}</span></p>
            
            <h3>IMMEDIATE ACTIONS REQUIRED:</h3>
            <ol>
                <li><strong>Contact trademark attorney NOW</strong></li>
                <li>File emergency renewal</li>
                <li>Document late filing reasons</li>
                <li>Calculate late fees</li>
                <li>Assess risk of abandonment</li>
            </ol>
            
            <p style="background: #fcc; padding: 10px; border: 2px solid #c00;">
                <strong>WARNING:</strong> This trademark may be at risk of abandonment. 
                Immediate legal action required to protect IP rights.
            </p>
            
            <p>View tracker: <a href="https://github.com/raphaelhaddock-blip/dr-greenthumb-trademark-tracker">GitHub</a></p>
        </body>
        </html>
        """
        
        # Send to everyone for critical alerts
        recipients = (
            self.config["recipients"]["legal_team"] + 
            [self.config["recipients"]["b_real"]] +
            [self.config["recipients"]["business_dev"]]
        )
        return self.send_email(recipients, subject, body, priority="high")
    
    def send_weekly_report(self, report_data):
        """Send weekly portfolio report"""
        subject = f"📊 Weekly Trademark Portfolio Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""
        <html>
        <body>
            <h2>Dr. Greenthumb Trademark Portfolio - Weekly Report</h2>
            
            <h3>Portfolio Overview</h3>
            <ul>
                <li>Total Active: {report_data['total_active']}</li>
                <li>Renewals Within 90 Days: {report_data['upcoming_90']}</li>
                <li>Renewals Within 30 Days: {report_data['upcoming_30']}</li>
                <li>Overdue: {report_data['overdue']}</li>
            </ul>
            
            <h3>Action Items</h3>
            {self._format_action_items(report_data['action_items'])}
            
            <h3>Pending Filings</h3>
            <ul>
                <li>Arizona: URGENT - $3,900</li>
                <li>Illinois: URGENT - $3,900</li>
            </ul>
            
            <p>Full report: <a href="https://github.com/raphaelhaddock-blip/dr-greenthumb-trademark-tracker/issues">View Issues</a></p>
            
            <hr>
            <p style="color: #666; font-size: 12px;">Automated weekly report from Dr. Greenthumb Trademark Tracker</p>
        </body>
        </html>
        """
        
        recipients = self.config["recipients"]["legal_team"] + [self.config["recipients"]["b_real"]]
        return self.send_email(recipients, subject, body)
    
    def _format_action_items(self, items):
        """Format action items as HTML"""
        if not items:
            return "<p>✅ No urgent action items</p>"
        
        html = "<ul>"
        for item in items:
            html += f"<li>{item}</li>"
        html += "</ul>"
        return html
    
    def send_email(self, recipients, subject, body, priority="normal"):
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config['sender_email']
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            
            if priority == "high":
                msg['X-Priority'] = '1'
                msg['Importance'] = 'high'
            
            msg.attach(MIMEText(body, 'html'))
            
            # Use environment variable for password in production
            password = self.config['sender_password'] or os.getenv('EMAIL_PASSWORD')
            
            if not password:
                print("⚠️  No email password configured. Email not sent.")
                print(f"Subject: {subject}")
                print(f"To: {recipients}")
                return False
            
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['sender_email'], password)
                server.send_message(msg)
            
            print(f"✅ Email sent: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

if __name__ == "__main__":
    # Test email notification
    notifier = EmailNotifier()
    
    test_trademark = {
        "name": "DR. GREENTHUMB",
        "jurisdiction": "Federal (USPTO)",
        "renewal_date": "2026-01-15",
        "registration_number": "5234567"
    }
    
    print("Testing email notification system...")
    notifier.send_renewal_alert(test_trademark, days_until=25)