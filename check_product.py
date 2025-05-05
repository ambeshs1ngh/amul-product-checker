import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from twilio.rest import Client
import os
import smtplib
import json
import http.client

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

def send_email_sendgrid(time_str):
    api_key = os.getenv("SENDGRID_API_KEY")
    print("SENDGRID_API_KEY value:", api_key)
    if not api_key:
        print("Missing SendGrid API key.")
        return

    body = {
        "personalizations": [{
            "to": [{"email": "singhambesh153@gmail.com"}],
            "subject": "Amul Product Unavailable"
        }],
    "from": {"email": "singhambesh153@gmail.com"},
        "content": [{
            "type": "text/plain",
            "value": f"The Amul product is still not available as of {time_str} IST."
        }]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    conn = http.client.HTTPSConnection("api.sendgrid.com")
    try:
        conn.request("POST", "/v3/mail/send", body=json.dumps(body), headers=headers)
        response = conn.getresponse()
        print("SendGrid email response:", response.status, response.reason)
        if response.status == 202:
            print("Email sent successfully via SendGrid.")
        else:
            print("Failed to send email. Check SendGrid configuration.")
    except Exception as e:
        print("Exception while sending email:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    if is_valid_time():
        available = is_product_available()
        _, current_time = get_ist_time()
        if available:
            message = f"As of {current_time} IST, the Amul high protein milk is available online."
            make_call(message)
        else:
            send_email_sendgrid(current_time)
            print("Product is not available. Email sent via SendGrid.")
    else:
        print("Outside allowed calling hours.")
