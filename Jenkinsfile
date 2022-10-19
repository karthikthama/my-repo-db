pipeline {
    agent any 
    environment {
        DB_CREDS=credentials('db-creds')
    }
    stages {
        stage ('git clone') {
            steps {
                script {
                    sh '''
                    rm -rf $WORKSPACE/*
                    git clone -b $BRANCH https://github.com/karthikthama/my-repo-db.git
                    '''    
                }     
            }
        }
        stage ('script check') {
            steps {
                echo "script checked"   
            }
        } 
        stage ('store') {
            steps {
                script {
                     sh '''
                     cd /var/lib/jenkins/workspace/flyway-updated
                     sudo mkdir /home/ubuntu/backup
                     sudo cp -r /var/lib/jenkins/workspace/flyway-updated/my-repo-db  /home/ubuntu/backup
                     cp -r /var/lib/jenkins/workspace/flyway-updated/my-repo-db/*.sql /jenkins/sql '''
                }               
            }
        }
        stage ('verfiy version') {
            steps {
                script {
                    sh '''
                    docker pull flyway/flyway:9.2.0
                    docker run --rm flyway/flyway:9.2.0 '''
                }
            }
        }
        stage ('migrate') {
            steps {
                script {
                    sh 'docker run --rm -v /jenkins/sql:/flyway/sql -v /jenkins/conf:/flyway/conf flyway/flyway -user=$DB_CREDS_USR -password=$DB_CREDS_PSW migrate'
                }
            }
        }         
        stage ('validate') {
            steps {
                script {
                    sh 'docker run --rm -v /jenkins/sql:/flyway/sql -v /jenkins/conf:/flyway/conf flyway/flyway -user=$DB_CREDS_USR -password=$DB_CREDS_PSW migrate'
                }
            }
        }
        stage ('info') {
            steps {
                script {
                    sh 'docker run --rm -v /jenkins/sql:/flyway/sql -v /jenkins/conf:/flyway/conf flyway/flyway -user=$DB_CREDS_USR -password=$DB_CREDS_PSW migrate'
                }     
            }
        }
        stage ('upload to master') {
            steps {
                script {
                    sh 'git merge $BRANCH'
                }     
            }
        }
    }
}
