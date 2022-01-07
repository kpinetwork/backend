# ----------------------------------------------------------------------------------------------------------------------
# CREATE USER POOL 
# @param alias_attributes Attributes supported as an alias for the user pool. Valid values: phone_number, email, or preferred_username
# @param generate_secret Should an application secret be generated.
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# USER POOL
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_cognito_user_pool" "pool" {
  name = "${var.environment}_pool"
  username_attributes = ["email"]
  auto_verified_attributes = ["email"]
  
  lambda_config {
  post_confirmation = var.lambda_trigger_arn
  }

}

# ----------------------------------------------------------------------------------------------------------------------
# USER GROUPS
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_cognito_user_group" "admin" {
  name         = "${var.environment}_admin_group"
  user_pool_id = aws_cognito_user_pool.pool.id
  description  = "Administrator group"
}

resource "aws_cognito_user_group" "customer" {
  name         = "${var.environment}_customer_group"
  user_pool_id = aws_cognito_user_pool.pool.id
  description  = "Customer group"
}

# ----------------------------------------------------------------------------------------------------------------------
# CLIENTS
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_cognito_user_pool_client" "amplify" {
  name = "${var.environment}-amplify"
  user_pool_id = aws_cognito_user_pool.pool.id
  generate_secret = false
  refresh_token_validity = 10
}

# ----------------------------------------------------------------------------------------------------------------------
# LAMBDA TRIGGER PERMISSION
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_lambda_permission" "allow_post_confirmation_from_user_pool" {
  statement_id = "AllowPostConfirmationFromUserPool"
  action = "lambda:InvokeFunction"
  function_name = var.lambda_trigger_arn
  principal = "cognito-idp.amazonaws.com"
  source_arn = aws_cognito_user_pool.pool.arn
}