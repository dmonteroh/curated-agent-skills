# Release CI/CD Examples

## GitLab CI

```yaml
stages: [test, build, deploy]

test:
  stage: test
  image: node:20
  script:
    - npm ci && npm test

build:
  stage: build
  image: docker:latest
  services: [docker:dind]
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:production:
  stage: deploy
  script:
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  environment: production
  when: manual
  only: [main]
```

Verification: ensure build artifacts are pushed and deployment triggers only on `main`.

## Jenkins Pipeline

Requirements: Jenkins agents with Docker, `kubectl`, and `trivy` installed.

```groovy
pipeline {
    agent any

    environment {
        IMAGE = "registry.example.com/app"
    }

    stages {
        stage('Test') {
            steps {
                sh 'npm ci && npm test'
                junit 'reports/junit.xml'
            }
        }

        stage('Build') {
            steps {
                script {
                    docker.build("${IMAGE}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Security Scan') {
            steps {
                sh "trivy image ${IMAGE}:${BUILD_NUMBER}"
            }
        }

        stage('Deploy Staging') {
            when { branch 'main' }
            steps {
                sh "kubectl set image deployment/app app=${IMAGE}:${BUILD_NUMBER} -n staging"
            }
        }

        stage('Deploy Production') {
            when { branch 'main' }
            steps {
                input 'Deploy to production?'
                sh "kubectl set image deployment/app app=${IMAGE}:${BUILD_NUMBER} -n production"
            }
        }
    }

    post {
        failure {
            slackSend color: 'danger', message: "Build failed: ${JOB_NAME}"
        }
    }
}
```

Verification: review Jenkins stage logs and confirm deployments are gated.
