resource "aws_db_subnet_group" "kpinetwork" {
  name                   = local.db_subnet_group_name
  subnet_ids             = var.subnet_ids

  tags                   = {
    Name                 = local.db_subnet_group_name
  }
}

resource "aws_db_instance" "kpinetwork_db" {
  identifier             = local.db_name
  allocated_storage      = 5

  instance_class         = var.is_production? "db.t3.small" : "db.t3.micro"
  engine                 = "postgres"
  engine_version         = "13.3"
  port                   = "5432"

  db_subnet_group_name   = aws_db_subnet_group.kpinetwork.name
  vpc_security_group_ids = [var.db_security_group.id]

  availability_zone      = "${var.region}a"
  skip_final_snapshot    = true

  username               = var.db_username
  password               = var.db_password
  name                   = local.db_name

  depends_on = [
    aws_db_subnet_group.kpinetwork
  ]
}