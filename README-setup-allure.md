To set up Allure reporting with pytest for the `fastapi-spec-driven-dev` project and execute a Python script using a Jenkins job that clones the repository from GitHub (`https://github.com/btholath/fastapi-spec-driven-dev`), we’ll follow these steps:

1. **Install and configure Allure with pytest** in the GitHub Codespaces environment for the `fastapi-spec-driven-dev` project.
2. **Update pytest configuration** to generate Allure reports for the existing tests (e.g., `tests/unit/test_annuity.py`).
3. **Set up a Jenkins job** to clone the repository, run the tests, and generate/serve the Allure report.
4. **Ensure the setup** integrates with the existing project structure, which uses FastAPI, pytest, and Docker, and addresses the annuity calculator tests.

The project uses pytest-driven unit tests and Gherkin-style BDD specs, with a sample annuity premium calculator. We’ll leverage the existing `pytest.ini` and test structure, and use the Jenkins setup from your previous context (running in `/workspaces/fastapi-spec-driven-dev/jenkins`).

### Step 1: Set Up Allure Reporting with Pytest
We’ll install the `allure-pytest` adapter, configure pytest to generate Allure results, and set up the Allure command-line tool to serve reports.

**Action**:
1. **Install Allure dependencies** in the virtual environment:
   ```bash
   cd /workspaces/fastapi-spec-driven-dev
   source .venv/bin/activate
   pip install allure-pytest
   ```
2. **Install Allure CLI** (requires Java):
   ```bash
   sudo apt-get update
   sudo apt-get install -y openjdk-17-jre
   wget https://github.com/allure-framework/allure2/releases/download/2.30.0/allure_2.30.0-1_all.deb
   sudo dpkg -i allure_2.30.0-1_all.deb
   ```
3. **Update `requirements.txt`** to include `allure-pytest`:
   ```bash
   echo "allure-pytest==2.15.0" >> requirements.txt
   ```
4. **Configure pytest for Allure**:
   - Ensure `/workspaces/fastapi-spec-driven-dev/pytest.ini` includes Allure settings:
     ```ini
     [pytest]
     python_files = tests/*.py
     python_functions = test_*
     addopts = --asyncio-mode=auto --alluredir=./allure-results
     ```
5. **Run pytest with Allure**:
   ```bash
   export PYTHONPATH=/workspaces/fastapi-spec-driven-dev:$PYTHONPATH
   pytest -v tests/unit/test_annuity.py
   ```
   - This generates JSON files in `/workspaces/fastapi-spec-driven-dev/allure-results`.
   - **Note**: If tests fail (e.g., due to the `socket.gaierror` from previous context), apply the fixes from the earlier response (update `app/dependencies.py` and `tests/unit/test_annuity.py` to mock `get_engine`).
6. **Generate and serve Allure report**:
   ```bash
   allure serve allure-results
   ```
   - This opens a browser with the Allure report. In Codespaces, forward the Allure port (default ~5000) in the "Ports" tab, similar to Jenkins port 8080.

### Step 2: Update Tests for Allure Metadata
Enhance `tests/unit/test_annuity.py` with Allure decorators to enrich reports with metadata (e.g., features, stories).

<xaiArtifact artifact_id="369c8915-186c-49d7-a0fd-8bd21edbfab8" artifact_version_id="260a3a9a-2b43-42b4-a97f-a300e24f4bad" title="test_annuity.py" contentType="text/python">
import pytest
import allure
from fastapi.testclient import TestClient
from app.main import app, get_current_user, get_async_session
from app.models.annuity import Annuity, Base
from app.services.annuity import calculate_premium
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

