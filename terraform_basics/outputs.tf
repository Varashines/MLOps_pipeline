output "container_id" {
  description = "ID of the Podman container"
  value       = podman_container.nginx.id
}

output "image_id" {
  description = "ID of the Podman image"
  value       = podman_image.nginx.id
}

output "container_url" {
  description = "The URL to access the Nginx container"
  value       = "http://localhost:${var.external_port}"
}
