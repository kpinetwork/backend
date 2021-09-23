resource "aws_vpc" "kpinetworks_vpc" {
    cidr_block             = "10.0.0.0/16"

    tags    =  {
        Name               = var.vpc_name
    }
}