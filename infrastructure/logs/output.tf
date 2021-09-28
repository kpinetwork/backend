output "codebuild_log" {
    value = {
        "arn"  : aws_cloudwatch_log_group.codebuild_rds_migrations.arn
        "name" : aws_cloudwatch_log_group.codebuild_rds_migrations.tags_all.Name
    }
}