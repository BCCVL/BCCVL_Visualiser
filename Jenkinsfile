pipeline {

    //options {
    //    buildDiscarder(logRotator(numToKeepStr: '10'))
    //
    //}

    agent {
        docker {
            image 'hub.bccvl.org.au/bccvl/visualiserbase:2017-02-01'
        }
    }

    stages {

        stage('Build') {

            environment {
                CPLUS_INCLUDE_PATH = '/usr/include/gdal'
                C_INCLUDE_PATH = '/usr/include/gdal'
                HOME = "${env.WORKSPACE}"
            }

            steps {
                sh 'env'

                // we should be inside the container with the workspace mounted at current working dir
                // and running as jenkins user (should have read/write access to workspace)
                // we need a virtual env here
                sh 'virtualenv -p python2.7 --system-site-packages ./virtualenv'
                // convert virtualenv to relocatable to avoid problems with too long shebangs
                sh 'virtualenv --relocatable ./virtualenv'
                sh '. ./virtualenv/bin/activate; pip install pytz'
                sh '. ./virtualenv/bin/activate; pip install -r BCCVL_Visualiser/requirements.txt'
                sh '. ./virtualenv/bin/activate; pip install -e BCCVL_Visualiser'
            }

        }
        stage('Test') {

            environment {
                PYTHONWARNINGS="ignore:Unverified HTTPS request"
            }

            steps {
                //sh 'mkdir -p /tmp/bccvl/map_data_files'
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

        stage('Package') {
            when {
                // branch accepts wildcards as well... e.g. "*/master"
                branch "master"
                expression { currentBuild.result && currentBuild.result == 'SUCCESS' }
            }
            steps {
                sh 'rm -rf build; rm -rf dist'
                sh './virtualenv/bin/python BCCVL_Visualiser/setup.py bdist_wheel'
            }
        }

        // stage('Push Artifact') {
        //     // archiveArtifacts artifacts: 'BCCVL_Visualiser/dist/*.whl', onlyIfSuccessful: true
        //     // stash 'climatemapcode'
        // }

    }

    post {
        always {
            echo "This runs always"
            // does this plugin get committer emails by themselves?
            // alternative would be to put get commiter email ourselves, and list of people who need to be notified
            // and put mail(...) step into each appropriate section
            // => would this then send 2 emails? e.g. changed + state email?
            step([
                $class: 'Mailer',
                notifyEveryUnstableBuild: true,
                recipients: 'g.weis@griffith.edu.au ' + emailextrecipients([
                    [$class: 'CulpritsRecipientProvider'],
                    [$class: 'RequesterRecipientProvider']
                ])
            ])
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
