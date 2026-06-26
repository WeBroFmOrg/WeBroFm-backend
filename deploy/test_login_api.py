import requests, json
r = requests.post(
    "https://api.webrofm.in/api/admin/login/",
    json={"phone_number": "8888888888", "password": "Admin@12345"}
)
print("Status:", r.status_code)
print("Response:", json.dumps(r.json(), indent=2)[:300])
