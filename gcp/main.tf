# LetsGetCrypto Google Cloud Platform Infrastructure
# Terraform configuration for deploying to GCP Cloud Run with Cloud SQL

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for deployment"
  type        = string
  default     = "us-central1"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "letsgetcrypto"
}

variable "db_tier" {
  description = "Cloud SQL database tier"
  type        = string
  default     = "db-f1-micro"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "django_secret_key" {
  description = "Django secret key"
  type        = string
  sensitive   = true
}

variable "container_image" {
  description = "Container image URL (format: gcr.io/PROJECT_ID/letsgetcrypto:latest)"
  type        = string
  default     = ""  # Will be set from project_id if not provided
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

# Local values
locals {
  container_image = var.container_image != "" ? var.container_image : "gcr.io/${var.project_id}/${var.app_name}:latest"
}

# Enable required APIs
resource "google_project_service" "compute" {
  service            = "compute.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "sql" {
  service            = "sqladmin.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "vpcaccess" {
  service            = "vpcaccess.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudresourcemanager" {
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}

# VPC Network
resource "google_compute_network" "vpc_network" {
  name                    = "${var.app_name}-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.compute]
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.app_name}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  network       = google_compute_network.vpc_network.id
  region        = var.region
}

# VPC Access Connector for Cloud Run to Cloud SQL
resource "google_vpc_access_connector" "connector" {
  name          = "${var.app_name}-connector"
  region        = var.region
  network       = google_compute_network.vpc_network.name
  ip_cidr_range = "10.8.0.0/28"
  depends_on    = [google_project_service.vpcaccess]
}

# Cloud SQL PostgreSQL Instance
resource "google_sql_database_instance" "postgres" {
  name             = "${var.app_name}-db-instance"
  database_version = "POSTGRES_14"
  region           = var.region
  depends_on       = [google_project_service.sql]

  settings {
    tier              = var.db_tier
    availability_type = "ZONAL"
    disk_size         = 10
    disk_type         = "PD_SSD"

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = false
      backup_retention_settings {
        retained_backups = 7
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc_network.id
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }

  deletion_protection = false
}

# Database
resource "google_sql_database" "database" {
  name     = var.app_name
  instance = google_sql_database_instance.postgres.name
}

# Database User
resource "google_sql_user" "db_user" {
  name     = "postgres"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

# Secret Manager - Django Secret Key
resource "google_secret_manager_secret" "django_secret" {
  secret_id = "${var.app_name}-django-secret"
  depends_on = [google_project_service.secretmanager]

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "django_secret_version" {
  secret      = google_secret_manager_secret.django_secret.id
  secret_data = var.django_secret_key
}

# Secret Manager - Database Password
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${var.app_name}-db-password"
  depends_on = [google_project_service.secretmanager]

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password_version" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = var.db_password
}

# Cloud Run Service
resource "google_cloud_run_service" "app" {
  name     = var.app_name
  location = var.region
  depends_on = [
    google_project_service.run,
    google_sql_database_instance.postgres
  ]

  template {
    spec {
      containers {
        image = local.container_image

        env {
          name  = "DJANGO_DEBUG"
          value = "False"
        }

        env {
          name  = "DJANGO_ALLOWED_HOSTS"
          value = "*"
        }

        env {
          name = "DJANGO_SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.django_secret.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "DATABASE_URL"
          # Use Cloud SQL Unix socket connection without exposing password in environment
          value = "postgres://postgres@/${var.app_name}?host=/cloudsql/${google_sql_database_instance.postgres.connection_name}"
        }

        env {
          name = "DB_PASSWORD"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_password.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "DJANGO_LOG_LEVEL"
          value = "INFO"
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        ports {
          container_port = 8000
        }
      }

      # Connect to Cloud SQL via Unix socket
      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"         = var.min_instances
        "autoscaling.knative.dev/maxScale"         = var.max_instances
        "run.googleapis.com/cloudsql-instances"    = google_sql_database_instance.postgres.connection_name
        "run.googleapis.com/vpc-access-connector"  = google_vpc_access_connector.connector.id
        "run.googleapis.com/vpc-access-egress"     = "all-traffic"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access to Cloud Run service
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.app.name
  location = google_cloud_run_service.app.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "service_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_service.app.status[0].url
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.postgres.connection_name
}

output "database_ip" {
  description = "Cloud SQL private IP"
  value       = google_sql_database_instance.postgres.private_ip_address
}

output "vpc_connector" {
  description = "VPC Access Connector name"
  value       = google_vpc_access_connector.connector.name
}
