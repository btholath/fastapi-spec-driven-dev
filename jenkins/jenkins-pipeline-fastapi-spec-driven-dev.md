Create a Jenkins Pipeline Job:

In Jenkins, click "New Item" > Name: fastapi-spec-driven-dev-pipeline > Select "Pipeline" > Click "OK."
Under "General," check "GitHub project" and enter: https://github.com/btholath/fastapi-spec-driven-dev/.
Under "Pipeline," select:

Definition: "Pipeline script"
Script: Use the following Groovy script:
groovypipeline {
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



Save the job.


Run the Job:

Click "Build Now" in the Jenkins UI.
Check "Build History" > Click the build number > "Console Output" to verify:

Repository is cloned.
Virtual environment is set up.
Tests are executed.
Allure report is generated.

----------------------------------------------------------------------------------
Update Pipeline for fastapi-spec-driven-dev
Ensure the pipeline job for fastapi-spec-driven-dev uses the configured JDK for Allure reporting.
Action:

Go to "Manage Jenkins" > "Manage Jobs" > Select fastapi-spec-driven-dev-pipeline > "Configure."
Update the pipeline script:
groovypipeline {
    agent any
    tools {
        jdk 'JDK17'
    }
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
                allure includeProperties: false, jdk: 'JDK17', results: [[path: 'allure-results']]
            }
        }
    }
}

Save and run the job ("Build Now").
Verify the Allure report in the build’s "Allure Report" link.