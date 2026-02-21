variable "container_name" {
  description = "Value of the name for the Docker container"
  type        = string
  default     = "terraform-tutorial"
}

variable "external_port" {
  description = "External port for the container"
  type        = number
  default     = 8000
}
