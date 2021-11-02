resource "aws_codebuild_source_credential" "git_credential" {
    auth_type              = "PERSONAL_ACCESS_TOKEN"
    server_type            = "GITHUB"
    token                  = var.git_token
}

resource "aws_codebuild_project" "rds_migrations" {
    name                   = "${var.environment}_${var.codebuild_project_name}"
    description            = "code build project for db migrations"
    build_timeout          = 30

    service_role  = var.codebuild_aws_iam_role
    
    artifacts {
        type                = "NO_ARTIFACTS"
    }

    cache {
        type                = "NO_CACHE"
    }

    environment {
        compute_type                = "BUILD_GENERAL1_SMALL"
        image                       = "aws/codebuild/standard:4.0"
        type                        = "LINUX_CONTAINER"
        image_pull_credentials_type = "CODEBUILD"

        environment_variable {
            name            = "DB_NAME"
            value           = var.db_name
        }

        environment_variable {
            name            = "DB_USERNAME"
            value           = var.db_username
        }

        environment_variable {
            name            = "DB_PASSWORD"
            value           = var.db_password
        }

        environment_variable {
            name            = "DB_HOST"
            value           = var.db_host
        }
    }

    source {
        type                = "GITHUB"
        location            = var.repository
        git_clone_depth     = 1

        git_submodules_config {
            fetch_submodules = false
        }

        report_build_status = false
        insecure_ssl        = false
    }

    vpc_config {
        vpc_id = var.kpinetwork_vpc_id

        subnets = [
            var.private_subnet_a_id
        ]

        security_group_ids = [
            var.codebuild_group_id
        ]
    }

    logs_config {
        cloudwatch_logs {
            group_name  = var.log_group_name
            status      = "ENABLED"
        }

        s3_logs {
            status   = "DISABLED"
        }
    }

    tags    = {
        Name    = "${var.environment}_${var.codebuild_project_name}"
    }

}