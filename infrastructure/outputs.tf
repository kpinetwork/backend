output "codebuild_project_name" {
  value = module.codebuild.codebuild_project.name
}

output "region" {
  value = var.region
}