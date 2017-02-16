pipeline {

    agent {
        docker {
            image 'hub.bccvl.org.au/bccvl/visualiserbase:2017-02-01'
        }
    }

    stages {

        stage('Build') {

            steps {
                // environment {} is executed in node context, and there is no WORKSPACE defined
                withPyPi() {
                    // clear virtualenv
                    sh 'rm -fr ./virtualenv .cache ./BCCVL_Visualiser/.eggs'
                    sh 'ls -la'
                    // we should be inside the container with the workspace mounted at current working dir
                    // and running as jenkins user (should have read/write access to workspace)
                    // we need a virtual env here
                    sh 'virtualenv -p python2.7 --system-site-packages ./virtualenv'
                    // convert virtualenv to relocatable to avoid problems with too long shebangs
                    sh 'virtualenv --relocatable ./virtualenv'
                    // we want to run tests, so we should rather do an editable install
                    sh '. ./virtualenv/bin/activate; pip install -e ./BCCVL_Visualiser'
                    // make the additionally installed scripts relocatable to avoid long path problems with those as well
                    sh 'virtualenv --relocatable ./virtualenv'
                }
            }

        }
        stage('Test') {

            environment {
                PYTHONWARNINGS="ignore:Unverified HTTPS request"
            }

            steps {
                withPyPi() {
                    // make sure an old .coverage files doesn't interfere
                    sh 'rm -f BCCVL_Visualiser/.coverage'
                    // don't fail pipeline if there are test errors, we handle that on currentBuild.result conditions later
                    //sh(script: '. ./virtualenv/bin/activate; cd BCCVL_Visualiser; python setup.py nosetests --verbosity=2 --with-xunit --xunit-file=./nosetests.xml --with-coverage --cover-package=bccvl_visualiser --cover-xml --cover-xml-file=./coverage.xml',
                    //   returnStatus: true)
                    // For now generate html report as the jenkins cobertura plugin is not yet compatible with pipelines
                    sh(script: '. ./virtualenv/bin/activate; cd BCCVL_Visualiser; python setup.py nosetests --verbosity=2 --with-xunit --xunit-file=./nosetests.xml --with-coverage --cover-package=bccvl_visualiser --cover-html --cover-branches',
                       returnStatus: true)
                }
                // capture test result
                step([
                    $class: 'XUnitBuilder',
                    thresholds: [
                        [$class: 'FailedThreshold', failureThreshold: '0',
                                                    unstableThreshold: '1']
                    ],
                    tools: [
                        [$class: 'JUnitType', deleteOutputFiles: true,
                                              failIfNotNew: true,
                                              pattern: 'BCCVL_Visualiser/nosetests.xml',
                                              stopProcessingIfError: true]
                    ]
                ])
                // publish html coverage report
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: false,
                    keepAll: true,
                    reportDir: 'BCCVL_Visualiser/cover',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])

            }

        }

        stage('Package') {
            when {
                // check if we want to publish a package
                expression {
                    return publishPackage(currentBuild.result, env.BRANCH_NAME)
                }
            }
            steps {
                sh 'cd BCCVL_Visualiser; rm -rf build; rm -rf dist'
                withPyPi() {
                    // Build has to happen in correct folder or setup.py won't find MANIFEST.in file and other files
                    sh '. ./virtualenv/bin/activate; cd BCCVL_Visualiser; python setup.py register -r dev sdist bdist_wheel upload -r dev'
                    sh '. ./virtualenv/bin/activate; pip freeze > requirements.txt'
                }
            }
        }

        stage ('Push Artifact') {
            steps {
                archiveArtifacts artifacts: 'requirements.txt', fingerprint: true, onlyIfSuccessful: true
            }
        }

    }

    post {
        always {
            echo "This runs always"

            // cleanup virtualenv
            sh 'rm -fr ./virtualenv'

            // does this plugin get committer emails by themselves?
            // alternative would be to put get commiter email ourselves, and list of people who need to be notified
            // and put mail(...) step into each appropriate section
            // => would this then send 2 emails? e.g. changed + state email?
            step([
                $class: 'Mailer',
                notifyEveryUnstableBuild: true,
                recipients: 'gerhard.weis@gmail.com ' + emailextrecipients([
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
