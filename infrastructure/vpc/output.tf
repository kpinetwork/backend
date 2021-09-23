output "vpc_kpinetworks_id" {
     value       = aws_vpc.kpinetworks_vpc.id
 }

 output "private_subnet_ids" {
     value       = [aws_subnet.private_subnet_a.id, aws_subnet.private_subnet_b.id]
 }

 output "security_group" {
     value       = {
         id   :  aws_security_group.kpinetworks_group.id
         arn  :  aws_security_group.kpinetworks_group.arn
         tags :  aws_security_group.kpinetworks_group.tags_all
     }
 }