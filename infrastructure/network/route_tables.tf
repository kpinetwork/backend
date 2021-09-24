resource "aws_route_table" "kpinetworks_rt_public" {
    vpc_id          = var.kpinetworks_vpc_id
    route           = [
        {
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_internet_gateway.igw_kpinetworks.id
            instance_id                 = ""
            ipv6_cidr_block             = ""
            egress_only_gateway_id      = ""
            nat_gateway_id              = ""
            network_interface_id        = ""
            transit_gateway_id          = ""
            vpc_peering_connection_id   = ""
            carrier_gateway_id          = ""
            local_gateway_id            = ""
            destination_prefix_list_id  = ""
            vpc_endpoint_id             = ""
        }
    ]

}

resource "aws_route_table_association" "public_a_subnet" {
    subnet_id       = var.kpinetworks_public_subnet_a_id
    route_table_id  = aws_route_table.kpinetworks_rt_public.id
}

resource "aws_route_table" "kpinetworks_rt_private" {
    vpc_id          = var.kpinetworks_vpc_id
    route           = [
        {
            cidr_block = "0.0.0.0/0"
            gateway_id = aws_nat_gateway.nat_kpinetworks.id
            instance_id                 = ""
            ipv6_cidr_block             = ""
            egress_only_gateway_id      = ""
            nat_gateway_id              = ""
            network_interface_id        = ""
            transit_gateway_id          = ""
            vpc_peering_connection_id   = ""
            carrier_gateway_id          = ""
            local_gateway_id            = ""
            destination_prefix_list_id  = ""
            vpc_endpoint_id             = ""
        }
    ]
}

resource "aws_route_table_association" "private_a_subnet" {
    subnet_id       = var.kpinetworks_private_subnet_a_id
    route_table_id  = aws_route_table.kpinetworks_rt_private.id
}