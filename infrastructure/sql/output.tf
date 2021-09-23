output "kpinetworks_db_hostname" {
   description = "KPI Networks RDS instance hostname"
   value       = aws_db_instance.kpinetworks_db.address
   sensitive   = true
 }

 output "kpinetworks_db_port" {
   description = " KPI Networks RDS instance port"
   value       = aws_db_instance.kpinetworks_db.port
   sensitive   = true
 }

 output "kpinetworks_db_username" {
   description = "KPI Networks RDS instance root username"
   value       = aws_db_instance.kpinetworks_db.username
   sensitive   = true
 }