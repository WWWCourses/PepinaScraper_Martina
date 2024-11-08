import requests
import os

url = "https://pepina.bg/products/jeni/obuvki"
filename = "pepina.html"

headers = {"User-Agent": "Mozilla/5.0"}


def fetch_html(url):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            print("Зареждане на съдържание от локалния файл")
            return f.read()
    else:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response.text)
                print(f"Съдържанието е записано в: {filename}")
                return response.text
        except requests.exceptions.RequestException as e:
            print(f"Грешка при заявка: {e}")
            return None

