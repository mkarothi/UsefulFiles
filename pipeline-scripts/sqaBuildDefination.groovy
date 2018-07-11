/*
 * Below annotation can be uncommented to implement the  shared-library methodology
 * @Library('shared-pipeline-library') _
 */
node {
    try {
        deleteDir()
        stage('InitFromSCM') {
            credentialsId = "ref"
            git poll: true, url: "$repo_url", branch: "$revision", credentialsId: credentialsId
            dir('shared-library') {
                git poll: true, url: "$shared_lib_url", branch: "$shared_library_revision", credentialsId: 'f8b8fb25-f003-4e36-ae8b-c9304224048d'
            }
        }
        shared_lib = load 'shared-library/src/main/groovy/commons.groovy'
        load 'config/stages/nexusPreparation.groovy'
        load 'config/stages/build.groovy'
        load 'config/stages/nexusUpload.groovy'
        load 'config/stages/tagging.groovy'
    } catch(error) {
        echo "ERROR IN PIPELINE"
        println error
        throw error
    } finally{
        //deleteDir()
    }
}
