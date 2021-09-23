resource "aws_db_subnet_group" "kpinetworks" {
  name                   = var.db_subnet_group_name
  subnet_ids             = var.subnet_ids

  tags                   = {
    Name                 = var.db_subnet_group_name
  }
}

resource "aws_db_instance" "kpinetworks_db" {
  identifier             = var.db_name
  allocated_storage      = 5

  instance_class         = "db.t3.small"
  engine                 = "postgres"
  engine_version         = "13.2"
  port                   = "3306"

  db_subnet_group_name   = aws_db_subnet_group.kpinetworks.name
  vpc_security_group_ids = [var.db_security_group.id]

  availability_zone      = "${var.region}a"
  skip_final_snapshot    = true

  username               = var.db_username
  password               = var.db_password
  name                   = var.db_name
}