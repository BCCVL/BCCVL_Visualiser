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
    def imagename = "hub.bccvl.org.au/bccvl/visualiser:${version}-${env.BUILD_NUMBER}"

    def image = docker.build(imagename)

    stage 'Test'

    docker.image(imagename).inside("-u root") {

        sh "ENV=UNIT /cmd.sh"

        // copy test results to workdir
        sh 'cp /tmp/nosetests.xml "${PWD}/"'
        sh 'cp /tmp/coverage.xml "${PWD}/"'

        // capture unit test outputs in jenkins
        // step([$class: 'JUnitResultArchiver', testResults: 'nosetests.xml'])
        junit 'nosetsts.xml'

        // install cobertura -> clover transform (until robertura is supported in pipelines)
        sh "yum install -y python-pip"
        sh "pip install cobertura-clover-transform"  // needs lxml
        sh "cobertura-clover-transform coverage.xml > clover.xml"

        step([$class: 'CloverPublisher', cloverReportFileName: 'clover.xml'])

        // generate coverage report as html and capture it?
        //sh "cd /opt/zope; ./bin/coverage html -d parts/jenkins-test/coverage-report"
        //publishHTML(target: [allowMissing: false, alwaysLinkToLastBuild: false,
        //             keepAll: false,
        //             reportDir: 'jenkins-test/coverage-report',
        //             reportFiles: 'index.html',
        //             reportName: 'Coverage Report'])
    }

    // if (env.BRANCH_NAME == 'master') {

    //     stage 'Push Image'

    //     image.push()

    //     stage 'Deploy'

    //     deploy("Visualiser", env.BRANCH_NAME, imagename)

    // }

}
