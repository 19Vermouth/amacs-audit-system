import pandas as pd
import duckdb

def run_etl(file_path):
    df = pd.read_csv(file_path)

    # Basic cleaning
    df['amount'] = df['amount'].astype(float)

    # Feature engineering
    df['is_night'] = df['time'].apply(lambda x: int(x < "06:00"))
    df['is_high_value'] = df['amount'].apply(lambda x: int(x > 500000))

    # Store in DuckDB
    con = duckdb.connect("audit.db")
    con.execute("CREATE TABLE IF NOT EXISTS transactions AS SELECT * FROM df")

    return df