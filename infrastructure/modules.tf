module "buckets" {
  source      = "./buckets/"
  environment = local.environment
}

module "shared" {
  source              = "./shared/"
  backend             = var.backend
  remote_state_config = local.remote_state_config
}

module "functions" {
  source                   = "./functions/"
  object_bucket_references = module.buckets.object_references
  lambdas_exec_roles_arn   = module.policy.lambdas_exec_roles_arn
  lambdas_names            = var.lambdas_names
  security_group_id        = module.shared.resources.security_group_lambda.id
  public_subnet_a_id       = module.shared.resources.public_subnet_id
  environment              = local.environment
  db_host                  = module.sql.kpinetwork_db_host
  db_name                  = module.sql.kpinetwork_db_name
  db_username              = var.db_username
  db_password              = local.db_password[local.environment]
  aws_access_key_id        = var.aws_access_key_id
  aws_secret_access_key    = var.aws_secret_access_key
  bucket_files             = var.bucket_files
  region                   = var.region
  api_gateway              = module.network.api_gateway_rest_api_id
  user_pool_id             = module.cognito.id
  app_client_id            = module.cognito.amplify_client_id
  aws_account_id           = var.aws_account_id
}

module "policy" {
  source                     = "./policy/"
  region                     = var.region
  account_id                 = var.aws_account_id
  lambdas_names              = var.lambdas_names
  api_gateway_references     = module.network.api_gateway_references
  aws_iam_policy_logs_arn    = module.shared.resources.aws_iam_policy_logs_arn
  aws_iam_policy_network_arn = module.shared.resources.aws_iam_policy_network_arn
  cognito_user_pool_arn      = module.cognito.cognito_arn
  environment                = local.environment
  glue_trigger_arn           = module.functions.lambdas_arns.glue_trigger_lambda_function
  bucket_files               = var.bucket_files
}

module "logs" {
  source        = "./logs/"
  lambdas_names = var.lambdas_names
  environment   = local.environment
}

module "network" {
  source                 = "./network/"
  lambdas_functions_arn  = module.functions.lambdas_invoke_arns
  domain_name            = local.domains[local.environment]
  certificate_arn        = module.cert.certificate_validation_arn
  environment            = local.environment
  is_production          = local.is_production
  gateway_deployment     = module.gateway_deployment.gateway_deployment
  apigw_invokes_role_arn = module.policy.apigw_invokes_role_arn
}

module "gateway_deployment" {
  source            = "./gateway_deploymnet/"
  environment           = local.environment
  is_production         = local.is_production
  api_gateway_rest_api_id = module.network.api_gateway_rest_api_id
}

module "sql" {
  source            = "./sql/"
  region            = var.region
  db_username       = var.db_username
  db_password       = local.db_password[local.environment]
  db_security_group = module.shared.resources.security_group_db
  subnet_ids        = module.shared.resources.private_subnet_ids
  environment       = local.environment
  is_production     = local.is_production
}

module "codebuild" {
  source                 = "./codebuild/"
  git_token              = var.git_token
  environment            = local.environment
  codebuild_aws_iam_role = module.shared.resources.codebuild_role_arn
  log_group_name         = module.logs.codebuild_log.name
  db_host                = module.sql.kpinetwork_db_host
  db_name                = module.sql.kpinetwork_db_name
  db_username            = var.db_username
  db_password            = local.db_password[local.environment]
  kpinetwork_vpc_id      = module.shared.resources.vpc_kpinetwork_id
  private_subnet_a_id    = element(module.shared.resources.private_subnet_ids, 0)
  codebuild_group_id     = module.shared.resources.security_group_codebuild.id
}

module "dns" {
  source              = "./dns/"
  api_gateway_domain  = module.network.api_gateway_domain
  domain_name         = local.domains[local.environment]
  cert_sans           = local.cert_sans
  hosted_zone_id      = aws_route53_zone.kpinetwork.id
  domain_certificates = module.cert.domain_certificate
  is_production       = local.is_production
}

module "cert" {
  source                = "./certificates"
  cert_validation_fqdn  = module.dns.cert_validation_fqdn
  domain_name           = local.domains[local.environment]
  aws_access_key_id     = var.aws_access_key_id
  aws_secret_access_key = var.aws_secret_access_key
  cert_sans             = local.cert_sans
}

module "cognito" {
  source = "./cognito/"
  environment = local.environment
  lambda_trigger_arns = module.functions.lambda_trigger_arns
  callback_urls = local.callback_urls
  logout_urls = local.logout_urls
}