/*
 * Below annotation can be uncommented to implement the  shared-library methodology
 * @Library('shared-pipeline-library') _
 */
import groovy.json.JsonSlurperClassic
node {
    try {
        stage('InitFromSCM') {
            deleteDir()
            git poll: true, url: "$repo_url", branch: "$revision", credentialsId: 'f8b8fb25-f003-4e36-ae8b-c9304224048d'
            shortCommit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim().take(6)
            beanstalk_deployment = "swap-urls"
            dir('shared-library') {
                git poll: true, url: "$shared_lib_url", branch: "$shared_library_revision", credentialsId: 'f8b8fb25-f003-4e36-ae8b-c9304224048d'
            }
        }
        shared_lib = load 'shared-library/src/main/groovy/commons.groovy'
        load 'config/stages/preparation.groovy'
        load 'config/stages/build.groovy'
        load 'config/stages/publish_reports.groovy'
        load 'config/stages/deploy.groovy'

    } catch (error) {
        echo "ERROR IN PIPELINE"
        println error
        throw error
    } finally {

    }
}



