/*
 * Below annotation can be uncommented to implement the  shared-library methodology
 * @Library('shared-pipeline-library') _
 */
node {
    try {
        deleteDir()
        buildUser = env.BUILD_USER
        buildUserEmail = env.BUILD_USER_EMAIL
        WORKSPACE = env.WORKSPACE
        oldTagName = "$Revision"
        newTagName = oldTagName.replace("sqa", "uat")
        stage('InitFromSCM') {
            credentialsId = "ref"
            git poll: true, url: "$repo_url",  branch: "release/sqa", credentialsId: credentialsId
        }
        sh "cd $WORKSPACE"
        git_code_repo =  repo_url.split("@")[1]
        git_shared_repo = shared_lib_url.split("@")[1]
        withCredentials([[$class: 'UsernamePasswordMultiBinding',
                          credentialsId: "ref",
                          usernameVariable: 'GIT_USERNAME',
                          passwordVariable: 'GIT_PASSWORD']]) {
            sh("git config --local user.email $buildUserEmail")
            sh("git config --local user.name $buildUser")
            sh("git config --local http.sslVerify false")
            sh("git tag $newTagName $oldTagName")
            sh("git push https://${GIT_USERNAME}:${GIT_PASSWORD}@${git_code_repo} --tags")
            sh("git push https://${GIT_USERNAME}:${GIT_PASSWORD}@${git_shared_repo} --tags")
        }
    } catch(error) {
        echo "ERROR IN PIPELINE"
        println error
        throw error
    } finally{
        deleteDir()
    }
}
