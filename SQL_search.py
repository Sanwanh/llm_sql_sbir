import psycopg2
import pandas as pd

# 連線資訊
DB_PARAMS = {
    "dbname": "sbir1",
    "user": "postgres",
    "password": "postgres",
    "host": "192.168.1.14",
    "port": "5433"
}

# SQL 查詢
query = """
SELECT DISTINCT find AS inc, information,
  CASE
    WHEN information LIKE '%air flow detector%' THEN 1
    WHEN information LIKE '%airflow sensor%' THEN 2
    WHEN information LIKE '%pressure-based detector%' THEN 3
    WHEN information LIKE '%thermal detector%' THEN 4
    WHEN information LIKE '%turbine detector%' THEN 5
    WHEN information LIKE '%HVAC systems%' THEN 6
    WHEN information LIKE '%ventilation monitoring%' THEN 7
    WHEN information LIKE '%air distribution control%' THEN 8
    WHEN information LIKE '%industrial airflow%' THEN 9
    WHEN information LIKE '%safety ventilation%' THEN 10
    ELSE 11
  END AS relevance
FROM sbir1.public.find
WHERE inc IS NOT NULL AND inc <> ''
  AND (
    information LIKE '%air flow detector%' OR
    information LIKE '%airflow sensor%' OR
    information LIKE '%pressure-based detector%' OR
    information LIKE '%thermal detector%' OR
    information LIKE '%turbine detector%' OR
    information LIKE '%HVAC systems%' OR
    information LIKE '%ventilation monitoring%' OR
    information LIKE '%air distribution control%' OR
    information LIKE '%industrial airflow%' OR
    information LIKE '%safety ventilation%'
  )
ORDER BY relevance, inc;
"""

# 連線到 PostgreSQL 並執行查詢
try:
    with psycopg2.connect(**DB_PARAMS) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            df = df[df['relevance'] == 1]  # 只保留 relevance 為 1 的資料
            print(df)  # 顯示查詢結果
except Exception as e:
    print("資料庫查詢錯誤:", e)
