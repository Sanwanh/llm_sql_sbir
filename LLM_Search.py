import requests
import re
import psycopg2
import pandas as pd

# 設定 Ollama 伺服器的 IP 和 API 端點
OLLAMA_HOST = "192.168.1.106"
OLLAMA_URL = f"http://{OLLAMA_HOST}:11434/api/generate"

# 設定模型名稱
MODEL_NAME = "phi4:14b"

# 設定資料庫連線資訊
DB_PARAMS = {
    "dbname": "sbir1",
    "user": "postgres",
    "password": "postgres",
    "host": "192.168.1.14",
    "port": "5433"
}

# 設定系統提示詞，要求 Ollama 產生符合 SQL 規範的查詢指令
SYSTEM_PROMPT = """I have a data table call sbir1.public.real_final, and column will like:
SHRT_NM_2301 -> product title
nm_cd_2303 -> product code
ITM_NM_DEF_5015 description about this product
right now, I will provide search prompts below. Please generate relevant keywords related to the product and use an SQL command to select the data, ordering by relevance with the most relevant results at the top.

I am searching for a complete word, not breaking it down into individual characters.

The keywords do not need to be inside the prompts; please generate as many relevant ones as possible.

Provide the complete SQL command every time.

Please follow my format.

I am looking for a complete word, not breaking it down into individual characters.

ONLY SQL COMMAND OUTPUT
ONLY VALID SQL COMMAND
SELECT DISTINCT, ORDER BY expressions must appear in select list.

Example:
SELECT DISTINCT find AS inc, information,
  CASE
    ...
    WHEN information LIKE '%???%' THEN 1
    WHEN information LIKE '%???%' THEN 2
    ...
    ELSE ?
  END AS relevance
FROM sbir1.public.real_final
WHERE inc IS NOT NULL AND inc <> ''
  AND (
    information LIKE '%???%' OR
    information LIKE '%???%' OR
  )
ORDER BY relevance;

Search: 
"""

def query_ollama(search_prompt):
    """ 發送 SQL 產生請求到 Ollama 並獲取回應 """
    full_prompt = SYSTEM_PROMPT + search_prompt

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False  # 設定為 False 以獲取完整回應
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()  # 檢查請求是否成功
        data = response.json()
        sql_response = data.get("response", "")
        # print(sql_response)
        # 只提取sql ... 之間的內容
        match = re.search(r"```sql\n(.*?)\n```", sql_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "No valid SQL response found."

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


def execute_sql(query):
    """ 連線到 PostgreSQL 並執行查詢 """
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=columns)
                df = df.drop(columns=['relevance'])  # 移除 relevance 欄位
                pd.set_option('display.max_rows', None)  # 顯示所有行
                pd.set_option('display.max_columns', None)  # 顯示所有列
                # pd.set_option('display.max_colwidth', None)  # 顯示完整內容
                print(df.to_string(index=False))  # 顯示查詢結果，不省略內容
    except Exception as e:
        print("資料庫查詢錯誤:", e)


if __name__ == "__main__":
    print("Ollama SQL 查詢測試 (輸入 'exit' 來結束)")
    while True:
        search_input = input("Search: ")
        if search_input.lower() == "exit":
            print("結束對話")
            break
        sql_response = query_ollama(search_input)
        print("\n生成的 SQL 指令：\n")
        print(sql_response)
        print("\n執行查詢結果：\n")
        execute_sql(sql_response)
        print("\n")