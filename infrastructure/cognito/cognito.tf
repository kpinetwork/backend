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
  alias_attributes = ["email"]
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

resource "aws_cognito_user_pool_client" "client" {
  name = "${var.environment}-client"
  user_pool_id = aws_cognito_user_pool.pool.id
  generate_secret = false
  
  token_validity_units {
     access_token  = "hours"
     id_token      = "hours"
     refresh_token = "minutes"
     // valid values: seconds | minutes | hours | days
  }

  refresh_token_validity = 60
}