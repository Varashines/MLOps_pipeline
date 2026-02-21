terraform {
  required_providers {
    podman = {
      source  = "containers/podman"
      version = "~> 0.10.0"
    }
  }
}

provider "podman" {}

resource "podman_image" "nginx" {
  name = "nginx:latest"
}

resource "podman_container" "nginx" {
  image = podman_image.nginx.name
  name  = var.container_name
  ports {
    internal = 80
    external = var.external_port
  }
}
