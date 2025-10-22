import requests

BASE_URL = "http://127.0.0.1:8000"


def chat_loop(user_id: int):
    print("\nPortfolio Chat started. Type 'exit' to quit.\n")

    while True:
        msg = input("You: ").strip()
        if msg.lower() in ["exit", "quit"]:
            print("Ending chat session.")
            break

        if not msg:
            print("(Please enter a message or type 'exit' to quit.)")
            continue

        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"user_id": user_id, "message": msg},
                timeout=15,
            )

            if response.status_code == 200:
                data = response.json()
                print("\nAssistant:", data.get("response", "[No response]"))
                if "context_used" in data:
                    print(f"(Context used: {data['context_used']} messages)\n")

            elif response.status_code == 404:
                detail = response.json().get("detail", "Not found.")
                print(f"[Error 404] {detail}")

                if "User not found" in detail:
                    print("→ Please register a user first using the registration script.")
                elif "No portfolio found" in detail:
                    print("→ Please upload your portfolio before chatting.")
                break

            else:
                print(f"[Error {response.status_code}] {response.text}")

        except requests.exceptions.ConnectionError:
            print("Could not connect to the API server. Is FastAPI running?")
            break
        except requests.exceptions.Timeout:
            print("Request timed out. Try again.")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    try:
        user_id = int(input("Enter your user_id: "))
        chat_loop(user_id)
    except ValueError:
        print("Invalid user_id. Please enter a numeric ID.")
