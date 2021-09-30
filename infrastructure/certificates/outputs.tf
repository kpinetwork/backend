output "domain_certificate" {
  value = {
    arn = aws_acm_certificate.cert.arn
    cert = aws_acm_certificate.cert
  }
}

output "certificate_validation_arn" {
  value = aws_acm_certificate_validation.cert.certificate_arn
}
