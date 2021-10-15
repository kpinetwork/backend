output "kpinetwork_db_hostname" {
  description = "KPI Networks RDS instance hostname"
  value       = aws_db_instance.kpinetwork_db.address
  sensitive   = true
}

output "kpinetwork_db_port" {
  description = " KPI Networks RDS instance port"
  value       = aws_db_instance.kpinetwork_db.port
  sensitive   = true
}

output "kpinetwork_db_username" {
  description = "KPI Networks RDS instance root username"
  value       = aws_db_instance.kpinetwork_db.username
  sensitive   = true
}

output "kpinetwork_db_host" {
  description = "KPI Networks RDS host"
  value       = aws_db_instance.kpinetwork_db.address
  sensitive   = true
}