import requests
import json

# Adres endpointu naszego mikroserwisu Clojure
url = "http://localhost:8080"

# Przykładowe dane gracza wysyłane do przeliczenia
# - actions: czasy poszczególnych akcji/ruchów w sekundach
# - scores: punkty bazowe za poszczególne zagadki
payload = {
    "actions": [15, 25, 45, 12],
    "scores": [100, 100, 100, 100]
}

try:
    # Wysyłamy żądanie POST z nagłówkiem JSON
    response = requests.post(url, json=payload)
    
    print(f"Status HTTP: {response.status_code}")
    print("Odpowiedź z mikroserwisu Clojure:")
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))

except requests.exceptions.ConnectionError:
    print("Błąd: Nie można połączyć się z mikroserwisem Clojure. Upewnij się, że 'lein run' działa w terminalu!")