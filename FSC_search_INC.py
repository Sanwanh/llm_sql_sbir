import psycopg2

# 資料庫連線資訊
DB_PARAMS = {
    "dbname": "sbir1",
    "user": "postgres",
    "password": "postgres",
    "host": "192.168.1.14",
    "port": "5433"
}

def execute_query(fsc_pattern):
    query = """
    SELECT nm_cd_2303
    FROM "NM_CD_FSC_XREF-099"
    WHERE CONCAT(fsg_3994, fsc_wi_fsg_3996) LIKE %s
      AND nm_cd_2303 IS NOT NULL;
    """

    try:
        # 連線到 PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        # 執行查詢
        cursor.execute(query, (f"%{fsc_pattern}%",))
        results = cursor.fetchall()

        # 只取第一個欄位的值
        codes = [row[0] for row in results]
        print(len(results))
        # 格式化輸出
        if codes:
            print(f"'{', '.join(codes)}'")
        else:
            print("未找到相關資料。")

        # 關閉連線
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    while True:
        fsc_pattern = input("請輸入 FSC 關鍵字 (輸入 'exit' 離開): ")
        if fsc_pattern.lower() == 'exit':
            break
        execute_query(fsc_pattern)
