# Activate python virtual environment
cd /workspaces/fastapi-spec-driven-dev
python3 -m venv .venv
source .venv/bin/activate


# Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install --timeout 100 -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
pip uninstall langsmith langchain-core unstructured-client -y
pip show pytest six urllib3


# Run Your FastAPI Application
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ uvicorn app.main:app --reload
INFO:     Will watch for changes in these directories: ['/workspaces/fastapi-spec-driven-dev']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [17979] using StatReload
INFO:     Started server process [17981]
INFO:     Waiting for application startup.
INFO:     Application startup complete.


# Testing API
curl -X POST "http://localhost:8000/annuities/premium" -H "Authorization: Bearer fake-token" -H "Content-Type: application/json" -d '{"principal": 10000, "term_years": 5, "annual_rate": 3}'

