# Copilot instructions for ChurnGuard

Quick goal: help an AI coding agent be productive in this repository by describing the architecture, key workflows, coding conventions, and concrete examples it can use when making changes.

- Big picture
  - Monolithic Streamlit app (`app.py`, `frontend/`) that imports backend modules directly. Not a microservice architecture: code runs in the same process.
  - Backend separation by responsibility: `backend/repositories/` (data access), `backend/services/` (business logic), `backend/models/` (ORM entities).
  - AI and ML code lives under `ai_agents/` (e.g. `ai_agents/churn_predictor/predictor.py`, `ai_agents/sentiment_analyzer/analyzer.py`). These are imported and used by services (e.g. `backend/services/churn_service.py`).
  - Database connectivity and initialization live in `database/` and `scripts/db_init.py`.

- Where to change behavior
  - Business rules → edit `backend/services/*.py` (e.g. `ChurnService.predict_churn_for_customer`).
  - Data access or feature engineering → edit `backend/repositories/customer_repository.py` (e.g. `get_customer_features`).
  - ML model logic → edit `ai_agents/churn_predictor/predictor.py` (feature list, training, save/load paths).
  - Frontend UI → edit files under `frontend/pages/` (Streamlit pages). `app.py` routes pages.

- Important files and examples (use these in PR descriptions)
  - `app.py` — Streamlit entry point and page routing.
  - `config/config.py` — central configuration loaded from environment and `.env` (see `.env.example`). Use `config.config` for constants like `CHURN_MODEL_PATH`.
  - `scripts/db_init.py` — database bootstrap (run before first use).
  - `scripts/train_model.py` — training harness for churn model (saves to `resources/models/`).
  - `backend/repositories/customer_repository.py` — example of repository pattern; functions return ORM objects or primitives.
  - `backend/services/churn_service.py` — example of service layer using DI (accepts SQLAlchemy Session) and calling predictor + repository.
  - `ai_agents/churn_predictor/predictor.py` — model load/save, feature columns: `['days_since_signup','days_since_last_activity','total_transactions','total_spend','avg_transaction_value','lifetime_value']`.

- Environment & runtime
  - Use virtualenv, install with `pip install -r requirements.txt`.
  - Copy and edit environment: `cp config/.env.example .env` (edit `GEMINI_API_KEY`, DB vars, `SECRET_KEY`).
  - Initialize DB: `python scripts/db_init.py`.
  - (Optional) Train model: `python scripts/train_model.py` — outputs `resources/models/churn_model.pkl` and scaler.
  - Run UI: `streamlit run app.py` (default localhost:8501).
  - Tests: `pytest tests/unit/` and `pytest tests/integration/`.

- Conventions and patterns to follow
  - Repository pattern for DB access: keep SQLAlchemy queries in `backend/repositories/*` and return domain objects.
  - Service layer for business logic: `backend/services/*` should orchestrate repos + agents and handle commit/rollback.
  - Dependency injection: services expect a SQLAlchemy `Session` (pass in tests/mocks).
  - Logging: use `logging.getLogger(__name__)`. Use `config.logging_config` for global setup.
  - Model artifacts: use `config.Config` paths (`CHURN_MODEL_PATH`, `CHURN_SCALER_PATH`) — don't hardcode paths.
  - Feature schema: preserve the feature ordering in `ChurnPredictor.feature_columns` when transforming data for model input.

- Integrations and external requirements
  - Google Gemini (API key in `GEMINI_API_KEY`) — used by NLQ/chat agents under `ai_agents/nlq_agent`.
  - PostgreSQL — DB credentials from `.env`; SQLAlchemy sessions are used across repos and services.
  - Python packages: scikit-learn (model), TextBlob (sentiment), LangChain (agents) — check `requirements.txt`.

- Safe edit examples (copy into PR message)
  - "Fix feature calc in `backend/repositories/customer_repository.py` — ensure `avg_transaction_value` uses `total_transactions` guard to avoid divide-by-zero; update unit test in `tests/unit/test_repository.py`."
  - "Replace rule-based fallback in `ai_agents/churn_predictor/predictor.py` with calibrated logistic regression; keep `feature_columns` stable and update `scripts/train_model.py` to persist scaler/model to `resources/models/`."

- Quick heuristics for reviewers/agents
  - When changing DB schema, update `scripts/db_init.py` and any code that constructs feature vectors.
  - Keep `feature_columns` stable — changing order breaks saved models. If reordering, retrain and update model artifacts.
  - Prefer adding small focused tests under `tests/unit/` that mock DB `Session` for services.
  - Avoid changing `config.Config` names — consuming code expects those attributes.

If anything here is unclear or you want more coverage (e.g. example tests, CI commands, or how the NLQ agents wire to Gemini), tell me which section to expand and I will iterate.