variable "project_name" {
  description = "Project name prefix"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
  default     = "10.0.10.0/24"
}

variable "private_subnet_a_cidr" {
  description = "CIDR block for private subnet A"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_b_cidr" {
  description = "CIDR block for private subnet B"
  type        = string
  default     = "10.0.2.0/24"
}

variable "az_a" {
  description = "Availability zone A"
  type        = string
  default     = "us-east-1a"
}

variable "az_b" {
  description = "Availability zone B"
  type        = string
  default     = "us-east-1b"
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}