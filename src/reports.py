import json
import logging
from datetime import datetime
from typing import Any, Callable, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


def save_report(filename: Optional[str] = None) -> Callable:
    """Декоратор, сохраняющий результат функции-отчета в JSON-файл.

    Args:
        filename: Имя файла для сохранения. Если не указано, генерируется автоматически.

    Returns:
        Обернутую функцию.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            file_name = (
                filename
                if filename
                else f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            )

            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                logger.info(f"Отчет успешно сохранен в файл {file_name}")
            except Exception as e:
                logger.error(f"Не удалось сохранить отчет: {e}")

            return result

        return wrapper

    return decorator


@save_report(filename="workday_spending_report.json")
def spending_by_workday(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> dict:
    """Выводит средние траты в рабочий и в выходной день за последние 3 месяца.

    Args:
        transactions: Датафрейм с транзакциями.
        date: Дата отсчета в формате 'dd.mm.yyyy'. Если не указана — текущая дата.

    Returns:
        Словарь со средними тратами.
    """
    # 1. Определяем дату отсчета
    if date is None:
        dt = datetime.now()
    else:
        dt = datetime.strptime(date, "%d.%m.%Y")

    three_months_ago = dt - relativedelta(months=3)

    # 2. Копируем датафрейм, чтобы не менять оригинал
    df = transactions.copy()

    # На всякий случай убеждаемся, что колонка с датой имеет тип datetime
    if not pd.api.types.is_datetime64_any_dtype(df["Дата операции"]):
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

    # 3. Фильтруем по дате (за последние 3 месяца)
    df = df[(df["Дата операции"] >= three_months_ago) & (df["Дата операции"] <= dt)]

    # 4. Оставляем только расходы (отрицательные суммы) и берем их по модулю
    df = df[df["Сумма операции"] < 0].copy()
    df["Сумма"] = df["Сумма операции"].abs()

    if df.empty:
        return {"Рабочий день": 0.0, "Выходной день": 0.0}

    # 5. Определяем, был ли день рабочим (0-4) или выходным (5-6)
    df["День недели"] = df["Дата операции"].dt.day_of_week
    df["Тип дня"] = df["День недели"].apply(
        lambda x: "Рабочий день" if x < 5 else "Выходной день"
    )

    # 6. Считаем среднее значение
    averages = df.groupby("Тип дня")["Сумма"].mean().round(2).to_dict()

    # Заполняем нулями, если какого-то типа дней не было в выборке
    return {
        "Рабочий день": averages.get("Рабочий день", 0.0),
        "Выходной день": averages.get("Выходной день", 0.0),
    }
