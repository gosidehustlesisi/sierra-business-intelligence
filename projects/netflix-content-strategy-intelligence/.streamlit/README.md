# Netflix Content Intelligence

See the main [README.md](../../README.md) for project overview.

## Local Development Setup

To run the dashboard locally with TMDB API access:

1. Create `.streamlit/secrets.toml` in this directory:
```toml
TMDB_API_KEY = "your_api_key_here"
TMDB_READ_TOKEN = "your_read_token_here"
```

2. Run:
```bash
streamlit run dashboard.py
```

**Note:** Never commit `secrets.toml` to git. The `.streamlit/` directory is in `.gitignore`.

## Deployment

See [DEPLOY.md](DEPLOY.md) for Streamlit Cloud deployment instructions.
