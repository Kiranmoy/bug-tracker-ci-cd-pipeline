pipeline {
    agent any

    options {
        timestamps()
        ansiColor('xterm')
        skipDefaultCheckout(true)
    }

    parameters {
        choice(
            name: 'ENV',
            choices: ['dev', 'qa', 'staging'],
            description: 'Target environment'
        )
        string(
            name: 'GIT_REPO',
            defaultValue: 'https://github.com/Kiranmoy/bug-tracker-ci-cd-pipeline',
            description: 'Git repository URL'
        )
        string(
            name: 'GIT_BRANCH',
            defaultValue: 'main',
            description: 'Git branch to build'
        )
        booleanParam(
            name: 'RUN_UNIT',
            defaultValue: true,
            description: 'Run Unit Tests'
        )
        booleanParam(
            name: 'RUN_API',
            defaultValue: true,
            description: 'Run API Tests'
        )
        booleanParam(
            name: 'RUN_E2E',
            defaultValue: true,
            description: 'Run E2E Tests'
        )
        string(
            name: 'EMAIL_RECIPIENTS',
            defaultValue: 'paul.kiranmoy@gmail.com',
            description: 'Email recipients'
        )
    }

    environment {
        UNIT_IMAGE = 'python-pytest-unit'
        API_IMAGE  = 'python-playwright-api'
        E2E_IMAGE  = 'python-robot-e2e'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: params.GIT_BRANCH, url: params.GIT_REPO
            }
        }

        stage('Environment Setup') {
            steps {
                sh '''
                    docker --version
                    echo "Running tests on ENV=${ENV}"
                '''
            }
        }

        stage('Execute Tests in Parallel') {
            parallel {

                stage('Unit Tests (Pytest)') {
                    when { expression { params.RUN_UNIT } }
                    steps {
                        script {
                            docker.build(UNIT_IMAGE, 'unit-tests')
                            docker.image(UNIT_IMAGE).inside {
                                sh '''
                                    pytest tests \
                                     --html=unit-test-report.html \
                                     --self-contained-html
                                '''
                            }
                        }
                    }
                }

                stage('API Tests (Playwright - Python)') {
                    when { expression { params.RUN_API } }
                    steps {
                        script {
                            docker.build(API_IMAGE, 'api-tests')
                            docker.image(API_IMAGE).inside {
                                sh '''
                                    pytest tests \
                                      --browser chromium \
                                      --html=api-test-report.html \
                                      --self-contained-html
                                '''
                            }
                        }
                    }
                }

                stage('E2E Tests (Robot Framework)') {
                    when { expression { params.RUN_E2E } }
                    steps {
                        retry(2) {   // ✅ Flaky UI handling
                            script {
                                docker.build(E2E_IMAGE, 'e2e-tests')
                                docker.image(E2E_IMAGE).inside {
                                    sh '''
                                        robot \
                                          --variable ENV:${ENV} \
                                          --outputdir results \
                                          --report report.html \
                                          --log log.html \
                                          tests/
                                    '''
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Publish Test Reports') {
            steps {

                publishHTML target: [
                    allowMissing: true,
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    reportDir: 'unit-tests',
                    reportFiles: 'unit-test-report.html',
                    reportName: 'Unit Test Report'
                ]

                publishHTML target: [
                    allowMissing: true,
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    reportDir: 'api-tests',
                    reportFiles: 'api-test-report.html',
                    reportName: 'API Test Report'
                ]

                publishHTML target: [
                    allowMissing: true,
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    reportDir: 'e2e-tests/results',
                    reportFiles: 'report.html',
                    reportName: 'E2E Test Report'
                ]
            }
        }
    }

    post {
        always {
            emailext(
                subject: "Automation Results | ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                mimeType: 'text/html',
                to: params.EMAIL_RECIPIENTS,
                body: """
                    <h3>Automation Execution Summary</h3>
                    <ul>
                        <li>Environment: <b>${params.ENV}</b></li>
                        <li>Status: <b>${currentBuild.currentResult}</b></li>
                        <li>Job: ${env.JOB_NAME}</li>
                        <li>Build #: ${env.BUILD_NUMBER}</li>
                        <li><a href="${env.BUILD_URL}">Build Link</a></li>
                    </ul>
                """,
                attachmentsPattern: '**/*-report.html',
                attachLog: true
            )
        }
    }
}