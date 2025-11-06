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
    """
    Genera un RNG determinista (reproducible) para 'date_utc_str' (YYYY-MM-DD).
    Así las horas elegidas se mantienen estables durante ese día.
    """
    seed_int = int(
        hashlib.sha256(f"{STATE_SALT}-{date_utc_str}".encode("utf-8")).hexdigest(),
        16
    ) % (2**32)
    return random.Random(seed_int)

def today_plan(now_utc: datetime.datetime):
    """
    Devuelve (runs_per_day, sorted_hours_list) para hoy (UTC).
    runs_per_day es un entero en [1, 5].
    sorted_hours_list son horas enteras (0..23) en las que se debe ejecutar.
    """
    date_key = now_utc.strftime("%Y-%m-%d")
    rng = deterministic_rng_for_date(date_key)
    runs = rng.randint(1, 5)           # 1..5 ejecuciones diarias
    hours = sorted(rng.sample(range(24), runs))  # horas únicas del día
    return runs, hours

def should_run_now(now_utc: datetime.datetime) -> bool:
    """
    Devuelve True si la hora UTC actual está en el plan de hoy.
    """
    _, hours = today_plan(now_utc)
    return now_utc.hour in hours

def fetch_prices():
    try:
        response = requests.get(API_URL, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Fallo al consultar CoinGecko: {e}", file=sys.stderr)
        sys.exit(1)

def update_csv(data, filename="prices.csv"):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    btc_price = data.get("bitcoin", {}).get("usd", "N/A")
    eth_price = data.get("ethereum", {}).get("usd", "N/A")
    new_row = [now, btc_price, eth_price]

    file_exists = os.path.isfile(filename)
    # Abrimos en append; creamos cabecera si no existe
    with open(filename, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Timestamp (UTC)", "Bitcoin (USD)", "Ethereum (USD)"])
        writer.writerow(new_row)

def main():
    now_utc = datetime.datetime.utcnow()
    runs, hours = today_plan(now_utc)

    # Log informativo (se verá en Actions)
    print(f"[INFO] Hoy (UTC {now_utc.strftime('%Y-%m-%d')}) se ejecutará {runs} vez/veces en las horas UTC: {hours}. Hora actual UTC: {now_utc.hour:02d}:00")

    if not should_run_now(now_utc):
        print("[INFO] Esta hora no está en el plan de hoy. No se actualiza el CSV.")
        # Salimos con 0 para que el job no falle; y como no hay cambios, no habrá commit.
        return

    data = fetch_prices()
    update_csv(data)
    print("[OK] Archivo actualizado con precios de Bitcoin y Ethereum.")

if __name__ == "__main__":
    main()
