#!/usr/bin/env python3
"""
Test Microsoft Exchange SMTP configuration.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_microsoft_smtp():
    """Test different Microsoft SMTP configurations."""
    
    print("🧪 Testing Microsoft Exchange SMTP Configuration")
    print("=" * 50)
    
    # Configuration to test
    smtp_server = "smtp.office365.com"
    from_email = "abparts_support@oraseas.com"
    to_email = "abparts_support@oraseas.com"  # Send to self for testing
    
    # Get password from user
    import getpass
    password = getpass.getpass(f"Enter password for {from_email}: ")
    
    configurations = [
        {"port": 587, "use_tls": True, "use_ssl": False, "name": "TLS on port 587"},
        {"port": 25, "use_tls": True, "use_ssl": False, "name": "TLS on port 25"},
        {"port": 465, "use_tls": False, "use_ssl": True, "name": "SSL on port 465"},
    ]
    
    for config in configurations:
        print(f"\n🔧 Testing: {config['name']}")
        print("-" * 30)
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = "ABParts SMTP Test - " + config['name']
            
            body = f"""
This is a test email from ABParts AI Assistant.

Configuration tested: {config['name']}
Server: {smtp_server}
Port: {config['port']}
TLS: {config['use_tls']}
SSL: {config['use_ssl']}

If you receive this email, the SMTP configuration is working correctly!
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to server
            if config['use_ssl']:
                server = smtplib.SMTP_SSL(smtp_server, config['port'])
            else:
                server = smtplib.SMTP(smtp_server, config['port'])
                if config['use_tls']:
                    server.starttls()
            
            # Login and send
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ SUCCESS: {config['name']} works!")
            print(f"   Use these settings in your .env file:")
            print(f"   SMTP_SERVER={smtp_server}")
            print(f"   SMTP_PORT={config['port']}")
            print(f"   SMTP_USE_TLS={'true' if config['use_tls'] else 'false'}")
            print(f"   SMTP_USE_SSL={'true' if config['use_ssl'] else 'false'}")
            
            return config
            
        except Exception as e:
            print(f"❌ FAILED: {config['name']}")
            print(f"   Error: {str(e)}")
            
            # Check for specific error types
            if "authentication" in str(e).lower():
                print("   💡 This might be an authentication issue.")
                print("   💡 Try enabling SMTP AUTH or using an app password.")
            elif "connection" in str(e).lower():
                print("   💡 This might be a network/firewall issue.")
            elif "ssl" in str(e).lower() or "tls" in str(e).lower():
                print("   💡 This might be an SSL/TLS configuration issue.")
    
    print("\n❌ None of the configurations worked.")
    print("\n📋 Next steps:")
    print("1. Verify the email account exists and is active")
    print("2. Check if SMTP AUTH is enabled in Microsoft 365 Admin Center")
    print("3. Try generating an app password if MFA is enabled")
    print("4. Contact your Microsoft 365 administrator")
    
    return None

if __name__ == "__main__":
    test_microsoft_smtp()