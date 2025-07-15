variable "region" {
    default = "ap-south-1"
}
variable "instance_type" {
    default = "m7i-flex.large"
}

variable "key_name" {
    description = "legal-rag-assistant"
    type = string
}