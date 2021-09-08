# ----------------------------------------------------------------------------------------------------------------------
# DYNAMODB
# @param name The name of bdd
# @param read_capacity RCU
# @param write_capacity WCU
# ----------------------------------------------------------------------------------------------------------------------

# This table is required to keep lock version of terraform
resource "aws_dynamodb_table" "terraform-state" {
  name = "terraform-state"
  read_capacity = 20
  write_capacity = 20
  hash_key = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}