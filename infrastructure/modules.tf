module "buckets" {
  source = "./buckets/"
}

module "vpc" {
  source = "./vpc/"
  region = var.region
}

module "functions" {
  source = "./functions/"
  minimal_lambda_function_bucket = module.buckets.minimal_function_bucket
  db_sample_lambda_function_bucket = module.buckets.db_sample_function_bucket
  minimal_lambda_function_exec_role_arn = module.policy.lambda_exec_role_arn
  lambdas_names = var.lambdas_names
  security_group_id = module.vpc.security_group_lambda.id
  public_subnet_a_id = module.vpc.public_subnet_id
}

module "policy" {
  source = "./policy/"
  region = var.region
  account_id = var.aws_account_id
  lambdas_names = var.lambdas_names
  api_gateway_minimal_lambda_function = module.network.api_gateway_minimal_lambda_function
  private_subnet_a = element(module.vpc.private_subnet_ids,0)
}

module "logs" {
  source = "./logs/"
  lambdas_names = var.lambdas_names
}

module "network" {
  source = "./network/"
  lambdas_functions_arn = module.functions.lambdas_invoke_arns
  kpinetworks_private_subnet_a_id = element(module.vpc.private_subnet_ids,0)
  kpinetworks_public_subnet_a_id = module.vpc.public_subnet_id
  kpinetworks_vpc_id = module.vpc.vpc_kpinetworks_id
}

module "sql" {
  source = "./sql/"
  region = var.region
  db_username = var.db_username
  db_password = var.db_password
  db_security_group = module.vpc.security_group
  subnet_ids = module.vpc.private_subnet_ids
}

module "codebuild" {
  source = "./codebuild/"
  git_token = var.git_token
  codebuild_aws_iam_role = module.policy.codebuild_role_arn
  log_group_name = module.logs.codebuild_log.name
  db_host = module.sql.kpinetworks_db_host
  db_username = var.db_username
  db_password = var.db_password
  kpinetworks_vpc_id = module.vpc.vpc_kpinetworks_id
  private_subnet_a_id = element(module.vpc.private_subnet_ids,0)
  codebuild_group_id = module.vpc.security_group_codebuild.id
}