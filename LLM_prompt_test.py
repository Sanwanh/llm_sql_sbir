import requests
import re

# 設定 Ollama 伺服器的 IP 和 API 端點
OLLAMA_HOST = "192.168.1.106"
OLLAMA_URL = f"http://{OLLAMA_HOST}:11434/api/generate"

# 設定模型名稱
MODEL_NAME = "phi4:14b"

# 設定系統提示詞，要求 Ollama 產生符合 SQL 規範的查詢指令
SYSTEM_PROMPT = """I have a data table call find, and column will like:
information -> product title and description about this product
inc -> product code

right now i will put search prompts below, please think all single keywords that relate to this product, and using SQL command to select it and order by relative, more relevance at top.

keywords no need to inside prompts, please generate all you can think it.
Give me the complete SQL command every time.
Please follow my format.

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
FROM sbir1.public.find
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

        # 只提取 ```sql ... ``` 之間的內容
        match = re.search(r"```sql\n(.*?)\n```", sql_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "No valid SQL response found."

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


if __name__ == "__main__":
    print("Ollama SQL 查詢測試 (輸入 'exit' 來結束)")
    while True:
        search_input = input("Search: ")
        if search_input.lower() == "exit":
            print("結束對話")
            break
        sql_response = query_ollama(search_input)
        print("\n")
        print(sql_response)



