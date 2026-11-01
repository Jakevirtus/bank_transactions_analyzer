import json
import logging

from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def cashback_categories(data: List[Dict[str, Any]], year: int, month: int) -> str:
    """Анализирует выгодность категорий повышенного кешбэка.

    Args:
        data: Список транзакций.
        year: Год.
        month: Месяц.

    Returns:
        JSON с суммами кешбэка по категориям.
    """
    cashback_dict: dict[str, float] = {}
    for t in data:
        # Проверяем, что дата операции совпадает с нужным годом и месяцем
        # Формат даты в транзакциях: 'YYYY-MM-DD' (строка)
        date_str = str(t.get("Дата операции", ""))
        if date_str.startswith(f"{year}-{month:02d}"):
            category = t.get("Категория", "Остальное")
            # Берем кешбэк из колонки "Бонусы (включая кешбэк)" или "Кешбэк"
            cashback = float(t.get("Кешбэк", 0) or 0)
            if cashback > 0:
                cashback_dict[category] = cashback_dict.get(category, 0) + cashback

    # Сортируем по убыванию кешбэка
    sorted_cashback = dict(sorted(cashback_dict.items(), key=lambda x: x[1], reverse=True))
    return json.dumps(sorted_cashback, ensure_ascii=False, indent=2)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Считает сумму, которую удалось бы отложить в Инвесткопилку.

    Args:
        month: Месяц в формате 'YYYY-MM'.
        transactions: Список транзакций.
        limit: Шаг округления (10, 50, 100).

    Returns:
        Сумма, отложенная в копилку.
    """
    total_saved = 0.0
    for t in transactions:
        date_str = str(t.get("Дата операции", ""))
        if date_str.startswith(month):
            amount = float(t.get("Сумма операции", 0))
            # Округляем только траты (отрицательные суммы)
            if amount < 0:
                abs_amount = abs(amount)
                # Математика округления вверх до кратного limit
                rounded = ((abs_amount + limit - 1) // limit) * limit
                total_saved += (rounded - abs_amount)

    logger.info(f"Инвесткопилка за {month}: {total_saved}")
    return round(total_saved, 2)


def simple_search(transactions: List[Dict[str, Any]], query: str) -> str:
    """Ищет строку в описании или категории транзакции.

    Args:
        transactions: Список транзакций.
        query: Строка для поиска.

    Returns:
        JSON со списком найденных транзакций.
    """
    query = query.lower()
    results = []
    for t in transactions:
        desc = str(t.get("Описание", "")).lower()
        category = str(t.get("Категория", "")).lower()

        if query in desc or query in category:
            results.append(t)

    logger.info(f"Поиск по запросу '{query}': найдено {len(results)} транзакций.")
    return json.dumps(results, ensure_ascii=False, indent=2)
