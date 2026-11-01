from src.services import cashback_categories, investment_bank, simple_search


def test_investment_bank():
    transactions = [
        {"Дата операции": "2024-05-10", "Сумма операции": -1712},
        {"Дата операции": "2024-05-11", "Сумма операции": -400},
        {"Дата операции": "2024-06-10", "Сумма операции": -500},  # Другой месяц
    ]

    # Округление до 50. 1712 -> 1750 (38 руб). 400 -> 400 (0 руб). Итого 38.
    result = investment_bank("2024-05", transactions, 50)
    assert result == 38.0


def test_simple_search():
    transactions = [
        {"Описание": "Покупка в Магнит", "Категория": "Супермаркеты"},
        {"Описание": "Оплата такси", "Категория": "Транспорт"},
    ]
    # Ищем без учета регистра
    result = simple_search(transactions, "магнит")
    assert "Пятерочка" not in result
    assert "Магнит" in result
    assert "такси" not in result


def test_cashback_categories():
    transactions = [
        {"Дата операции": "2024-05-10", "Категория": "Супермаркеты", "Кешбэк": 100},
        {"Дата операции": "2024-05-11", "Категория": "Супермаркеты", "Кешбэк": 50},
        {"Дата операции": "2024-05-12", "Категория": "Транспорт", "Кешбэк": 200},
    ]
    result_json = cashback_categories(transactions, 2024, 5)
    assert "Супермаркеты" in result_json
    assert "150" in result_json
    assert "200" in result_json
