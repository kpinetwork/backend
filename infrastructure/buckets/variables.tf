variable "bucket_name" {
  default = "kpinetwork-backend"
}
variable "environment" {}
variable "lambda_resource_name" {
  default = "lambdas"
}

variable "lambda_layer_resource_name" {
  default = "layer"
}