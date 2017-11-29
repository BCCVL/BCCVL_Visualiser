node('docker') {

    try {

        stage('Checkout') {
            // clean git clone, but don't fail in case it doesn't exist yet
            sh(script: 'git clean -x -d -f', returnStatus: true)
            checkout scm
        }

        def img = docker.image('hub.bccvl.org.au/bccvl/visualiserbase:2017-11-29')
        docker.withRegistry('https://hub.bccvl.org.au', 'hub.bccvl.org.au') {
            img.inside('-v /etc/machine-id:/etc/machine-id') {

                withVirtualenv() {

                    stage('Build') {

                        sh '. ${VIRTUALENV}/bin/activate; pip install .'

                    }

                    stage('Test') {

                        // install test tools
                        sh '. ${VIRTUALENV}/bin/activate; pip install .[test] pytest pytest-cov'
                        // run tests
                        sh(script: '. ${VIRTUALENV}/bin/activate; PYTHONWARNINGS="ignore:Unverified HTTPS request" pytest -v --junitxml=junit.xml --cov-report=xml --cov=bccvl_visualiser --pyarg bccvl_visualiser',
                           returnStatus: true)

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
                                                      pattern: 'junit.xml',
                                                      stopProcessingIfError: true]
                            ]
                        ])
                        // publish html coverage report
                        step([$class: 'CoberturaPublisher',
                              coberturaReportFile: 'coverage.xml']
                        )

                    }

                    stage('Package') {

                        if (publishPackage(currentBuild.result, env.BRANCH_NAME)) {

                            sh 'rm -fr build dist'
                            // Build has to happen in correct folder or setup.py won't find MANIFEST.in file and other files
                            sh '. ${VIRTUALENV}/bin/activate; python setup.py register -r devpi sdist bdist_wheel upload -r devpi'

                        }
                    }

                    stage ('Push Artifact') {

                        // uninstall editable package
                        sh '. ${VIRTUALENV}/bin/activate; pip uninstall -y BCCVL_Visualiser'
                        sh '. ${VIRTUALENV}/bin/activate; pip freeze > requirements.txt'
                        archiveArtifacts artifacts: 'requirements.txt', fingerprint: true, onlyIfSuccessful: true
                    }
                }
            }
        }
    } catch(err) {
        throw err
    } finally {

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
}
