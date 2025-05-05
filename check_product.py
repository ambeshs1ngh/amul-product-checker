import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from twilio.rest import Client
import os

def is_product_available():
    url = "https://shop.amul.com/en/product/amul-kool-protein-milkshake-or-arabica-coffee-180-ml-or-pack-of-30"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return "Out of stock" not in soup.text.lower()

def get_ist_time():
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    return ist_now.time(), ist_now.strftime("%I:%M %p")

def is_valid_time():
    now, _ = get_ist_time()
    return not (now >= datetime.strptime("22:00", "%H:%M").time() or now <= datetime.strptime("09:00", "%H:%M").time())

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

if __name__ == "__main__":
    if is_valid_time():
        available = is_product_available()
        _, current_time = get_ist_time()
        status = "available" if available else "not available"
        message = f"As of {current_time} IST, the Amul product is {status}."
        make_call(message)
    else:
        print("Outside allowed calling hours.")