@allure.feature("Annuity Calculator")
@allure.story("Create Annuity Premium")
@pytest.mark.asyncio
async def test_create_annuity_happy_path(monkeypatch):
    # Mock get_current_user
    @allure.step("Mock authentication")
    async def mock_get_current_user(token: str):
        return {"id": 123, "role": "user"}
    monkeypatch.setattr("app.dependencies.get_current_user", mock_get_current_user)

    # Mock calculate_premium
    @allure.step("Mock premium calculation")
    def mock_calculate_premium(principal: float, term_years: int, annual_rate: float) -> float:
        return 2124.60
    monkeypatch.setattr("app.services.annuity.calculate_premium", mock_calculate_premium)

    # Mock SQLAlchemy engine, session, and metadata
    mock_engine = MagicMock(spec=create_async_engine)
    mock_sessionmaker = MagicMock(spec=async_sessionmaker)
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_sessionmaker.return_value.__aenter__.return_value = mock_session
    monkeypatch.setattr("app.dependencies.get_engine", MagicMock(return_value=mock_engine))
    monkeypatch.setattr("app.dependencies.async_sessionmaker", MagicMock(return_value=mock_sessionmaker))
    mock_metadata = MagicMock()
    mock_metadata.create_all = MagicMock()
    mock_metadata.drop_all = MagicMock()
    monkeypatch.setattr("app.models.annuity.Base", MagicMock(metadata=mock_metadata))

    # Mock Annuity object
    mock_annuity = MagicMock(spec=Annuity)
    mock_annuity.id = 1
    mock_annuity.principal = 10000.0
    mock_annuity.term_years = 5
    mock_annuity.annual_rate = 3.0
    mock_annuity.premium = 2124.60
    mock_session.add.side_effect = lambda x: setattr(x, "id", 1)
    mock_session.refresh.side_effect = lambda x: x
    monkeypatch.setattr("app.models.annuity.Annuity", MagicMock(return_value=mock_annuity))

    client = TestClient(app)
    with allure.step("Send POST request to create annuity"):
        response = client.post(
            "/annuities/premium",
            json={"principal": 10000, "term_years": 5, "annual_rate": 3},
            headers={"Authorization": "Bearer fake-token"}
        )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    assert response.json() == {
        "id": 1,
        "principal": 10000.0,
        "term_years": 5,
        "annual_rate": 3.0,
        "premium": 2124.60
    }
    mock_session.commit.assert_awaited()

@allure.feature("Annuity Calculator")
@allure.story("Validate Annuity Input")
@pytest.mark.asyncio
async def test_create_annuity_invalid_input(monkeypatch):
    @allure.step("Mock authentication")
    async def mock_get_current_user(token: str):
        return {"id": 123, "role": "user"}
    monkeypatch.setattr("app.dependencies.get_current_user", mock_get_current_user)

    client = TestClient(app)
    with allure.step("Send POST request with invalid input"):
        response = client.post(
            "/annuities/premium",
            json={"principal": -100, "term_years": 5, "annual_rate": 3},
            headers={"Authorization": "Bearer fake-token"}
        )
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.json()}"
    assert "greater than 0" in response.json()["detail"][0]["msg"]
</xaiArtifact>

- **Commit changes**:
  ```bash
  git add tests/unit/test_annuity.py pytest.ini requirements.txt
  git commit -m "Add Allure reporting to pytest tests"
  git push origin main
  ```

### Step 3: Set Up Jenkins Job to Execute Python Script
We’ll configure a Jenkins job to clone the `fastapi-spec-driven-dev` repository, run pytest with Allure, and generate the report. The Jenkins setup from your previous context (`/workspaces/fastapi-spec-driven-dev/jenkins`) is assumed to be running.

**Action**:
1. **Install Allure Jenkins Plugin**:
   - In Jenkins UI (`https://<codespace-id>-8080.githubpreview.dev`), go to "Manage Jenkins" > "Plugins" > "Available Plugins."
   - Search for "Allure" and install the "Allure" plugin (version ~2.31.0).
   - Alternatively, add to `plugins.txt` and rebuild:
     ```bash
     echo "allure:2.31.0" >> /workspaces/fastapi-spec-driven-dev/jenkins/plugins.txt
     cd /workspaces/fastapi-spec-driven-dev/jenkins
     docker-compose down
     docker-compose up -d --build
     ```

