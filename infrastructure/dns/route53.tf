# Example DNS record using Route53.
# Route53 is not specifically required; any DNS host can be used.
resource "aws_route53_record" "kpinetwork_domain" {
  zone_id = var.hosted_zone_id

  name = var.domain_name
  type = "A"

  alias {
    name                   = var.api_gateway_domain.cloudfront_domain_name
    zone_id                = var.api_gateway_domain.cloudfront_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "cert_validations" {
  count = length(var.cert_sans) + 1
  zone_id = var.hosted_zone_id
  allow_overwrite = true
  name    = element(var.domain_certificates.cert.domain_validation_options.*.resource_record_name, count.index)
  type    = element(var.domain_certificates.cert.domain_validation_options.*.resource_record_type, count.index)
  records = [element(var.domain_certificates.cert.domain_validation_options.*.resource_record_value, count.index)]
  ttl     = 60
}