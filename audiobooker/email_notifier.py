
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_notification_email(recipient_email, audiobook_name, download_url):
    """
    Sends an email notification when an audiobook is ready.
    Requires SMTP environment variables.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL", smtp_user)

    if not all([smtp_user, smtp_pass, recipient_email]):
        print("Warning: Skipping email notification. SMTP_USER, SMTP_PASSWORD, or recipient_email not configured.")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"Audiobooker AI <{sender_email}>"
    msg['To'] = recipient_email
    msg['Subject'] = f"Success! Your audiobook '{audiobook_name}' is ready"

    body = f"""
    Hello,

    Your audiobook '{audiobook_name}' has been successfully generated and is ready for listening!

    You can listen to it or download it here:
    {download_url}

    Enjoy,
    The Audiobooker Team
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"Notification email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
