import requests
import json

# Adres mikroserwisu Clojure
url = "http://localhost:8080"

# Przykładowe dane symulujące czas akcji (np. 15 sekund od startu gry) oraz punkty
payload = {
    "actions": [15.5],
    "scores": [100]
}

try:
    response = requests.post(url, json=payload)
    print(f"Status HTTP: {response.status_code}")
    print("Odpowiedź z Clojure:")
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))
except Exception as e:
    print("Błąd połączenia z mikroserwisem:", e)