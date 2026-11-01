import os

import pandas as pd

from src.reports import spending_by_workday


def test_spending_by_workday(tmp_path):
    # Создаем фейковый датафрейм
    data = {
        "Дата операции": pd.to_datetime(["2024-05-06", "2024-05-11"]),  # Понедельник и суббота
        "Сумма операции": [-100.0, -200.0]
    }
    df = pd.DataFrame(data)

    # Вызываем функцию (декоратор создаст файл workday_spending_report.json)
    result = spending_by_workday(df, "24.05.2024")

    assert result["Рабочий день"] == 100.0
    assert result["Выходной день"] == 200.0

    # Проверяем, что файл создался (декоратор сработал)
    assert os.path.exists("workday_spending_report.json")
