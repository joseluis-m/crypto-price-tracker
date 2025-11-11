import requests
import datetime
import csv
import os
import random
import hashlib
import sys

API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
STATE_SALT = "crypto-price-tracker-v1"  # cambia si quieres otra distribución

def deterministic_rng_for_date(date_utc_str: str) -> random.Random:
    seed_int = int(
        hashlib.sha256(f"{STATE_SALT}-{date_utc_str}".encode("utf-8")).hexdigest(),
        16
    ) % (2**32)
    return random.Random(seed_int)

def today_plan(now_utc: datetime.datetime):
    date_key = now_utc.strftime("%Y-%m-%d")
    rng = deterministic_rng_for_date(date_key)
    runs = rng.randint(1, 5)                 # 1..5 ejecuciones diarias
    hours = sorted(rng.sample(range(24), runs))
    return runs, hours

def should_run_now(now_utc: datetime.datetime) -> bool:
    _, hours = today_plan(now_utc)
    return now_utc.hour in hours

def fetch_prices():
    try:
        r = requests.get(API_URL, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        # Fallback: garantizamos línea y commit en la hora planificada
        print(f"[WARN] CoinGecko no disponible: {e}. Escribiendo N/A.", file=sys.stderr)
        return {"bitcoin": {"usd": "N/A"}, "ethereum": {"usd": "N/A"}}

def update_csv(data, filename="prices.csv"):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    btc_price = data.get("bitcoin", {}).get("usd", "N/A")
    eth_price = data.get("ethereum", {}).get("usd", "N/A")
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Timestamp (UTC)", "Bitcoin (USD)", "Ethereum (USD)"])
        writer.writerow([now, btc_price, eth_price])

def main():
    now_utc = datetime.datetime.utcnow()
    runs, hours = today_plan(now_utc)
    print(f"[INFO] Plan hoy {now_utc.strftime('%Y-%m-%d')} UTC -> {runs} vez/veces en horas: {hours}. Hora actual: {now_utc.hour:02d}")

    if not should_run_now(now_utc):
        print("[INFO] Esta hora no está en el plan. Sin cambios.")
        return

    data = fetch_prices()
    update_csv(data)
    print("[OK] CSV actualizado.")

if __name__ == "__main__":
    main()
