# Crypto Price Tracker

[![Auto Commit Crypto Prices](https://github.com/joseluis-m/crypto-price-tracker/actions/workflows/auto_commit.yml/badge.svg)](https://github.com/joseluis-m/crypto-price-tracker/actions)

Seguimiento automatizado de los precios de **Bitcoin** y **Ethereum** con la API de CoinGecko. Un workflow de GitHub Actions se ejecuta **cada hora (UTC)** y el script selecciona de forma determinista, sin guardar estado, **entre 1 y 5 horas únicas al día** para registrar datos en `prices.csv`. Los commits solo se realizan cuando hay cambios.

## Características
- Automatización con GitHub Actions (cron horario en UTC).
- Registro aleatorio determinista **1–5 veces al día** por fecha UTC.
- CSV con columnas: `Timestamp (UTC)`, `Bitcoin (USD)`, `Ethereum (USD)`.
- Commit y push condicionados a la existencia de cambios.
- Código simple en Python 3.x con `requests`.

## Cómo funciona
1. **Plan diario determinista:** para cada fecha UTC se genera una semilla y se eligen de 1 a 5 horas únicas del día.
2. **Ejecución horaria:** el workflow invoca el script; este solo escribe si la hora actual está en el plan.
3. **Obtención de precios:** consulta a CoinGecko con control básico de errores y `timeout`.
4. **Persistencia:** crea `prices.csv` con cabecera si no existe y añade una fila por ejecución válida.
5. **Commit/push:** el workflow añade y comitea únicamente si el CSV cambió.

## Estructura
- `update_prices.py`
- `prices.csv` (generado/actualizado por el workflow)
- `.github/workflows/auto_commit.yml` (cron: `0 * * * *`)

## Ejecución local (opcional)
- Requisitos: Python 3.x y `requests`.
- Pasos:
  1. Clonar el repositorio: `git clone https://github.com/joseluis-m/crypto-price-tracker.git` y `cd crypto-price-tracker`.
  2. Instalar dependencias: `python -m pip install --upgrade pip && pip install requests`.
  3. Ejecutar: `python update_prices.py` (si la hora UTC no está en el plan del día, no habrá cambios).

## Notas
- Se usa **UTC** para coherencia con el cron y la trazabilidad.
- La selección diaria de horas cambia cada día y permanece estable dentro del mismo día.
- El workflow define `permissions: contents: write` para poder hacer push en ejecuciones programadas.
- CoinGecko puede aplicar límites de uso; el proyecto realiza un volumen muy bajo de consultas.
