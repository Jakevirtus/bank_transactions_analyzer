from unittest.mock import patch
import pandas as pd
from src.utils import read_transactions_excel


@patch("src.utils.pd.read_excel")
def test_read_transactions_excel_success(mock_read_excel):
    """Тестируем успешное чтение файла."""
    mock_df = pd.DataFrame({"Дата операции": ["2024-05-10"], "Сумма": [100]})
    mock_read_excel.return_value = mock_df

    result = read_transactions_excel("dummy.xlsx")
    assert not result.empty
    assert "Дата операции" in result.columns


@patch("src.utils.pd.read_excel")
def test_read_transactions_excel_not_found(mock_read_excel):
    """Тестируем случай, когда файл не найден."""
    mock_read_excel.side_effect = FileNotFoundError

    result = read_transactions_excel("bad.xlsx")
    assert result.empty
