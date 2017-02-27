pipeline {

    agent {
        docker {
            image 'hub.bccvl.org.au/bccvl/visualiserbase:2017-02-27'
        }
    }

    stages {

        stage('Build') {

            // environment {} is executed in node context, and there is no WORKSPACE defined

            steps {
                // clean git clone (removes all build files like virtualenv etc..)
                sh 'git clean -x -d -f'

                withPyPi() {
                    // we should be inside the container with the workspace mounted at current working dir
                    // and running as jenkins user (should have read/write access to workspace)
                    // we need a virtual env here
                    sh 'virtualenv -p python2.7 --system-site-packages ./virtualenv'
                    // convert virtualenv to relocatable to avoid problems with too long shebangs
                    sh 'virtualenv --relocatable ./virtualenv'
                    // build wheel to install (workaround where pip install would install via a tmp directory vhere no .git repo is and guscmversion wolud fail to determine correct version)
                    sh '. ./virtualenv/bin/activate; python setup.py bdist_wheel'
                    // we want to run tests, so we should rather do an editable install but we also don't want to have '-e links' in pip freeze output
                    //   pro: non editable tests packaging as well; con: weirdness with running tests form different location
                    sh '. ./virtualenv/bin/activate; pip install ./dist/*.whl'
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
                    // don't fail pipeline if there are test errors, we handle that on currentBuild.result conditions later
                    // also we shouldn't run the tests form source clone against non editable install of package
                    //     nose happily does that, py.test warns and fails to properly generate xml test output
                    //sh(script: '. ./virtualenv/bin/activate; python setup.py nosetests --verbosity=2 --with-xunit --xunit-file=./nosetests.xml --with-coverage --cover-package=bccvl_visualiser --cover-xml --cover-xml-file=./coverage.xml',
                    //   returnStatus: true)
                    // For now generate html report as the jenkins cobertura plugin is not yet compatible with pipelines
                    sh(script: '. ./virtualenv/bin/activate; python setup.py nosetests --verbosity=2 --with-xunit --xunit-file=./nosetests.xml --with-coverage --cover-package=bccvl_visualiser --cover-html --cover-branches',
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
                                              pattern: 'nosetests.xml',
                                              stopProcessingIfError: true]
                    ]
                ])
                // publish html coverage report
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: false,
                    keepAll: true,
                    reportDir: 'cover',
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
                withPyPi() {
                    // Build has to happen in correct folder or setup.py won't find MANIFEST.in file and other files
                    sh '. ./virtualenv/bin/activate; python setup.py register -r devpi sdist bdist_wheel upload -r devpi'
                }
            }
        }

        stage ('Push Artifact') {
            steps {
                sh '. ./virtualenv/bin/activate; pip freeze > requirements.txt'
                archiveArtifacts artifacts: 'requirements.txt', fingerprint: true, onlyIfSuccessful: true
            }
        }

    }

    post {
        always {
            echo "This runs always"

            // clean git clone (removes all build files like virtualenv etc..)
            sh 'git clean -x -d -f'

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
