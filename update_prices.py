import requests
import datetime
import csv
import os

def fetch_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data

def update_csv(data, filename="prices.csv"):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    btc_price = data.get("bitcoin", {}).get("usd", "N/A")
    eth_price = data.get("ethereum", {}).get("usd", "N/A")
    new_row = [now, btc_price, eth_price]
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Si el archivo no existe, escribe la cabecera
        if not file_exists:
            writer.writerow(["Timestamp (UTC)", "Bitcoin (USD)", "Ethereum (USD)"])
        writer.writerow(new_row)

def main():
    data = fetch_prices()
    update_csv(data)
    print("Archivo actualizado con precios de Bitcoin y Ethereum.")

if __name__ == "__main__":
    main()
