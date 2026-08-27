variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.medium" # Using t3.medium as docker + models need some RAM
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
  default     = "my-aws-key"
}
