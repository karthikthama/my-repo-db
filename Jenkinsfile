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
                     cd $WORKSPACE/flyway-updated/my-repo-db
                     zip -r $BRANCH.zip . -i $BRANCH
                     mv $WORKSPACE/flyway-updated/my-repo-db/$BRANCH.zip /jenkins/backup
                     cp -r $WORKSPACE/flyway-updated/my-repo-db/$BRANCH/*.sql /jenkins/sql 
                     cp -r $WORKSPACE/flyway-updated/my-repo-db/$BRANCH/*.sql /jenkins/version
                     cp -r /jenkins/version/* /jenkins/sql 
                     '''
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
                    sh 'docker run --rm -v /jenkins/sql:/flyway/sql -v /jenkins/conf:/flyway/conf flyway/flyway -user=$DB_CREDS_USR -password=$DB_CREDS_PSW validate'
                }
            }
        }
        stage ('info') {
            steps {
                script {
                    sh 'docker run --rm -v /jenkins/sql:/flyway/sql -v /jenkins/conf:/flyway/conf flyway/flyway -user=$DB_CREDS_USR -password=$DB_CREDS_PSW info'
                }     
            }
        }
        stage ('upload to master') {
            steps {
                script {
                    sh ''' 
                    cd /jenkins/version
                    git clone https://github.com/karthikthama/my-repo-db.git
                    resync -av --exclude 'my-repo-db' /jenkins/version/*.sql '''
                }     
            }
        }
    }
}
