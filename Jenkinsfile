node {

    stage 'Checkout'

    git branch: 'docker', url:'https://github.com/BCCVL/BCCVL_Visualiser.git'

    tag = "1.8.0.dev"

    docker.withRegistry('https://hub.bccvl.org.au', 'hub.bccvl.org.au') {
        docker.withServer('unix:///var/run/docker.sock') {

            stage 'Build'

            def imagename = "hub.bccvl.org.au/bccvl/visualiser:${tag}"

            echo "${env.DOCKER_REGISTRY_URL}"
            sh "docker build --rm -t '${imagename}' --no-cache=false ."

            stage 'Test'

            docker.image(imagename).inside("-u root") {

                sh "ENV=UNIT /cmd.sh"

                // copy test results to workdir
                sh 'cp /tmp/nosetests.xml "${PWD}/"'
                sh 'cp /tmp/coverage.xml "${PWD}/"'
                //sh "cd /opt/zope; ./bin/coverage html -d parts/jenkins-test/coverage-report"

                // capture unit test outputs in jenkins
                step([$class: 'JUnitResultArchiver', testResults: 'nosetests.xml'])

                //sh "yum install -y python-pip"
                //sh "pip install cobertura-clover-transform"  // needs lxml
                //sh "cobertura-clover-transform coverage.xml > clover.xml"

                //step([$class: 'CloverPublisher', cloverReportFileName: 'clover.xml'])
                //publishHTML(target: [allowMissing: false, alwaysLinkToLastBuild: false,
                //             keepAll: false,
                //             reportDir: 'jenkins-test/coverage-report',
                //             reportFiles: 'index.html',
                //             reportName: 'Coverage Report'])
            }

            stage 'Deploy'

            echo "Deploy turned off"
            //sh "docker push '${imagename}'"

            def depl = new org.bccvl.Deplay()
            depl.triggerDeploy("Visualiser", env.BRANCH_NAME, imagename);
        }
    }
}
