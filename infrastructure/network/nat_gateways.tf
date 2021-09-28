resource "aws_internet_gateway" "igw_kpinetworks" {
    vpc_id                 = var.kpinetworks_vpc_id
    tags                   = {
        Name               = "igw-${var.tag_name}"
    }
}

resource "aws_eip" "public_eip" {
    tags                   = {
        Name               = "eip-${var.tag_name}"
    }
}

resource "aws_nat_gateway" "nat_kpinetworks" {
    allocation_id          = aws_eip.public_eip.id
    subnet_id              = var.kpinetworks_public_subnet_a_id

    tags                   = {
        Name               = "nat-${var.tag_name}"
    }

    depends_on = [
        aws_internet_gateway.igw_kpinetworks
    ]
}