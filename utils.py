import pandas as pd
from src.etl import load_and_standardize_csv, auto_categorize

def import_and_categorize(file_path: str) -> pd.DataFrame:
    df = load_and_standardize_csv(file_path)
    df = auto_categorize(df)
    return df
