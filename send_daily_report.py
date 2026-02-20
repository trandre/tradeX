import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import datetime

def send_email_report(recipient_email, attachment_path):
    # Retrieve credentials from environment variables (Safety First!)
    sender_email = os.getenv("TRADEX_EMAIL_USER") 
    sender_password = os.getenv("TRADEX_EMAIL_PASS")
    
    if not sender_email or not sender_password:
        print("Error: EMAIL_USER or EMAIL_PASS environment variables not set.")
        print(f"REPORT SAVED LOCALLY: {attachment_path}")
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"TradeX Daily Performance Report - {datetime.date.today().isoformat()}"

    body = (
        "Attached is the daily TradeX performance report.\n\n"
        "The report contains:\n"
        "1. Portfolio charts and allocation.\n"
        "2. Active positions, trade history, and market performance.\n"
        "3. AI-driven analysis of successes, failures, and news impacts."
    )
    
    msg.attach(MIMEText(body, 'plain'))

    # Attachment
    try:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
            msg.attach(part)
    except Exception as e:
        print(f"Error attaching file: {e}")
        return False

    # Send Email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587) 
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.close()
        print(f"Successfully sent report to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
