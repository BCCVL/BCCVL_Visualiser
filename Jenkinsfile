pipeline {

    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))

    }

    agent {
        docker {
            image 'hub.bccvl.org.au/bccvl/visualiserbase:2017-02-01'
        }
    }

    stages {

        stage('Checkout') {

            steps {

                // checkout scm
                git url: 'https://github.com/BCCVL/BCCVL_Visualiser', branch:'docker'

            }

        }

        stage('Build') {

            environment {
                CPLUS_INCLUDE_PATH = '/usr/include/gdal'
                C_INCLUDE_PATH = '/usr/include/gdal'
                HOME = "${env.WORKSPACE}"
            }

            steps {
                // we should be inside the container with the workspace mounted at current working dir
                // and running as jenknis user (should have read/write access to workspace)
                // we need a virtual env here
                sh 'virtualenv -p python2.7 --system-site-packages ./virtualenv'
                sh './virtualenv/bin/pip install --upgrade setuptools'
                sh './virtualenv/bin/pip install pytz'
                sh './virtualenv/bin/pip install -r BCCVL_Visualiser/requirements.txt'
                sh './virtualenv/bin/pip install -e BCCVL_Visualiser'
            }

        }
        stage('Test') {

            environment {
                PYTHONWARNINGS="ignore:Unverified HTTPS request"
            }

            steps {
                sh 'mkdir -p /tmp/bccvl/map_data_files'
                // don't fail pipeline if there are test errors, we handle that on currentBuild.result conditions later
                sh(script: 'cd BCCVL_Visualiser; ../virtualenv/bin/nosetests -v -v --with-xunit --xunit-file=./nosetests.xml --with-coverage --cover-package=bccvl_visualiser --cover-xml --cover-xml-file=./coverage.xml',
                   returnStatus: true)

                // capture test result
                //junit 'BCCVL_Visualiser/nosetests.xml'
                step([
                    $class: 'XUnitBuilder',
                    thresholds: [
                        [$class: 'FailedThreshold', failureThreshold: '1',
                                                    unstableThreshold: '1']
                    ],
                    tools: [
                        [$class: 'JUnitType', pattern: 'BCCVL_Visualiser/nosetests.xml']
                    ]
                ])

            }

        }
        stage('End') {
            when {
                expression { currentBuild.result && currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo "End Stage ran"
            }
        }
        //stage('Build Image') {

        //}
        //stage('Deploy') {

        //}
    }

    post {
        always {
            echo "This runs always"
            // does this plugin get committer emails by themselves?
            // alternative would be to put get commiter email ourselves, and list of people who need to be notified
            // and put mail(...) step into each appropriate section
            // => would this then send 2 emails? e.g. changed + state email?
            step([$class: 'Mailer', notifyEveryUnstableBuild: true, recipients: 'g.weis@griffith.edu.au', sendToIndividuals: true])
        }
        success {
            echo 'This will run only if successful'
        }
        failure {
            echo 'This will run only if failed'
        }
        unstable {
            echo 'This will run only if the run was marked as unstable'
        }
        changed {
            echo 'This will run only if the state of the Pipeline has changed'
            echo 'For example, the Pipeline was previously failing but is now successful'
        }
    }

}
