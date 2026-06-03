import os
from dotenv import load_dotenv

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent

from langchain_groq import ChatGroq

import datetime


import streamlit as st

import pandas as pd

import re


# Load environment variables
load_dotenv()

# log file
LOG_FILE = "logs.txt"

# Input validation (light)
def is_safe_input(text: str) -> bool:
    dangerous = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE"]
    text_upper = text.upper()

    for word in dangerous:
        if re.search(rf"\b{word}\b", text_upper):
            return False
    return True

# Output validation (strict)
def is_safe_output(text: str) -> bool:
    text_lower = text.lower().strip()

    dangerous = ["insert", "update", "delete", "drop", "alter", "truncate", "create"]
    if any(word in text_lower for word in dangerous):
        return False

    # SQL injection patterns
    if "--" in text_lower or "/*" in text_lower or "*/" in text_lower:
        return False

    # Multi-query hints
    if ";" in text_lower and "select" in text_lower:
        return False

    # Very large response protection
    if len(text_lower) > 5000:
        return False

    return True


# log fn 
def log_event(event_type: str, data: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{time}] [{event_type}] {data}\n")

# 1️. Connect LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0
)


# Insight enhancement layer (Phase 4)
def enhance_response(question: str, answer: str) -> str:
    if any(char.isdigit() for char in answer):
        return answer   
    
    prompt = f"""
    You are a data analyst.

    User Question:
    {question}

    Raw Answer:
    {answer}

    Convert this into a meaningful business insight.

    STRICT RULES:
    - ONLY use numbers present in the answer
    - DO NOT invent percentages or data
    - If multiple values are present, you MAY compare them
    - If only one value is present, just state it clearly
    - Avoid vague terms like "significant", "strong", unless supported by data
    - Keep it short and precise
    

    GOOD EXAMPLES:
    - "Total transactions recorded are 207,000."
    - "Rahul Sharma generated the highest revenue of $85,700."
    - "Revenue increased from 10,000 in January to 15,000 in March."

    BAD EXAMPLES:
    - "This shows strong growth" ❌
    - "Business is performing well" ❌

    Output:
    """

    try:
        enhanced = llm.invoke(prompt)
        return enhanced.content
    except:
        return answer


# 2️. Connect Database
db = SQLDatabase.from_uri(
    os.getenv("DATABASE_URL"),
    include_tables=[
        "users_table",
        "campaigns",
        "invoices",
        "transactions"
    ]
)

# 3️. Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# 4️. Prompt
prefix = """
You are a PostgreSQL expert.

STRICT RULES:
- ONLY use SELECT queries
- NEVER modify database (no DELETE, DROP, UPDATE, INSERT)
- If the question asks for modifying data, respond: "Operation not allowed"
- ALWAYS execute the query and return FINAL ANSWER only
- Do NOT return SQL query
- NEVER show SQL query
- NEVER explain the query
- ONLY return final answer


IMPORTANT:
- Always provide meaningful insights, not just raw numbers
- If possible, include comparisons (previous month, trends)
- Highlight increases or decreases in percentage when relevant
- Keep answers short but insightful
- Always use LIMIT 100 when returning rows
- Prefer aggregated results instead of full datasets
- ONLY use data returned from database
- NEVER fabricate historical data
- If data not available → say "No data available"

- ALWAYS respond in EXACTLY this format:
Final Answer: <your answer>

1. INTERPRETATION RULE:
- "total number of X" → COUNT(*)
- "total X" where X is money → SUM(amount)
- "total invoices" → COUNT(*)
- If unclear → default to COUNT

2. JOIN RULE:
- ALWAYS join users_table when user_id is used
- ALWAYS return user names, NEVER IDs

3. AGGREGATION RULE:
- Avoid duplicate rows when joining tables
- Use GROUP BY correctly
- Use DISTINCT if needed

4. OUTPUT RULE:
- Return clean formatted text
- Do NOT break words or characters

5. FILTER RULE:
- "above X" → amount > X
- "below X" → amount < X
- "greater than" → >
- "less than" → <

6. DATE RULE:
- "current month" = current system month using CURRENT_DATE
- "last month" = previous calendar month from CURRENT_DATE
- DO NOT use MAX(created_at)
- Use CURRENT_DATE for all time-based queries
- Example:
  current month → DATE_TRUNC('month', CURRENT_DATE)
  last month → DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')

  
IMPORTANT CURRENCY RULE:
- All monetary values are in Indian Rupees (INR)
- NEVER use "$" or "USD"
- Always display currency as "₹" or "INR"
- Example:
  Correct: ₹252,000
  Correct: INR 252,000
  Wrong: $252,000

Tables:
users_table(id, name, email)
campaigns(id, user_id, name, budget)
invoices(id, user_id, amount, status)
transactions(id, user_id, amount, description, created_at)

Notes:
- Use SUM() for totals
- Use COUNT() for counts
- Use DATE_TRUNC('month', created_at) for monthly filtering
"""

# 5️. Agent
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=False,
    agent_type="zero-shot-react-description",
    handle_parsing_errors=True,
    max_iterations=10,
    early_stopping_method="generate",
    prefix=prefix
)

# 5️ CORE LOGIC FUNCTION (PUT HERE)
def get_answer(question):
    log_event("QUESTION", question)

    if not is_safe_input(question):
        log_event("BLOCKED_INPUT", question)
        return "❌ Unsafe operation detected!"

    try:
        response = agent.invoke({"input": question})
    
        output = response["output"]

        # clean output
        if "Final Answer:" in output:
            output = output.split("Final Answer:")[-1].strip()

        enhanced_output = enhance_response(question, output)

        if not is_safe_output(enhanced_output):
            log_event("BLOCKED_OUTPUT", enhanced_output)
            return "❌ Unsafe response blocked!"

        log_event("RESPONSE", enhanced_output)
        return enhanced_output

    except Exception as e:
        log_event("ERROR", str(e))
        return "❌ I couldn't process that. Try rephrasing."
    

def generate_csv_from_answer(answer: str):
    """
    Convert text answer into simple CSV (basic version)
    """
    df = pd.DataFrame({
        "Result": [answer]
    })
    return df
