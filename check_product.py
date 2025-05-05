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
    return ist_now.time()

def is_valid_time():
    now = get_ist_time()
    return not (now >= datetime.strptime("22:00", "%H:%M").time() or now <= datetime.strptime("09:00", "%H:%M").time())

def make_call():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        twiml='<Response><Say>The Amul product is now available online. Check it now!</Say></Response>',
        to=os.getenv("MY_PHONE_NUMBER"),
        from_=os.getenv("TWILIO_PHONE_NUMBER")
    )
    print("Call placed:", call.sid)

if __name__ == "__main__":
    if is_valid_time() and is_product_available():
        make_call()
    else:
        print("Not available or wrong time.")

