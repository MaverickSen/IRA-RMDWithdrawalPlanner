import requests

BASE_URL = "http://127.0.0.1:8000"

def register_user():
    print("=== Register New User ===")
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()
    email = input("Enter email: ").strip()
    
    try:
        age = int(input("Enter age: ").strip())
    except ValueError:
        print("Invalid age. Please enter a number.")
        return

    payload = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "age": age
    }

    try:
        response = requests.post(f"{BASE_URL}/users/register", json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"Registration successful. Your User ID: {data.get('user_id', 'Unknown')}")
    except requests.exceptions.RequestException as e:
        print("Connection error:", e)
    except ValueError:
        print("Invalid response from server.")
    except Exception as e:
        print("Unexpected error:", e)

if __name__ == "__main__":
    register_user()
