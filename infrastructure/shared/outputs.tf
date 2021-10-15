output "resources" {
  value = data.terraform_remote_state.infrastructure_state.outputs
}
