
def imagename;

node {

    stage 'Checkout'

    if (! env.BRANCH_NAME) {
        env.BRANCH_NAME = 'docker'
        // checkout source
        git url: "https://github.com/BCCVL/BCCVL_Visualiser.git", branch: env.BRANCH_NAME
    } else {
        checkout scm
    }

    stage 'Build Image'

    def version = getPythonVersion('BCCVL_Visualiser/setup.py')
    imagename = "hub.bccvl.org.au/bccvl/visualiser:${version}-${env.BUILD_NUMBER}"

    def image = docker.build(imagename)

    stage 'Test'

    docker.image(imagename).inside("-u root") {

        sh "ENV=UNIT /cmd.sh"

        // copy test results to workdir
        sh 'cp /tmp/nosetests.xml "${PWD}/"'
        sh 'cp /tmp/coverage.xml "${PWD}/"'

        // capture unit test outputs in jenkins
        step([$class: 'JUnitResultArchiver', testResults: 'nosetests.xml'])

        // install cobertura -> clover transform (until robertura is supported in pipelines)
        sh "yum install -y python-pip libxslt-devel "
        sh "pip install cobertura-clover-transform"  // needs lxml
        sh "cobertura-clover-transform coverage.xml > clover.xml"

        step([$class: 'CloverPublisher', cloverReportDir: '', cloverReportFileName: 'clover.xml'])

        // generate coverage report as html and capture it?
        //sh "cd /opt/zope; ./bin/coverage html -d parts/jenkins-test/coverage-report"
        //publishHTML(target: [allowMissing: false, alwaysLinkToLastBuild: false,
        //             keepAll: false,
        //             reportDir: 'jenkins-test/coverage-report',
        //             reportFiles: 'index.html',
        //             reportName: 'Coverage Report'])
    }

    switch(env.BRANCH_NAME) {
        case 'docker':
        case 'master':
        case 'qa':
            stage 'Image Push'
            image.push()
            break
            // TODO: notify email/slack about new image?
            //       maybe even update dev-compose/config?
    }

}

switch(env.BRANCH_NAME) {

    case 'master':

        stage 'Approve'

        mail(to: 'g.weis@griffith.edu.au',
             subject: "Job '${env.JOB_NAME}' (${env.BUILD_NUMBER}) is waiting for input",
             body: "Please go to ${env.BUILD_URL}.");

        slackSend color: 'good', message: "Ready to deploy ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"

        input 'Ready to deploy?';

    case 'docker':
    case 'qa':

        stage 'Deploy'

        node {

            deploy("Visualiser", env.BRANCH_NAME, imagename)

            slackSend color: 'good', message: "Deployed ${env.JOB_NAME} ${env.BUILD_NUMBER}"

        }

        break

}
