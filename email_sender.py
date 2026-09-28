import os
from smtplib import SMTP, SMTPException

SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")


def send_email(receiver_email, code):
    if not SMTP_USER or not SMTP_PASS:
        return False
    
    message = f"Subject: To-Do App\n\nThis is the code to reset your password: {code}"
    try:
        with SMTP('smtp.gmail.com', 587) as connection:
            connection.starttls()
            connection.login(SMTP_USER, SMTP_PASS)
            connection.sendmail(SMTP_USER, 
                            receiver_email,
                            message)
        return True
    except (SMTPException, OSError):
        return False
