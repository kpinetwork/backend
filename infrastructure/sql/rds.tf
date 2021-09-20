resource "aws_db_instance" "kpinetworks_db" {
  identifier             = var.db_name
  allocated_storage      = 5

  instance_class         = "db.t3.small"
  engine                 = "postgres"
  engine_version         = "13.2"
  port                   = "3306"

  availability_zone      = "${var.region}a"
  skip_final_snapshot    = true

  username               = var.db_username
  password               = var.db_password
  name                   = var.db_name
}