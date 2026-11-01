from typing import Any, Dict, List, cast

from src.reports import spending_by_workday
from src.services import investment_bank
from src.utils import read_transactions_excel
from src.views import main_page


def main():
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")

    # Читаем данные из Excel
    df = read_transactions_excel("data/operations.xlsx")
    if df.empty:
        print("Не удалось загрузить данные.")
        return

    # 1. Главная страница (за 20.05.2020)
    print("\n--- Главная страница ---")
    print(main_page("2020-05-20 12:00:00"))

    # 2. Копилка (за май 2020)
    print("\n--- Копилка (округление до 50) ---")
    # Явно указываем тип, чтобы PyCharm и mypy не ругались
    transactions = cast(List[Dict[str, Any]], df.to_dict(orient="records"))
    saved = investment_bank("2020-05", transactions, 50)
    print(f"Удалось бы отложить: {saved} руб.")

    # 3. Отчет по дням недели
    print("\n--- Отчет: Траты в рабочий/выходной день ---")
    report = spending_by_workday(df, "20.05.2020")
    print(report)


if __name__ == "__main__":
    main()
