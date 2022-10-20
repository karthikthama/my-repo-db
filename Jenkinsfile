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
                     cd $WORKSPACE/my-repo-db
                     zip -r $BRANCH.zip . -i $BRANCH
                     mv $WORKSPACE/my-repo-db/$BRANCH.zip /jenkins/backup
                     cp -r $WORKSPACE/my-repo-db/*.sql /jenkins/sql 
                     cp -r $WORKSPACE/my-repo-db/*.sql /jenkins/version
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
                    rsync -r --exclude 'my-repo-db' /jenkins/version/*.sql /jenkins/version/my-repo-db
                    cd /jenkins/version/my-repo-db
                    git config --global user.name "karthikthama"
                    git config --global user.email "tamakarthik@gmail.com"
                    git remote add origin https://karthikthama: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@github.com/karthikthama/my-repo-db.git || true
                    git remote set-url origin https://karthikthama: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@github.com/karthikthama/my-repo-db.git
                    git add . 
                    git commit -m "$BRANCH"
                    rm -rf /jenkins/version/my-repo-db
                    '''
                }     
            }
        }
    }
    post { 
        always { 
            cleanWs()
        }
    }
}
