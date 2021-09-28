output "codebuild_project" {
    value = {
        "id" : aws_codebuild_project.rds_migrations.id
        "arn": aws_codebuild_project.rds_migrations.arn   
    }
}

output "codebuild_webhook" {
    value = {
        "id" : aws_codebuild_webhook.rds_migrations.id
        "payload_url": aws_codebuild_webhook.rds_migrations.payload_url
    }
}