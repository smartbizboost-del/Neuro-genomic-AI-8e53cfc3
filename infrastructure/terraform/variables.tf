# infrastructure/terraform/variables.tf
variable "tenancy_ocid" {
  description = "OCI Tenancy OCID"
  type        = string
  sensitive   = true
}

variable "user_ocid" {
  description = "OCI User OCID"
  type        = string
  sensitive   = true
}

variable "fingerprint" {
  description = "API Key Fingerprint"
  type        = string
  sensitive   = true
}

variable "private_key_path" {
  description = "Path to private key"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "OCI Region"
  type        = string
  default     = "us-ashburn-1"
}

variable "compartment_id" {
  description = "Compartment OCID"
  type        = string
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
  default     = "dev"
}

variable "vcn_cidr" {
  description = "VCN CIDR Block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_domain" {
  description = "Availability Domain"
  type        = string
  default     = "1"
}