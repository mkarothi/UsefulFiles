/*
 * Below annotation can be uncommented to implement the  shared-library methodology
 * @Library('shared-pipeline-library') _
 */

node {
    try {
        if(aws_account == 'dev') {
            stage('InitFromSCM') {
                deleteDir()
                git poll: true, url: "$repo_url", branch: "$revision", credentialsId: 'f8b8fb25-f003-4e36-ae8b-c9304224048d'
                shortCommit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim().take(6)
                dir('shared-library') {
                    git poll: true, url: "$shared_lib_url", branch: "$shared_library_revision", credentialsId: 'f8b8fb25-f003-4e36-ae8b-c9304224048d'
                }
            }
        } else {
            stage('InitFromNexus') {
                credentialsId = "tsm"
                WORKSPACE = env.WORKSPACE
                artifactId = "bundle-$Revision"+".zip"
                revision = Revision
                //Downloading the release bundle from Nexus..."
                account_name = aws_account
                if(account_name.contains("qa") || account_name.contains("qap")) nexus_releases_repo = "tsm-maven-releases" else nexus_releases_repo = "test-releases"
                nexus_url = "https://repo.dtcc.com/repository"
                downloadGroupId = "com/dtcc/ref/bundle"
                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: credentialsId,
                                  usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                    sh "curl --cacert /apps/cloudbees-je/ssl/repo.dtcc.com.crt -u ${env.USERNAME}:${env.PASSWORD} $nexus_url/$nexus_releases_repo/$downloadGroupId/$Revision/$artifactId>$artifactId"
                }
                // Unzip Nexus artifacts
                unzipPath = "$WORKSPACE/unzip"
                echo artifactId
                sh "mkdir -p $unzipPath && unzip -d $unzipPath $artifactId"
                sh "cp -R $unzipPath/config  $WORKSPACE"
                sh "cp -R $unzipPath/rds-migrations $WORKSPACE"
                sh "cp -R $unzipPath/shared-library $WORKSPACE"
                //sh "mkdir -p $WORKSPACE/beanstalk-lambda/hello-world-beanstalk/src &&  cp -R $unzipPath/.ebextensions  $WORKSPACE/beanstalk-lambda/hello-world-beanstalk/src"
            }
        }
        shared_lib = load 'shared-library/src/main/groovy/commons.groovy'
        load 'config/stages/preparation.groovy'
        load 'config/stages/deprovision.groovy'

    } catch(error) {
        echo "ERROR IN PIPELINE"
        println error
        throw error
    } finally{
        deleteDir()
    }
}



