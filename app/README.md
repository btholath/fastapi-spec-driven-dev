# Activate python virtual environment
cd /workspaces/fastapi-spec-driven-dev
python3 -m venv .venv
source .venv/bin/activate


# Install Dependencies
cd /workspaces/fastapi-spec-driven-dev
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install --timeout 100 -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
pip uninstall langsmith langchain-core unstructured-client -y
pip show pytest six urllib3


(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ lsof -i :8000
COMMAND   PID      USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
uvicorn 17979 codespace    3u  IPv4 214181      0t0  TCP localhost:8000 (LISTEN)
python3 23693 codespace    3u  IPv4 214181      0t0  TCP localhost:8000 (LISTEN)
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ 

kill -9 17979
kill -9 23693
lsof -i :8000


# Cleanup & Rebuild
cd /workspaces/fastapi-spec-driven-dev
source .venv/bin/activate
docker-compose down
docker system prune -f  # Remove unused images
DOCKER_BUILDKIT=0 docker-compose up --build


# check containers
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ docker ps
CONTAINER ID   IMAGE                         COMMAND                  CREATED              STATUS              PORTS                                         NAMES
ee73b0dbd044   fastapi-spec-driven-dev-app   "uvicorn app.main:ap…"   About a minute ago   Up About a minute   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   fastapi-spec-driven-dev-app-1
7d68ff75ae41   postgres:16                   "docker-entrypoint.s…"   About a minute ago   Up About a minute   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   fastapi-spec-driven-dev-db-1
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ 


(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ docker exec -it fastapi-spec-driven-dev-app-1 apt-get update
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ docker exec -it fastapi-spec-driven-dev-app-1 apt-get install -y netcat-openbsd
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ docker exec -it fastapi-spec-driven-dev-app-1 nc -zv db 5432
Connection to db (172.18.0.2) 5432 port [tcp/postgresql] succeeded!


--Initialize the database
-- Run init_db.py inside the app container
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $  
cd /workspaces/fastapi-spec-driven-dev
source .venv/bin/activate
docker exec -it fastapi-spec-driven-dev-app-1 python /app/init_db.py

# verify
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ docker exec -it fastapi-spec-driven-dev-db-1 psql -U postgres -d postgres -c "SELECT * FROM annuities;"
 id | principal | term_years | annual_rate | premium 
----+-----------+------------+-------------+---------
(0 rows)
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ 

# Check container logs
docker-compose logs

# test connectivity from the app container
docker exec -it fastapi-spec-driven-dev-app-1 ping db

# verify the directory structure of this project
ls -R /workspaces/fastapi-spec-driven-dev

# configure VS Code
-- Ensure the test runner works in Codespaces.
Update /workspaces/fastapi-spec-driven-dev/.vscode/settings.json
{
    "python.pythonPath": "/workspaces/fastapi-spec-driven-dev/.venv/bin/python",
    "python.testing.pytestArgs": [
        "tests",
        "--asyncio-mode=auto"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true
}

Run tests in VS Code:


# Fix ModuleNotFoundError: No module named 'app' in Tests
The ModuleNotFoundError occurs because the Python path does not include the project root (/workspaces/fastapi-spec-driven-dev), so app cannot be resolved when running tests. We’ll set the PYTHONPATH and ensure the test file is correct.
Action:
Set the PYTHONPATH environment variable
export PYTHONPATH=/workspaces/fastapi-spec-driven-dev:$PYTHONPATH


Open tests/unit/test_annuity.py → Click Run Tests.
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ 
cd /workspaces/fastapi-spec-driven-dev
source .venv/bin/activate
export PYTHONPATH=/workspaces/fastapi-spec-driven-dev:$PYTHONPATH
pytest -v tests/unit/test_annuity.py



# Run tests
source .venv/bin/activate
pytest -v tests/unit/test_annuity.py

# Run Your FastAPI Application
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ uvicorn app.main:app --reload
INFO:     Will watch for changes in these directories: ['/workspaces/fastapi-spec-driven-dev']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [17979] using StatReload
INFO:     Started server process [17981]
INFO:     Waiting for application startup.
INFO:     Application startup complete.


# verify premium calculation
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ python -c "principal=10000; r=0.03/12; n=60; print(round(principal * (r * (1 + r)**n) / ((1 + r)**n - 1), 2))"
179.69


# Testing API
(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ curl -X POST "http://localhost:8000/annuities/premium" -H "Authorization: Bearer fake-token" -H "Content-Type: application/json" -d '{"principal": 10000, "term_years": 5, "annual_rate": 3}'

{"principal":10000.0,"term_years":5,"annual_rate":3.0,"id":1,"premium":2183.55}

(.venv) @btholath ➜ /workspaces/fastapi-spec-driven-dev (main) $ 



Step 1: Fix Test Failure (socket.gaierror in test_create_annuity_happy_path)
The socket.gaierror in the test occurs because the get_async_session dependency in app/dependencies.py tries to connect to postgresql+asyncpg://postgres:admin@db:5432/postgres from the Codespaces host, which cannot resolve the db hostname (defined in the Docker network). The test should fully mock the database session to avoid real database connections.
Action:

Update /workspaces/fastapi-spec-driven-dev/tests/unit/test_annuity.py to mock the Annuity object creation and database operations:

Run the mock tests
cd /workspaces/fastapi-spec-driven-dev
source .venv/bin/activate
export PYTHONPATH=/workspaces/fastapi-spec-driven-dev:$PYTHONPATH
pytest -v tests/unit/test_annuity.py