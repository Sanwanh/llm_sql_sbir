import psycopg2

# 資料庫連線資訊
DB_PARAMS = {
    "dbname": "sbir1",
    "user": "postgres",
    "password": "postgres",
    "host": "192.168.1.14",
    "port": "5433"
}


def execute_query(nm_cd_2303):
    query = """
    SELECT
        nm_cd_2303,
        CONCAT(fsg_3994, fsc_wi_fsg_3996) AS merged_values,
        cl_asst_modh2_9554
    FROM "NM_CD_FSC_XREF-099"
    WHERE nm_cd_2303 = %s;
    """

    try:
        # 連線到 PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        # 執行查詢
        cursor.execute(query, (nm_cd_2303,))
        results = cursor.fetchall()

        # 顯示結果
        if results:
            for row in results:
                print(row)
        else:
            print("未找到相關資料。")

        # 關閉連線
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"發生錯誤: {e}")


if __name__ == "__main__":
    while True:
        nm_cd_2303 = input("請輸入 INC (輸入 'exit' 離開): ")
        if nm_cd_2303.lower() == 'exit':
            break
        execute_query(nm_cd_2303)