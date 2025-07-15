output "ec2_public_ip" {
  value = aws_instance.rag_ec2.public_ip
}

output "app_url" {
  value = "http://${aws_instance.rag_ec2.public_dns}:80"
}