2. **Create a Jenkins Pipeline Job**:
   - In Jenkins, click "New Item" > Name: `fastapi-spec-driven-dev-pipeline` > Select "Pipeline" > Click "OK."
   - Under "General," check "GitHub project" and enter: `https://github.com/btholath/fastapi-spec-driven-dev/`.
   - Under "Pipeline," select:
     - Definition: "Pipeline script"
     - Script: Use the following Groovy script:
       ```groovy
       pipeline {
           agent any
           stages {
               stage('Checkout') {
                   steps {
                       git credentialsId: 'github-pat', url: 'https://github.com/btholath/fastapi-spec-driven-dev.git'
                   }
               }
               stage('Set Up Environment') {
                   steps {
                       sh '''
                       python3 -m venv .venv
                       . .venv/bin/activate
                       pip install -r requirements.txt
                       '''
                   }
               }
               stage('Run Tests') {
                   steps {
                       sh '''
                       . .venv/bin/activate
                       export PYTHONPATH=/var/jenkins_home/workspace/fastapi-spec-driven-dev-pipeline:$PYTHONPATH
                       pytest --alluredir=allure-results tests/unit/test_annuity.py
                       '''
                   }
               }
               stage('Generate Allure Report') {
                   steps {
                       allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
                   }
               }
           }
       }
       ```
   - Save the job.

3. **Run the Job**:
   - Click "Build Now" in the Jenkins UI.
   - Check "Build History" > Click the build number > "Console Output" to verify:
     - Repository is cloned.
     - Virtual environment is set up.
     - Tests are executed.
     - Allure report is generated.
   - **Expected Console Output** (partial):
     ```
     [Pipeline] git
     ...
     [Pipeline] sh
     + python3 -m venv .venv
     + . .venv/bin/activate
     + pip install -r requirements.txt
     ...
     [Pipeline] sh
     + pytest --alluredir=allure-results tests/unit/test_annuity.py
     ...
     [Pipeline] allure
     Allure report generated: /var/jenkins_home/workspace/fastapi-spec-driven-dev-pipeline@tmp/allure-report
     ```

4. **View Allure Report**:
   - In the Jenkins UI, click the build number > Look for the "Allure Report" link on the left.
   - Click to view the report, which includes test results for `test_annuity.py` with metadata (e.g., "Annuity Calculator" feature).

### Step 4: Configure GitHub Webhook
To trigger the Jenkins job on repository pushes:

**Action**:
- In GitHub, go to `https://github.com/btholath/fastapi-spec-driven-dev` > Settings > Webhooks > Add webhook.
- Payload URL: `https://<codespace-id>-8080.githubpreview.dev/github-webhook/`
- Content type: `application/json`
- Events: Select "Pushes" and "Pull requests."
- Check "Active" and click "Add webhook."

### Step 5: Verify Setup
- Push a change to the repository:
  ```bash
  cd /workspaces/fastapi-spec-driven-dev
  git commit --allow-empty -m "Trigger Jenkins build"
  git push origin main
  ```
- Check Jenkins for a new build triggered by the webhook.
- Verify the Allure report in the Jenkins UI.

### Troubleshooting
- **Allure Report Not Generated**:
  - Check Jenkins logs:
    ```bash
    docker logs fastapi-spec-driven-dev_jenkins_1
    ```
  - Ensure `allure-results` directory is created in the Jenkins workspace:
    ```bash
    docker exec fastapi-spec-driven-dev_jenkins_1 ls /var/jenkins_home/workspace/fastapi-spec-driven-dev-pipeline/allure-results
    ```
- **Tests Fail**:
  - If `test_create_annuity_happy_path` fails with `socket.gaierror`, ensure `app/dependencies.py` uses `get_engine` (as per previous response).
  - Run tests locally to debug:
    ```bash
    pytest -v tests/unit/test_annuity.py
    ```
- **Jenkins Job Fails**:
  - Verify `github-pat` credentials in Jenkins.
  - Check pipeline logs for errors in the `sh` steps.

### Notes
- The Allure report will show test results for `test_create_annuity_happy_path` and `test_create_annuity_invalid_input`, with metadata like "Annuity Calculator" and steps for authentication and premium calculation.
- The premium calculation discrepancy (2183.55 vs. 2124.60) requires `app/services/annuity.py`. Please share it to fix the formula.
- The Jenkins setup persists data via the `jenkins_home` volume.
- For BDD tests (Gherkin-style), ensure `pytest-bdd` is configured, and add Allure metadata to `tests/features/*.feature` files if needed.

Please share `/workspaces/fastapi-spec-driven-dev/app/services/annuity.py` to fix the premium calculation. Would you like to add Allure reporting for Gherkin-style BDD tests or focus on another aspect (e.g., CI/CD enhancements)?