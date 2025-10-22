import requests

BASE_URL = "http://127.0.0.1:8000"

def login_user():
    print("=== Login ===")
    email = input("Enter your registered email: ").strip()

    try:
        response = requests.post(f"{BASE_URL}/users/login", json={"email": email})
        response.raise_for_status()

        user_data = response.json().get("user")
        if not user_data:
            print("Invalid server response.")
            return

        print(f"Welcome back, {user_data['first_name']} {user_data['last_name']}!")
        print(f"Your User ID: {user_data['user_id']}")
    except requests.exceptions.RequestException as e:
        print("Connection error:", e)
    except Exception as e:
        print("Unexpected error:", e)

if __name__ == "__main__":
    login_user()
