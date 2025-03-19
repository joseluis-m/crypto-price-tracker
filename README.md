# Crypto Price Tracker

[![Auto Commit Crypto Prices](https://github.com/joseluis-m/crypto-price-tracker/actions/workflows/auto_commit.yml/badge.svg)](https://github.com/joseluis-m/crypto-price-tracker/actions)

Este repositorio realiza un seguimiento automático de los precios de **Bitcoin** y **Ethereum** utilizando la [API de CoinGecko](https://www.coingecko.com/en/api). Cada día, un workflow de GitHub Actions ejecuta un script en Python que:

1. **Obtiene** los precios actuales de Bitcoin y Ethereum en USD.  
2. **Registra** los precios en un archivo CSV (`prices.csv`) junto con la fecha y hora en formato UTC.  
3. **Realiza un commit** automático con los nuevos datos.

## ✨ Características principales

- **Automatización completa** gracias a [GitHub Actions](https://docs.github.com/en/actions).
- **Registro continuo** de precios de criptomonedas en `prices.csv`.
- **Fácil de clonar y ejecutar localmente** para tus propios experimentos.
- **Contribuciones** (commits) se generan sin intervención manual.

## 🚀 Cómo funciona

1. **Workflow programado:**  
   - El archivo [`auto_commit.yml`](.github/workflows/auto_commit.yml) define un trabajo que se ejecuta cada hora (según la línea `cron: "0 * * * *"`).  
   - Este workflow clona el repositorio, instala las dependencias y ejecuta el script `update_prices.py`.

2. **Script de actualización (`update_prices.py`):**  
   - Utiliza `requests` para llamar a la API de CoinGecko y obtener precios en USD de Bitcoin y Ethereum.  
   - Si el archivo `prices.csv` no existe, lo crea con una cabecera.  
   - Añade una fila nueva con la fecha/hora actual y los precios.

3. **Commit automático:**  
   - Tras ejecutar el script, el workflow hace `git add prices.csv` y un commit con la hora actual.  
   - Luego hace `git push` al repositorio, generando así actividad (contribuciones) en GitHub.

## 🛠️ Uso local (opcional)

Si quieres ejecutar el script en tu propia máquina:

1. **Clona el repositorio**  
   ```bash
   git clone https://github.com/joseluis-m/crypto-price-tracker.git
   cd crypto-price-tracker
