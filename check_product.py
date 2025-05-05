import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from twilio.rest import Client
import os

def is_product_available():
    url = "https://shop.amul.com/en/product/amul-high-protein-milk-250-ml-or-pack-of-32"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the Add to Cart button
    button = soup.find("button", class_="product-add-to-cart")

    if button:
        button_text = button.text.strip().lower()
        is_disabled = button.has_attr("disabled") or "disabled" in button.get("class", [])
        
        print("Button text:", button_text)
        print("Button disabled:", is_disabled)

        if "add to cart" in button_text and not is_disabled:
            return True
        else:
            return False

    # No button found → assume not available
    print("No 'Add to Cart' button found.")
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

if __name__ == "__main__":
    if is_valid_time():
        available = is_product_available()
        if available:
            _, current_time = get_ist_time()
            message = f"As of {current_time} IST, the Amul high protein milk is available online."
            make_call(message)
        else:
            print("Product is sold out.")
    else:
        print("Outside allowed calling hours.")
