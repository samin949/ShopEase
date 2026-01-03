import requests
import json

data = {
    "username": "admin",
    "email": "admin@shopease.com",
    "password": "admin123"
}

response = requests.post(
    "http://localhost:5000/api/create-admin",
    json=data,
    headers={"Content-Type": "application/json"}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")