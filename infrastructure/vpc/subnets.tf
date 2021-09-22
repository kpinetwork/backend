resource "aws_subnet" "private_subnet_a"{
    vpc_id                 = aws_vpc.kpinetworks_vpc.id
    
    cidr_block             = "10.0.1.0/24"
    availability_zone      = "${var.region}a"
    
    tags = {
        Name               = "private-subnet-${var.region}a"

    }
}

resource "aws_subnet" "private_subnet_b"{
    vpc_id                 = aws_vpc.kpinetworks_vpc.id
    
    cidr_block             = "10.0.2.0/24"
    availability_zone      = "${var.region}b"
    
    tags = {
        Name               = "private-subnet-${var.region}b"

    }
}