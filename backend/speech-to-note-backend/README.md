# SpeechToNote — FastAPI backend

The API for SpeechToNote: stores speaker notes and voice commands in MongoDB
and serves them to the Vue frontend.

## Run

```bash
uv sync
uv run fastapi dev --port 8000
```

Interactive API docs: <http://127.0.0.1:8000/docs>

A MongoDB instance must be reachable at `MONGO_URI` (default
`mongodb://localhost:27017`):

```bash
docker run -d --name speechtonote-mongo -p 27017:27017 mongo:7
```

## Configuration

`CURRENT_ENV` selects the config class: `local` (default), `docker`, or
`kubernetes`. Values can be overridden in a `.env` file:

```bash
cp .env.example .env
```

| Variable       | Default                     | Description                       |
| -------------- | --------------------------- | --------------------------------- |
| `CURRENT_ENV`  | `local`                     | `local`, `docker`, `kubernetes`    |
| `MONGO_URI`    | `mongodb://localhost:27017` | MongoDB connection string         |
| `DATABASE_NAME`| `speechtonote`              | Database name                     |
| `DEBUG`        | `true` (local)              | Verbose logging                   |

## Tests

```bash
uv run pytest                  # route tests need MongoDB; they skip without it
uv run pytest tests/test_config.py   # no database required
```

Database tests use the `<DATABASE_NAME>_test` database and drop it at the end.