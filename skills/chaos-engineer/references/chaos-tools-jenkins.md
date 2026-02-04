# Jenkins Chaos Pipeline

Provides a Jenkinsfile template for running chaos experiments in CI.

## Prerequisites

- Jenkins agents with `kubectl`, `jq`, and cloud CLI credentials.
- Access to the target cluster namespaces and chaos CRDs.
- Slack integration configured if notifications are required.

## Usage

1. Store the Jenkinsfile in the repo root or pipeline library.
2. Configure parameters for environment, chaos type, and duration.
3. Ensure chaos manifests and service accounts exist in the cluster.

## Verification

- Verify the pre-flight steady-state check passes before chaos.
- Confirm the chaos engine reaches `Complete` and pods recover.
- Review archived results for experiment outputs.

## Jenkinsfile Example

```groovy
pipeline {
    agent any

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging'],
            description: 'Target environment'
        )
        choice(
            name: 'CHAOS_TYPE',
            choices: ['pod-delete', 'network-latency', 'cpu-stress'],
            description: 'Type of chaos experiment'
        )
        string(
            name: 'DURATION',
            defaultValue: '300',
            description: 'Chaos duration in seconds'
        )
    }

    stages {
        stage('Pre-flight Check') {
            steps {
                script {
                    def errorRate = sh(
                        script: '''
                            curl -s "http://prometheus/api/v1/query?query=rate(http_requests_total{status=~\\"5..\\"}[5m])" | jq -r '.data.result[0].value[1]'
                        ''',
                        returnStdout: true
                    ).trim()

                    if (errorRate.toFloat() > 0.01) {
                        error("System not in steady state. Error rate: ${errorRate}")
                    }
                }
            }
        }

        stage('Run Chaos Experiment') {
            steps {
                script {
                    def chaosManifest = """
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: jenkins-chaos-${env.BUILD_NUMBER}
  namespace: ${params.ENVIRONMENT}
spec:
  appinfo:
    appns: '${params.ENVIRONMENT}'
    applabel: 'app=myapp'
    appkind: 'deployment'
  chaosServiceAccount: litmus-admin
  experiments:
    - name: ${params.CHAOS_TYPE}
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: '${params.DURATION}'
"""

                    writeFile file: 'chaos-manifest.yaml', text: chaosManifest

                    sh '''
                        kubectl apply -f chaos-manifest.yaml
                        kubectl wait --for=condition=Complete chaosengine/jenkins-chaos-${BUILD_NUMBER} --timeout=900s
                    '''
                }
            }
        }

        stage('Verify Recovery') {
            steps {
                sh '''
                    sleep 60

                    kubectl get pods -n ${ENVIRONMENT} -l app=myapp

                    READY_PODS=$(kubectl get pods -n ${ENVIRONMENT} -l app=myapp -o json | jq '[.items[] | select(.status.phase=="Running")] | length')
                    TOTAL_PODS=$(kubectl get pods -n ${ENVIRONMENT} -l app=myapp -o json | jq '.items | length')

                    if [ "$READY_PODS" -ne "$TOTAL_PODS" ]; then
                        echo "Not all pods recovered: $READY_PODS/$TOTAL_PODS ready"
                        exit 1
                    fi
                '''
            }
        }

        stage('Extract Learnings') {
            steps {
                script {
                    def chaosResult = sh(
                        script: "kubectl get chaosresult -n ${params.ENVIRONMENT} -o json",
                        returnStdout: true
                    )

                    writeFile file: "chaos-result-${env.BUILD_NUMBER}.json", text: chaosResult
                    archiveArtifacts artifacts: "chaos-result-${env.BUILD_NUMBER}.json"
                }
            }
        }
    }

    post {
        always {
            sh '''
                kubectl delete chaosengine jenkins-chaos-${BUILD_NUMBER} -n ${ENVIRONMENT} || true
            '''
        }

        failure {
            slackSend(
                color: 'danger',
                message: "Chaos test failed: ${params.CHAOS_TYPE} in ${params.ENVIRONMENT}"
            )
        }

        success {
            slackSend(
                color: 'good',
                message: "Chaos test passed: ${params.CHAOS_TYPE} in ${params.ENVIRONMENT}. System recovered successfully."
            )
        }
    }
}
```
