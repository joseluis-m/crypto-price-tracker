from __future__ import annotations

import csv
import datetime as dt
import hashlib
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests

API_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,ethereum&vs_currencies=usd"
)
STATE_SALT = "crypto-price-tracker-v1"
CSV_FILENAME = "prices.csv"
REQUEST_TIMEOUT_SECONDS = 20

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Configura el logging básico para el script."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def deterministic_rng_for_date(date_utc: dt.date) -> random.Random:
    """
    Devuelve un generador aleatorio determinista en función de la fecha UTC.

    Esto permite que el plan de horas sea reproducible cada día.
    """
    date_str = date_utc.isoformat()
    seed_int = int(
        hashlib.sha256(f"{STATE_SALT}-{date_str}".encode("utf-8")).hexdigest(),
        16,
    ) % (2**32)
    return random.Random(seed_int)


def today_plan(now_utc: dt.datetime) -> Tuple[int, List[int]]:
    """
    Calcula cuántas veces y en qué horas (UTC) debería ejecutarse hoy.

    Devuelve:
        runs: número de ejecuciones previstas para hoy (1–15).
        hours: lista ordenada de horas (0–23) en las que debe ejecutarse.
    """
    rng = deterministic_rng_for_date(now_utc.date())
    runs = rng.randint(1, 15)
    hours = sorted(rng.sample(range(24), runs))
    return runs, hours


def should_run_now(now_utc: dt.datetime, hours: List[int] | None = None) -> bool:
    """
    Indica si el script debería ejecutarse en la hora actual (UTC).

    Si no se pasan horas, recalcula el plan de hoy.
    """
    if hours is None:
        _, hours = today_plan(now_utc)
    return now_utc.hour in hours


PriceData = Dict[str, Dict[str, Any]]


def fetch_prices() -> PriceData:
    """
    Obtiene precios de Bitcoin y Ethereum en USD desde CoinGecko.

    En caso de error, devuelve un fallback con "N/A" para asegurar
    que se escribe una línea en el CSV.
    """
    try:
        response = requests.get(API_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Respuesta JSON inesperada")

        return data
    except (requests.RequestException, ValueError) as exc:
        # Fallback: garantizamos línea y commit en la hora planificada
        logger.warning(
            "CoinGecko no disponible: %s. Escribiendo N/A.",
            exc,
            exc_info=True,
        )
        return {"bitcoin": {"usd": "N/A"}, "ethereum": {"usd": "N/A"}}


def update_csv(data: PriceData, filename: str = CSV_FILENAME) -> None:
    """
    Actualiza el CSV con el timestamp UTC actual y los precios recibidos.
    Crea el fichero con cabecera si no existe.
    """
    now_utc = dt.datetime.now(dt.timezone.utc)
    timestamp = now_utc.strftime("%Y-%m-%d %H:%M:%S")

    btc_price = data.get("bitcoin", {}).get("usd", "N/A")
    eth_price = data.get("ethereum", {}).get("usd", "N/A")

    path = Path(filename)
    file_exists = path.is_file()

    with path.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Timestamp (UTC)", "Bitcoin (USD)", "Ethereum (USD)"])
        writer.writerow([timestamp, btc_price, eth_price])


def main(argv: List[str] | None = None) -> int:
    setup_logging()

    now_utc = dt.datetime.now(dt.timezone.utc)
    runs, hours = today_plan(now_utc)

    logger.info(
        "Plan hoy %s UTC -> %d vez/veces en horas: %s. Hora actual: %02d",
        now_utc.date().isoformat(),
        runs,
        hours,
        now_utc.hour,
    )

    if not should_run_now(now_utc, hours=hours):
        logger.info("Esta hora no está en el plan. Sin cambios.")
        return 0

    data = fetch_prices()
    update_csv(data)
    logger.info("CSV actualizado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
