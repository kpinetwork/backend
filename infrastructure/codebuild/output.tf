output "codebuild_project" {
    value = {
        "id" : aws_codebuild_project.rds_migrations.id
        "arn": aws_codebuild_project.rds_migrations.arn
        "name": aws_codebuild_project.rds_migrations.tags_all.Name
    }
}