/*
 * Below annotation can be uncommented to implement the  shared-library methodology
 * @Library('shared-pipeline-library') _
 */
node {
    try {
        stage('InitFromSCM') {
            deleteDir()
            git poll: true, url: "$repo_url", branch: "$revision", credentialsId: 'f8b8fb25-f003-4e36-ae8b-c9304224048d'
            shortCommit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim().take(6)
            dir('shared-library') {
                git poll: true, url: "$shared_lib_url", branch: "$shared_library_revision", credentialsId: 'f8b8fb25-f003-4e36-ae8b-c9304224048d'
            }
            environment_name = "$stack_name"
            application_name ="ref"

        }
        shared_lib = load 'shared-library/src/main/groovy/commons.groovy'

        load 'config/stages/preparation.groovy'
        load 'config/stages/build.groovy'
        load 'config/stages/publish_reports.groovy'
        load 'config/stages/serverlessProvision.groovy'

    } catch(error) {
        echo "ERROR IN PIPELINE"
        println error
        throw error
    } finally{

    }
}
