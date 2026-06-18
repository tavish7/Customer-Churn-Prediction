# Phase 5: GenAI Customer Churn Chatbot

A natural-language chatbot that lets business users ask questions about Telco
customer churn and get plain-English answers. It uses **Google Gemini**
(`gemini-2.5-flash`) to turn questions into SQL, runs that SQL against a
**SQLite** star schema built from the Phase 1 cleaned dataset, and uses a
**LangGraph** self-correction loop that retries failed queries (up to 3 times)
by feeding the error back to the model.

## Architecture

```
User question
   |
   v
query_generator  (Gemini + schema context + 26 few-shot examples)
   |
   v
query_executor   (run read-only SQL on SQLite)
   |  success -> response_formatter -> answer
   |  error & retries left -> back to query_generator (with the error)
   |  error & retries exhausted -> graceful fallback message
   v
response_formatter (Gemini turns rows into a business answer)
```

## Project layout

```
phase5_chatbot/
  config.py              # paths, model settings, lazy LLM factory
  state.py               # LangGraph TypedDict state
  nodes.py               # query_generator / query_executor / response_formatter
  graph.py               # graph wiring + conditional retry edges
  app.py                 # interactive Streamlit chat UI
  ui/sample_questions.py # curated Q1-Q26 sample questions
  prompts/
    schema_context.py    # table/column schema + business rules for the LLM
    query_examples.py    # question -> SQL few-shot pairs
  database/
    connection.py        # read-only query runner + connection helpers
    init_db.py           # builds churn.db from the cleaned CSV
    sqlite_schema.sql    # star schema build script (runtime)
    churn.db             # generated locally (gitignored)
```

Data source: `../Data Files/customer_churn_clean.csv` (7,043 customers).
The SQLite schema mirrors the Phase 3 MySQL model in
`../Database and analysis/03_sqlite_schema_setup.sql`, and the 26 analytical
queries are ported in `../Database and analysis/03_sqlite_churn_queries.sql`.

## Setup

1. Install dependencies (from the project root):

   ```bash
   pip install -r requirements.txt
   ```

2. Add your Gemini API key:

   ```bash
   # copy the example and edit it
   cp phase5_chatbot/.env.example phase5_chatbot/.env
   # then set GOOGLE_API_KEY=...   (get one at https://aistudio.google.com/app/apikey)
   ```

3. (Optional) Pre-build the database. It is also built automatically on first
   run:

   ```bash
   python -m phase5_chatbot.database.init_db
   ```

## Run

```bash
streamlit run phase5_chatbot/app.py
```

Then either click a sample question or type your own, e.g.:

- "What is our overall churn rate?"
- "Which contract type has the highest churn?"
- "How much monthly revenue are we losing to churn?"
- "Which cities have the highest customer lifetime value?"
- "Who are the top 50 at-risk active customers we should contact?"

## Notes

- The query executor only allows read-only `SELECT` / `WITH` statements.
- SQLite uses integer division for `/`; rate calculations multiply by `100.0`
  first (see `prompts/schema_context.py`).
- ML churn *prediction* (Phase 2) is intentionally out of scope; this chatbot
  answers analytical questions from the database.
```
