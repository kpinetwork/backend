data "terraform_remote_state" "infrastructure_state" {
  backend   = var.backend
  config    = var.remote_state_config
}