# ----------------------------------------------------------------------------------------------------------------------
# ACM (Amazon Certificate Manager)
# The ACM certificate resource allows requesting and management
# of certificates from the Amazon Certificate Manager.
# @param provider Credentials to execute request, always must be in us-east-1
# @param domain_name A domain name for which the certificate should be issued
# @param validation_method Which method to use for validation. DNS or EMAIL are valid
# @param lifecycle The lifecycle block and its contents are meta-arguments, available for all resource blocks regardless of type.
# @param subject_alternative_names Set of domains that should be SANs in the issued certificate (uncomment if you need to renew the certificates)
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_acm_certificate" "cert" {
  provider = aws.east
  domain_name = "api.${var.domain}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
//subject_alternative_names = var.cert_sans
}

# ----------------------------------------------------------------------------------------------------------------------
# ACM Validation (Amazon Certificate Manager)
# The ACM certificate resource allows requesting and management
# of certificates from the Amazon Certificate Manager.
# @param provider Credentials to execute request, always must be in us-east-1
# @param certificate_arn The ARN of the certificate that is being validated.
# @param validation_record_fqdns List of FQDNs that implement the validation. Only valid for DNS validation method ACM certificates
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_acm_certificate_validation" "cert" {
  provider = aws.east
  certificate_arn = aws_acm_certificate.cert.arn
  validation_record_fqdns = var.cert_validation_fqdn.*.fqdn
}