import logging

import pandas as pd

logger = logging.getLogger(__name__)


def read_transactions_excel(filepath: str) -> pd.DataFrame:
    """Читает Excel-файл с транзакциями.

    Args:
        filepath: Путь к файлу Excel.

    Returns:
        DataFrame с транзакциями или пустой DataFrame в случае ошибки.
    """
    try:
        df = pd.read_excel(filepath)
        # Убедимся, что колонка с датой имеет правильный тип
        if "Дата операции" in df.columns:
            df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

        logger.info(f"Успешно прочитан файл {filepath}. Загружено строк: {len(df)}")
        return df
    except FileNotFoundError:
        logger.error(f"Файл не найден: {filepath}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {filepath}: {e}")
        return pd.DataFrame()
