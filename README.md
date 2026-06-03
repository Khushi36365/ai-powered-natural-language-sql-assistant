# AI-Powered Natural Language SQL Assistant

## Overview

An AI-powered SQL Assistant built using Streamlit, LangChain, LLM, and PostgreSQL.

The application allows users to interact with a PostgreSQL database using natural language. User questions are converted into SQL queries by an LLM, executed against the database, and returned as concise business insights.

---

## Project Structure

```text
.
├── app.py               # Streamlit UI
├── main.py              # AI agent, database, validation, logging
├── pyproject.toml       # Project dependencies
├── uv.lock              # Dependency lock file
├── .env                 # Environment variables
├── .gitignore
├── .python-version
├── logs.txt             # Application logs
└── README.md
```

---

## Architecture

```text
User
 │
 ▼
Streamlit UI (app.py)
 │
 ▼
LangChain SQL Agent (main.py)
 │
 ├── Input Validation
 ├── Groq LLM
 ├── PostgreSQL Database
 ├── Output Validation
 └── Logging
 │
 ▼
Business Insights
```

---

## Tech Stack

### Frontend

* Streamlit

### AI / LLM

* LangChain
* Groq
* Llama 3.1 8B Instant

### Database

* PostgreSQL

### Data Processing

* Pandas

### Environment Management

* uv

---

## Security Features

### Input Validation

Blocks potentially dangerous operations:

* DELETE
* DROP
* UPDATE
* INSERT
* ALTER
* TRUNCATE
* CREATE

### Output Validation

Prevents:

* Unsafe SQL responses
* SQL injection patterns
* Multi-query execution attempts
* Excessively large responses

### Database Protection

The SQL agent is restricted to generating SELECT queries only.

--- 

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd ai-sql-assistant
```

### Create Virtual Environment

```bash
uv venv
```

### Activate Virtual Environment

Windows:

```bash
.venv\Scripts\activate
```

Linux / Mac:

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
uv sync
```

---

## Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=your_postgresql_connection_string
```

---

## Run Application

```bash
streamlit run app.py
```

---

## Future Improvements

* Read-only database role
* Authentication & Authorization
* Data Visualization Dashboard
* Query Caching
* Advanced Analytics

---

## Author

Khushi Jhamb
