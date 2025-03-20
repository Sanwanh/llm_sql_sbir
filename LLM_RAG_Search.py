import os
import shutil
import psycopg2
import pandas as pd
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.chains import RetrievalQA
import chromadb

# Ollama 服務設定 (請根據您的環境修改)
OLLAMA_HOST = "192.168.1.106"
OLLAMA_URL = f"http://{OLLAMA_HOST}:11434"  # 注意這裡只需要 host 和 port，Langchain 會自動組裝 API 路徑
OLLAMA_MODEL = "phi4:14b"

# 資料庫連線資訊
DB_PARAMS = {
    "dbname": "sbir1",
    "user": "postgres",
    "password": "postgres",
    "host": "192.168.1.14",
    "port": "5433"
}

# SYSTEM_PROMPT (SQL 指令生成提示詞)
SYSTEM_PROMPT = """I have a data table called sbir1.public.real_final, with columns like:
SHRT_NM_2301 -> product title
NM_CD_2303 -> product code
ITM_NM_DEF_5015 -> description about this product

I will provide search prompts below. Please generate SQL queries using **only the exact search terms provided**, combining them in different order variations for better matching. **Do not expand keywords beyond those given.**

- **Only select product code (NM_CD_2303) and description (ITM_NM_DEF_5015).**  
- **Exclude results where product code (NM_CD_2303) is NULL or empty.**  
- **Remove duplicate product codes.**  
- **Ensure ORDER BY expressions appear in SELECT DISTINCT to prevent SQL errors.**  

ONLY SQL COMMAND OUTPUT  
ONLY VALID SQL COMMAND  
SELECT DISTINCT, ORDER BY expressions must appear in select list  

### Example:

```sql
SELECT DISTINCT
  nm_cd_2303,
  CASE
    WHEN shrt_nm_2301 ILIKE '%XXX%' THEN 1
    WHEN itm_nm_def_5015 ILIKE '%XXX%' THEN 2
    WHEN shrt_nm_2301 ILIKE '%XXX%YYY%' THEN 3
    WHEN itm_nm_def_5015 ILIKE '%XXX%YYY%' THEN 4
    ELSE 99
  END AS relevance
FROM sbir1.public.real_final
WHERE nm_cd_2303 IS NOT NULL AND nm_cd_2303 <> ''
  AND (
    shrt_nm_2301 ILIKE '%XXX%'
    OR itm_nm_def_5015 ILIKE '%XXX%'
    OR shrt_nm_2301 ILIKE '%XXX%YYY%'
    OR itm_nm_def_5015 ILIKE '%XXX%YYY%'
  )
ORDER BY relevance, nm_cd_2303;
```
Search:
"""
# 設定 Ollama LLM 和 Embeddings (Langchain 需要 base_url)
ollama_llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
ollama_embeddings = OllamaEmbeddings(base_url=OLLAMA_URL, model="bge-m3:latest")

# 檢查檔案是否存在
data_file = r"C:\Users\Win10\Documents\LLM\llm_sql_sbir\file\finish.txt"
if not os.path.isfile(data_file):
    print(f"錯誤：檔案 '{data_file}' 不存在或不是檔案。請確認檔案路徑是否正確。")
    exit()

# 載入 TXT 文件
documents = []
loader = TextLoader(data_file)
documents.extend(loader.load())

if not documents:
    print(f"錯誤：檔案 '{data_file}' 為空或無法讀取。")
    exit()

# 刪除舊的 ChromaDB 資料夾，避免維度衝突
persist_directory = "./chroma_db_sql_keywords"
shutil.rmtree(persist_directory, ignore_errors=True)

# 建立向量資料庫 (ChromaDB)
vectorstore = Chroma.from_documents(documents, embedding=ollama_embeddings, persist_directory=persist_directory)

# 建立 RetrievalQA 鏈 (用於 RAG 搜尋)
qa_chain = RetrievalQA.from_chain_type(
    llm=ollama_llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 1})  # 限制返回結果數量
)


# 搜尋並生成 SQL 指令的函數
def search_and_generate_sql(user_search_query):
    """
    使用 RAG 搜尋 TXT 文件，並根據搜尋結果和 SYSTEM_PROMPT 生成 SQL 指令。
    """
    # 1. 使用 RAG 搜尋相關文件片段
    rag_result = qa_chain.invoke({"query": user_search_query})
    retrieved_context = rag_result['result']

    # print(f"\n[RAG 搜尋結果]\n{retrieved_context}\n---")

    # 2. 將 RAG 結果放入 SYSTEM_PROMPT，生成最終 Prompt
    final_prompt = SYSTEM_PROMPT + retrieved_context + "\n\nONLY return a valid SQL query, no explanations."

    # 3. 使用 Ollama LLM 生成 SQL 指令
    sql_command = ollama_llm.invoke(final_prompt).strip()

    # 移除多餘的格式標記，例如 ```sql 或 ```
    sql_command = sql_command.replace("```sql", "").replace("```", "").strip()

    # 確保 SQL 指令有效
    if not sql_command.lower().startswith("select"):
        print("⚠️ LLM 生成的不是有效的 SQL 指令，請檢查 LLM 輸出。")
        print(f"\n🔍 LLM 回應內容:\n{sql_command}\n")
        return None

    # print(f"\n[SQL 指令]:\n{sql_command}\n")
    return sql_command

# 執行 SQL 查詢並過濾 relevance = 1
def execute_sql_query(sql_command):
    if sql_command is None:
        print("❌ SQL 指令無效，跳過執行。")
        return

    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_command)
                data = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]  # 取得實際的欄位名稱
                df = pd.DataFrame(data, columns=columns)  # 建立 DataFrame

                if "nm_cd_2303" in df.columns:
                    df = df[["nm_cd_2303"]]  # 只保留 nm_cd_2303 欄位
                else:
                    print("⚠️ 查詢結果不包含 nm_cd_2303，請檢查 SQL 查詢是否正確。")
                    return

                pd.set_option('display.max_row', None)
                pd.set_option('display.max_colwidth', None)  # 顯示完整內容
                print(df)  # 只顯示 nm_cd_2303
    except Exception as e:
        print("資料庫查詢錯誤:", e)

if __name__ == "__main__":
    while True:
        user_input = input("請輸入要查詢的產品名稱 (輸入 'exit' 離開): ")
        if user_input.lower() == 'exit':
            print("程式結束。")
            break
        sql_command = search_and_generate_sql(user_input)
        execute_sql_query(sql_command)
