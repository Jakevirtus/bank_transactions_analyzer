import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests

logger = logging.getLogger(__name__)


def get_greeting(current_time: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    hour = current_time.hour
    if 6 <= hour <= 11:
        return "Доброе утро"
    elif 12 <= hour <= 17:
        return "Добрый день"
    elif 18 <= hour <= 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Получает курсы валют к рублю.

    Использует открытый API (не требует ключа).
    """
    rates = []
    try:
        # Бесплатный API для курсов валют
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        response.raise_for_status()
        data = response.json().get("Valute", {})

        for currency in currencies:
            if currency in data:
                # В API ЦБ РФ курсы валют даны за определенное количество (например, 10 или 100)
                rate = float(data[currency]["Value"]) / float(data[currency]["Nominal"])
                rates.append({"currency": currency, "rate": round(rate, 2)})
            else:
                rates.append({"currency": currency, "rate": 1.0})
    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
        # Если API упало, отдаем заглушки, чтобы программа не падала
        for currency in currencies:
            rates.append({"currency": currency, "rate": 0.0})
    return rates


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """Получает цены на акции.

    Примечание: В реальном проекте тут должен быть запрос к API биржи
    (например, Alpha Vantage или Yahoo Finance). Для учебных целей
    мы используем заглушку, чтобы не требовать API-ключ.
    """
    prices = []
    for stock in stocks:
        # Генерируем фейковую цену на основе длины тикера
        price = float(100 + len(stock) * 10)
        prices.append({"stock": stock, "price": round(price, 2)})
    return prices


def main_page(date_time_str: str) -> str:
    """Генерирует JSON для главной страницы.

    Args:
        date_time_str: Строка с датой в формате 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        JSON-строка с данными для отображения.
    """
    # 1. Парсим дату
    dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    start_of_month = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 2. Читаем данные из Excel
    # Мы используем тот самый файл, который положили в папку data
    try:
        df = pd.read_excel("data/operations.xlsx")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    except FileNotFoundError:
        logger.error("Файл data/operations.xlsx не найден!")
        df = pd.DataFrame()

    # 3. Фильтруем с начала месяца по текущую дату
    if not df.empty:
        filtered_df = df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= dt)]
    else:
        filtered_df = pd.DataFrame()

    # 4. Топ-5 транзакций по сумме платежа
    transactions = []
    if not filtered_df.empty:
        top_5 = filtered_df.nlargest(5, "Сумма платежа")
        for _, row in top_5.iterrows():
            transactions.append({
                "date": row["Дата операции"].strftime("%d.%m.%Y"),
                "amount": float(abs(row["Сумма платежа"])),
                "category": str(row.get("Категория", "")),
                "description": str(row.get("Описание", ""))
            })

    # 5. Читаем настройки пользователя
    try:
        with open("user_settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
        user_currencies = settings.get("user_currencies", [])
        user_stocks = settings.get("user_stocks", [])
    except Exception as e:
        logger.error(f"Ошибка чтения user_settings.json: {e}")
        user_currencies = []
        user_stocks = []

    # 6. Собираем итоговый ответ
    result = {
        "greeting": get_greeting(dt),
        "cards": [
            {
                "last_digits": "4556",
                "total_spent": 15000.0,
                "cashback": 150.0
            }
        ],
        "top_transactions": transactions,
        "currency_rates": get_currency_rates(user_currencies),
        "stock_prices": get_stock_prices(user_stocks)
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
