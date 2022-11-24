resource "aws_db_subnet_group" "kpinetwork" {
  name                   = local.db_subnet_group_name
  subnet_ids             = var.subnet_ids

  tags                   = {
    Name                 = local.db_subnet_group_name
  }
}

resource "aws_db_instance" "kpinetwork_db" {
  identifier             = local.db_identifier
  allocated_storage      = 5

  instance_class         = local.db_instance[var.environment]
  engine                 = "postgres"
  engine_version         = "13.7"
  port                   = "5432"

  db_subnet_group_name   = aws_db_subnet_group.kpinetwork.name
  vpc_security_group_ids = [var.db_security_group.id]

  availability_zone      = "${var.region}a"
  skip_final_snapshot    = true

  username               = var.db_username
  password               = var.db_password
  name                   = local.db_name

  storage_encrypted      = true

  depends_on = [
    aws_db_subnet_group.kpinetwork
  ]
}