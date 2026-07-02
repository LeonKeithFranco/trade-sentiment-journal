# Trade Sentiment Journal

A trading journal that pairs trade logging with sentiment analysis of your own journal entries. It then correlates that sentiment against actual trade outcomes. Built with a FastAPI backend, a from-scratch PyTorch BiLSTM for sentiment classification, and a Streamlit client.

## What problem this solves

Traders keep journals but rarely go back and check whether what they *felt* about a trade lined up with what actually *happened*. This project aims to make that check automatic. Every journal entry is run through a sentiment classifier in the background, and two analytics endpoints surface the correlation: do your bullish trades actually make money, and does the model's confidence in a reading track with better or worse outcomes? The app shows a trader's patterns in their own past behaviour; what they do with that information is up to them thereafter.

## Tech stack
 
- Python 3.12
- uv (workspace with three members: `backend`, `dl`, `frontend`)
- FastAPI + SQLAlchemy (async) + Alembic + PostgreSQL
- PyTorch (from-scratch BiLSTM sentiment classifier) + Marimo
- Streamlit + Plotly
- Podman Compose

## Architecture

The project is split into three uv workspaces:

**`dl`**: The sentiment model, built and trained independently of the backend; built with marimo notebooks. A BiLSTM over frozen GloVe embeddings. Ships as an importable package that the backend depends on directly.  
**`backend`**: A FastAPI service layered as Route -> Service -> Repository using separate domains. Loads the trained model once at startup via a lifespan context manager and fails fast if the model artifacts are missing. Background sentiment analysis runs via FastAPI `BackgroundTasks` after journal entry creation.  
**`frontend`**: A Streamlit client that talks to the backend using `httpx`. Communication with the backend is strictly over HTTP, the frontend doesn't import at all from the backend.

### Data flow

1. User registers/logs in and the backend then issues an access token and refresh token
2. User logs a trade (ticker, direction, size, entry/exit price, opened/closed time)
3. User writes a journal entry tied to that trade
4. In the background, the entry's text is run through the sentiment model. The result (sentiment + confidence) is stored and linked to the entry
5. Once enough closed trades have associated sentiment, the analytics endpoints group P&L by sentiment and by confidence. This lets the user see whether their stated sentiment tracked their actual outcomes.

## Running locally

### Prerequisites

- Python 3.12+
- uv
- Podman (or Docker) + Compose
- The trained model artifacts (`model.pth`, `vocab_mapping.json`, `matrix_embeddings.npy`) in `dl/data/`, since these are gitignored and not part of a fresh clone. See below for how to produce them

### Producing the model artifacts

The artifacts aren't checked into the repo. To generate from scratch:

