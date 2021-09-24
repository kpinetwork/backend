output "vpc_kpinetworks_id" {
    value       = aws_vpc.kpinetworks_vpc.id
}

output "private_subnet_ids" {
    value       = [aws_subnet.private_subnet_a.id, aws_subnet.private_subnet_b.id]
}

output "public_subnet_id" {
    value       = aws_subnet.public_subnet_a.id
}

output "security_group" {
    value       = {
        id   :  aws_security_group.kpinetworks_group.id
        arn  :  aws_security_group.kpinetworks_group.arn
        tags :  aws_security_group.kpinetworks_group.tags_all
    }
}

output "security_group_lambda" {
    value       = {
        id   :  aws_security_group.kpinetworks_group_lambda.id
        arn  :  aws_security_group.kpinetworks_group_lambda.arn
        tags :  aws_security_group.kpinetworks_group_lambda.tags_all
    }
}