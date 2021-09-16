module "buckets" {
  source = "./buckets/"
}

module "functions" {
  source = "./functions/"
  minimal_lambda_function_bucket = module.buckets.minimal_function_bucket
  sample_lambda_function_bucket = module.buckets.sample_function_bucket
  minimal_lambda_function_exec_role_arn = module.policy.lambda_exec_role_arn
  lambdas_names = var.lambdas_names
}

module "policy" {
  source = "./policy/"
  region = var.region
  account_id = var.aws_account_id
  lambdas_names = var.lambdas_names
  api_gateway_minimal_lambda_function = module.network.api_gateway_minimal_lambda_function
  api_gateway_sample_lambda_function = module.network.api_gateway_sample_lambda_function
}

module "logs" {
  source = "./logs/"
  lambdas_names = var.lambdas_names
}

module "network" {
  source = "./network/"
  lambdas_functions_arn = module.functions.lambdas_invoke_arns
}