1. Download the [GloVe 6B](https://nlp.stanford.edu/projects/glove/) embeddings and place `glove.6B.100d.txt` in `dl/data/`
2. Go into `dl` directory and sync: `cd dl && uv sync`
3. Run the data notebook to build the vocabulary mapping and the matched embedding matrix: `uv run notebooks/get_and_cache_data.py`. This also downloads and caches the [Financial PhraseBank](https://huggingface.co/datasets/lmassaron/FinancialPhraseBank) training data on the first run
4. Run the training notebook to train and produce the model: `uv run notebooks/model.py`

Both notebooks place their outputs in `dl/data/`. Once all three artifacts exist, the backend will load them at startup.

### Podman Compose

1. Clone the repo
2. Ensure `dl/data/` contains the three model artifacts as specified above
3. Create `.env` files at the root, `backend/`, and `frontend/` based off of the corresponding `.env.template`, filling in with real values
4. Build and run the containers: `podman-compose up --build`
5. Open the frontend at `http://localhost:8501`. The backend is at `http://localhost:8000`, with interactive docs at `/docs`

## Auth flow

Registration and login are standard email/password combination against a FastAPI backend using `pwdlib` (Argon2) for hashing. On login, the backend issues a short-lived access token (15 min) and a longer-lived refresh token (7 days). Access token is a JWT while the refresh token is a random hash stored in the database. The frontend stores both in Streamlit's session state.

Every authenticated request carries the access token as a Bearer header. If the access token is expired, the frontend calls `POST /auth/refresh` with the stored refresh token, retries the original request with the new access token. If the retry fails, an error message is shown and the user will have to re-login.

Session state in Streamlit is tied to the browser tab. Close the tab clears it; if this were to be made into a production-ready app, persistent cookies would be used instead.

## API

### Auth
 
| Endpoint | Method | Description |
|---|---|---|
| `/auth/register` | POST | Create a user account |
| `/auth/login` | POST | Exchange email/password for an access + refresh token pair |
| `/auth/refresh` | POST | Exchange a refresh token for a new token pair |

### Trades
 
| Endpoint | Method | Description |
|---|---|---|
| `/trades` | POST | Log a trade (ticker, direction, size, entry price, and optionally exit price/closed_at for a closed trade) |
| `/trades` | GET | List the current user's trades |
 
P&L is computed automatically on insert/update via a SQLAlchemy event listener, direction-aware (long vs. short), and only populated once a trade is closed.

### Journal Entries
 
| Endpoint | Method | Description |
|---|---|---|
| `/journal-entries` | POST | Create a journal entry tied to a trade. Triggers background sentiment analysis. |
| `/journal-entries` | GET | List the current user's journal entries |

### NLP
 
| Endpoint | Method | Description |
|---|---|---|
| `/analyze` | POST | Run sentiment analysis on arbitrary text and get back a sentiment label + confidence score |
 
This is the same inference path used internally by the background task on journal entry creation, exposed directly for ad-hoc use.

### Analytics
 
| Endpoint | Method | Description |
|---|---|---|
| `/analytics/sentiment-vs-returns` | GET | Average/total P&L and entry count, grouped by journal entry sentiment, across the user's closed trades |
| `/analytics/confidence-breakdown` | GET | Same aggregates, grouped by model confidence band (low <0.5, medium <0.75, high ≥0.75) |
 
Both return an empty list if there's no closed-trade data yet; the frontend shows a "not enough data" message in that case rather than an empty chart.
 
**Error responses** (auth-protected endpoints): 401 for missing/invalid/expired tokens, 422 for validation failures, 404 for ownership mismatches or missing resources.
 
The above are the main endpoints. FastAPI generates interactive docs at `/docs` as well as shows the full list of endpoints.


## DL Methodology and honest limitations

The sentiment model is a from-scratch bidirectional LSTM, not a pretrained transformer. The point of building it this way wasn't to beat a pretrained model on accuracy, it was to show use and implementation of PyTorch fundamentals end-to-end: tokenization and vocab mapping, embedding lookup, a packed-sequence BiLSTM, class-weighted loss for imbalance, checkpointing on a validation metric, and honest evaluation.

### Setup

- **Dataset:** [Financial PhraseBank](https://huggingface.co/datasets/lmassaron/FinancialPhraseBank), ~3,800 sentences of financial news text, each labeled negative/neutral/positive by human annotators. Downloaded via HuggingFace `datasets` and cached to disk on first run.
- **Embeddings:** Frozen 100-dimensional GloVe vectors. Not fine-tuned due to a small amount of training examples
- **Architecture:** BiLSTM over the frozen embeddings, followed by two linear layers to a 3-class output (negative/neutral/positive). Dropout of 0.3 for regularization
- **Class imbalance:** The dataset is roughly 59% neutral. Loss is inverse-frequency weighted to prevent the model from just predicting the majority class
- **Checkpointing:** Selected on lowest validation loss

### Evaluation

Reported on the held-out test set, evaluated once, after the model was frozen:

- **Accuracy:** ~75%
- **Balanced accuracy:** ~75%, meaning the model isn't just coasting on the majority class
- **Per-class recall:** negative 84%, neutral 75%, positive 74%. Negative is the rarest class in the data and the highest recall, likely a consequence of the class weighting
- **Macro-F1**, per-class precision/recall, and the confusion matrix are all computed using `sklearn`

### Known limitations

- ~3,800 training examples is a small dataset for a from-scratch model
- No hyperparameter sweep was run to completion. The expectation is that further tuning would move the needle by one or two points at most
- A single from-scratch model is the entire pipeline

## Testing approach

- **Unit tests** (`dl/tests/`): Preprocessing and tokenization tests, including failure-mode coverage (missing vocab file, empty input)
- **Integration tests** (`backend/tests/integration/`): Full API endpoint tests via FastAPI's `TestClient`, backed by a real Postgres instance spun up per test session via `testcontainers`. Each domain (auth, trades, journal entries, nlp, analytics) has its own test module. Tests cover the happy path, ownership boundaries (a user can't see another user's data), validation failures, and auth failures. The nlp and analytics tests are contract tests, they assert on response shape and value ranges rather than exact model predictions, so they don't break every time the model is retrained
- **Background task testing:** Because the background sentiment task opens its own database session (independent of the request-scoped session `TestClient` overrides), test isolation required explicitly monkeypatching the task's session factory to point at the same test database

### Running tests
 
- All backend tests: `cd backend && uv run pytest`
- All dl tests: `cd dl && uv run pytest`

## Design decisions

- **Integer primary keys with UUID `public_id`:** internal IDs are sequential integers; a UUID `public_id` is what's exposed over the API for public use
- **BackgroundTasks over a task queue:** Celery, or the like, would be overkill at this scale. `BackgroundTasks` gets sentiment analysis off the request's critical path without adding infrastructure
- **One-to-one journal entry sentiment analysis:** each entry is analyzed once, enforced with a unique constraint on the foreign key
- **Fail-fast model loading:** the backend refuses to start if the model artifacts are missing, rather than starting in an incorrect state
- **No native DB enum for sentiment/direction:** both are stored as checked string columns rather than Postgres enums to avoid enum migration friction
- **Per-entry (not per-trade) analytics:** a trade with three journal entries contributes three data points to the sentiment-vs-returns aggregation, one per entry. This was chosen over deduplicating to one sentiment per trade because it avoids an arbitrary tiebreaker and treats each entry as its own observation

## Limitations & future work
 
**Known limitations (v1):**
 
- The Streamlit frontend has no trade-editing flow, even though the backend supports it (`PATCH /trades/{trade_public_id}`). Trades can be created (open or already closed) but not updated afterward through the UI, so a trade logged as open through the frontend has no way to be closed there once created
- No CI/CD pipeline. A Dockerized deployment exists and has been verified to boot end-to-end via Podman Compose, but there's no GitHub Actions workflow and no live deployment
- No structured logging. Background task failures currently go to stdout via `print`, which is workable locally but not something you'd want in a real deployment
- Model artifacts are not part of the repository or the CI story; anyone building the Docker image needs the trained weights locally first

**v2 extensions:**
 
- Trade tags and watchlists
- CI via GitHub Actions, and a live deployment (Fly.io or similar)
- Project-wide structured logging, starting with the background sentiment task
- Minimum-data thresholds on the analytics endpoints, so a handful of data points doesn't get presented with the same visual weight as a statistically meaningful sample
