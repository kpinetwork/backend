output "kpinetwork_db_hostname" {
  description = "KPI Network RDS instance hostname"
  value       = aws_db_instance.kpinetwork_db.address
  sensitive   = true
}

output "kpinetwork_db_port" {
  description = " KPI Network RDS instance port"
  value       = aws_db_instance.kpinetwork_db.port
  sensitive   = true
}

output "kpinetwork_db_username" {
  description = "KPI Network RDS instance root username"
  value       = aws_db_instance.kpinetwork_db.username
  sensitive   = true
}

output "kpinetwork_db_host" {
  description = "KPI Network RDS host"
  value       = aws_db_instance.kpinetwork_db.address
  sensitive   = true
}

output "kpinetwork_db_name" {
  description = "KPI Network RDS name"
  value       = aws_db_instance.kpinetwork_db.name
}