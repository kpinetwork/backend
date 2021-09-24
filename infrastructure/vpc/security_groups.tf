resource "aws_security_group" "kpinetworks_group" {
     name                   = var.security_group_name
     vpc_id                 = aws_vpc.kpinetworks_vpc.id

     ingress                = [
         {
             description    = "TCP"
             from_port      = 5432
             to_port        = 5432
             protocol       = "tcp"
             cidr_blocks    = ["0.0.0.0/0"]
             ipv6_cidr_blocks = []
             prefix_list_ids  = []
             security_groups  = []
             self             = false
         }
     ]

     egress                 = [
         {
             description    = "TCP"
             from_port      = 5432
             to_port        = 5432
             protocol       = "tcp"
             cidr_blocks    = ["0.0.0.0/0"]
             ipv6_cidr_blocks = ["::/0"]
             prefix_list_ids  = []
             security_groups  = []
             self             = false
         }
     ]

     tags                   = {
         Name               = var.security_group_name
     }
}

resource "aws_security_group" "kpinetworks_group_lambda" {
     name                   = var.security_group_name_lambda
     vpc_id                 = aws_vpc.kpinetworks_vpc.id

     egress                 = [
         {
             description    = "ALL"
             from_port      = 0
             to_port        = 0
             protocol       = "-1"
             cidr_blocks    = ["0.0.0.0/0"]
             ipv6_cidr_blocks = ["::/0"]
             prefix_list_ids  = []
             security_groups  = []
             self             = false
         }
     ]

     tags                   = {
         Name               = var.security_group_name_lambda
     }
}