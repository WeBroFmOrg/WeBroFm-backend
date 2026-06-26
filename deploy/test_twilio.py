from twilio.rest import Client

sid = "ACa02c5bee507406b6787bef89c38e9020"
token = "dafd5076730ecf175af2bb4b1d2cf4cf"

try:
    c = Client(sid, token)
    # Check account
    account = c.api.account.fetch()
    print("Status:", account.status)
    print("Type:", account.type)
    print("Name:", account.friendly_name)
    
    # Send test SMS
    msg = c.messages.create(
        body="WeBro FM test - OTP 123456",
        from_="+12293213556",
        to="+919999999999"
    )
    print("SMS sent:", msg.sid)
    print("Status:", msg.status)
except Exception as e:
    print("ERROR:", str(e)[:500])
