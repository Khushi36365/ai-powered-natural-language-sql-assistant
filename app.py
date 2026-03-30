import os
from dotenv import load_dotenv

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent

from langchain_groq import ChatGroq

import time

# Load environment variables
load_dotenv()

# 1️⃣ Connect LLM (Groq) — use stable model
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",   
    temperature=0
)

# 2️⃣ Connect Database (limit tables for better accuracy)
db = SQLDatabase.from_uri(
    os.getenv("DATABASE_URL"),
    include_tables=[
        "users_table",
        "campaigns",
        "invoices",
        "transactions"
    ]
)

# 3️⃣ Create Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# 4️⃣ Add strong system instructions (VERY IMPORTANT)
prefix = """
You are a PostgreSQL expert.

STRICT RULES:
- ONLY use SELECT queries
- NEVER modify database (no DELETE, DROP, UPDATE, INSERT)
- ALWAYS execute query and return FINAL ANSWER (not SQL)
- Do NOT use markdown
- Do NOT loop

Tables:
users_table(id, name, email)
campaigns(id, user_id, name, budget)
invoices(id, user_id, amount, status)
transactions(id, user_id, amount, description, created_at)
"""

# 5️⃣ Create Agent (fixed settings)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=False,
    agent_type="zero-shot-react-description",
    handle_parsing_errors=True,
    max_iterations=5,        # ✅ prevents infinite loop
    early_stopping_method="force",  # ✅ stops bad loops
    prefix=prefix
)

# 6️⃣ Chat Loop
print("AI SQL Assistant Ready! (type 'exit' to quit)")

while True:
    question = input("\nAsk your question: ")

    if question.lower() == "exit":
        break

    try:
        response = agent.invoke({"input": question})
        print("\nAnswer:", response["output"])

        time.sleep(2)

    except Exception as e:
        print("❌ Error:", e)