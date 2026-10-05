# SpeechToNote — DuckDB analytics

Mirrors the MongoDB speaker-note data into an in-process DuckDB database for
analytical queries.

## Run

```bash
uv sync
uv run python run_operations.py
```

Run it from this directory — the module imports its siblings (`config`,
`connection`) by their top-level names.

MongoDB defaults to `mongodb://localhost:27017`; override with `MONGO_URI` /
`MONGO_DB_NAME` in a `.env` file or the environment.

```bash
docker run -d --name speechtonote-mongo -p 27017:27017 mongo:7
```