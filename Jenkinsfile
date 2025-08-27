pipeline {
  agent any
  options { timestamps() }
  environment { VENV = ".venv" }

  stages {
    stage('Checkout') {
      steps {
        // If the repo is public, you can remove credentialsId
        git branch: 'main',
            url: 'https://github.com/btholath/fastapi-spec-driven-dev.git',
            credentialsId: 'github-pat'
      }
    }

    stage('Set Up Environment') {
      steps {
        sh '''
          python3 -m venv "$VENV"
          . "$VENV/bin/activate"
          "$VENV/bin/python" -m pip install -U pip wheel
          "$VENV/bin/python" -m pip install -r requirements.txt
          "$VENV/bin/python" - <<'PY'
import pkgutil, sys
sys.exit(0 if pkgutil.find_loader('allure_pytest') else 1)
PY
          if [ $? -ne 0 ]; then "$VENV/bin/python" -m pip install allure-pytest; fi
        '''
      }
    }

    stage('Run Tests') {
      steps {
        sh '''
          . "$VENV/bin/activate"
          export PYTHONPATH="$WORKSPACE:$PYTHONPATH"
          mkdir -p reports allure-results
          "$VENV/bin/pytest" -q \
            --junitxml=reports/junit.xml \
            --alluredir=allure-results \
            tests/unit/test_annuity.py
        '''
      }
    }

    stage('Generate Allure Report') {
      steps {
        allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'reports/**,allure-results/**', fingerprint: true, allowEmptyArchive: true
      junit allowEmptyResults: true, testResults: 'reports/junit.xml'
    }
  }
}
