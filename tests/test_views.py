from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd

from src.views import get_currency_rates, get_greeting, main_page


def test_get_greeting():
    assert get_greeting(datetime(2024, 5, 20, 8, 0)) == "Доброе утро"
    assert get_greeting(datetime(2024, 5, 20, 14, 0)) == "Добрый день"
    assert get_greeting(datetime(2024, 5, 20, 20, 0)) == "Добрый вечер"
    assert get_greeting(datetime(2024, 5, 20, 2, 0)) == "Доброй ночи"


@patch("src.views.requests.get")
def test_get_currency_rates(mock_get):
    # Мокаем ответ от ЦБ РФ
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Valute": {
            "USD": {"Value": 90.0, "Nominal": 1},
            "EUR": {"Value": 100.0, "Nominal": 1}
        }
    }
    mock_get.return_value = mock_response

    rates = get_currency_rates(["USD", "EUR"])
    assert rates[0]["currency"] == "USD"
    assert rates[0]["rate"] == 90.0
    assert rates[1]["rate"] == 100.0


@patch("src.views.pd.read_excel")
@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"user_currencies": ["USD"], "user_stocks": []}',
)
def test_main_page(mock_file, mock_curr, mock_stocks, mock_excel):
    # Подменяем Excel и функции (убрали слово "Мокаем")
    mock_excel.return_value = pd.DataFrame({
        "Дата операции": pd.to_datetime(["2024-05-10"]),
        "Сумма платежа": [-500.0],
        "Категория": ["Супермаркеты"],
        "Описание": ["Магнит"]
    })
    mock_curr.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_stocks.return_value = []

    result = main_page("2024-05-20 12:00:00")

    assert "Добрый день" in result
    assert "Магнит" in result
    assert "90.0" in result

    # А вот и использование mock_file (проверяем, что файл пытались открыть)
    mock_file.assert_called_once()

    # Мокаем Excel и функции
    mock_excel.return_value = pd.DataFrame({
        "Дата операции": pd.to_datetime(["2024-05-10"]),
        "Сумма платежа": [-500.0],
        "Категория": ["Супермаркеты"],
        "Описание": ["Магнит"]
    })
    mock_curr.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_stocks.return_value = []

    result = main_page("2024-05-20 12:00:00")

    assert "Добрый день" in result
    assert "Магнит" in result
    assert "90.0" in result

    # Мокаем Excel и функции
    mock_excel.return_value = pd.DataFrame({
        "Дата операции": pd.to_datetime(["2024-05-10"]),
        "Сумма платежа": [-500.0],
        "Категория": ["Супермаркеты"],
        "Описание": ["Магнит"]
    })
    mock_curr.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_stocks.return_value = []

    result = main_page("2024-05-20 12:00:00")

    assert "Добрый день" in result
    assert "Магнит" in result
    assert "90.0" in result
