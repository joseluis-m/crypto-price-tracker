# Crypto Price Tracker

[![Auto Commit Crypto Prices](https://github.com/joseluis-m/crypto-price-tracker/actions/workflows/auto_commit.yml/badge.svg)](https://github.com/joseluis-m/crypto-price-tracker/actions)

Seguimiento automatizado de los precios de **Bitcoin** y **Ethereum** usando la API de CoinGecko.  
Un workflow de GitHub Actions se ejecuta **cada hora (UTC)** y el script decide, de forma determinista y sin guardar estado, **entre 1 y 15 horas únicas al día** en las que registrar datos en `prices.csv`.  
Los commits solo se realizan cuando el archivo cambia, lo que lo hace ideal para consumirlo desde **GitHub Pages** como fuente de datos estática.

## Características

- Automatización con GitHub Actions (cron horario en UTC).
- Registro aleatorio determinista 1–15 veces al día por fecha UTC.
- Archivo CSV con columnas: `Timestamp (UTC)`, `Bitcoin (USD)`, `Ethereum (USD)`.
- Commit y push condicionados a la existencia de cambios.
- Script sencillo en Python 3 (probado en 3.12) con `requests`.

## Cómo funciona

1. **Plan diario determinista**  
   Para cada fecha UTC se calcula una semilla y se elige un conjunto de horas únicas (1–15). El mismo día siempre produce el mismo plan.

2. **Ejecución horaria**  
   El workflow se ejecuta cada hora. El script solo escribe al CSV cuando la hora UTC actual está en el plan del día.

3. **Obtención de precios**  
   Se consulta la API de CoinGecko con `timeout` y manejo básico de errores. Si la API no responde, se escribe `N/A` para mantener la serie temporal.

4. **Persistencia y versionado**  
   Si no existe, se crea `prices.csv` con cabecera; en cada ejecución válida se añade una fila y, si hay cambios, se realiza commit y push al repositorio (lo que a su vez dispara la build de GitHub Pages si está configurado).

## Estructura del repositorio

- `update_prices.py` — script que decide si registrar y escribe el CSV.
- `prices.csv` — serie histórica generada/actualizada por el workflow.
- `.github/workflows/auto_commit.yml` — workflow con cron `0 * * * *`.

## Ejecución local (opcional)

Requisitos: Python 3 y el paquete `requests`.

Pasos básicos:

1. Clonar el repositorio:  
   `git clone https://github.com/joseluis-m/crypto-price-tracker.git`  
   `cd crypto-price-tracker`
2. Instalar dependencias:  
   `python -m pip install --upgrade pip`  
   `pip install requests`
3. Ejecutar el script:  
   `python update_prices.py`  

Si la hora UTC actual no está en el plan del día, no se modificará `prices.csv` y no habrá cambios para commitear.
