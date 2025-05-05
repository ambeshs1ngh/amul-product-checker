import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from twilio.rest import Client
import os
import smtplib
from email.mime.text import MIMEText

def is_product_available():
    url = "https://shop.amul.com/en/product/amul-high-protein-milk-250-ml-or-pack-of-32"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    button = soup.find("button", class_="product-add-to-cart")

    if button:
        button_text = button.text.strip().lower()
        is_disabled = button.has_attr("disabled") or "disabled" in button.get("class", [])
        if "add to cart" in button_text and not is_disabled:
            return True
        else:
            return False

    return False

def get_ist_time():
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    return ist_now.time(), ist_now.strftime("%I:%M %p")

def is_valid_time():
    now, _ = get_ist_time()
    return datetime.strptime("09:00", "%H:%M").time() <= now <= datetime.strptime("23:00", "%H:%M").time()

def make_call(message):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        twiml=f'<Response><Say>{message}</Say></Response>',
        to=os.getenv("MY_PHONE_NUMBER"),
        from_=os.getenv("TWILIO_PHONE_NUMBER")
    )
    print("Call placed:", call.sid)

def send_email_notification_mailgun(time_str):
    smtp_login = os.getenv("MAILGUN_SMTP_LOGIN")
    smtp_password = os.getenv("MAILGUN_SMTP_PASSWORD")
    smtp_server = os.getenv("MAILGUN_SMTP_SERVER", "smtp.mailgun.org")
    to_email = "singhambesh153@gmail.com"

    subject = "Amul Product Unavailable"
    body = f"The Amul product is still not available as of {time_str} IST."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_login
    msg["To"] = to_email

    if not smtp_login or not smtp_password:
        print("Missing Mailgun credentials. Check GitHub secrets.")
        return

    try:
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.login(smtp_login, smtp_password)
        server.sendmail(smtp_login, to_email, msg.as_string())
        server.quit()
        print("Email sent via Mailgun.")
    except Exception as e:
        print("Failed to send email via Mailgun:", e)

if __name__ == "__main__":
    if is_valid_time():
        available = is_product_available()
        _, current_time = get_ist_time()
        if available:
            message = f"As of {current_time} IST, the Amul high protein milk is available online."
            make_call(message)
        else:
            send_email_notification_mailgun(current_time)
            print("Product is not available. Email sent.")
    else:
        print("Outside allowed calling hours.")
