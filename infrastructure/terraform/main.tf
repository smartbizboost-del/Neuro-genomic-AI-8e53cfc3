# infrastructure/terraform/main.tf

# Virtual Cloud Network
resource "oci_core_vcn" "neuro_vcn" {
  compartment_id = var.compartment_id
  cidr_block     = var.vcn_cidr
  display_name   = "neuro-genomic-vcn-${var.environment}"
  dns_label      = "neurovcn"
}

# Internet Gateway
resource "oci_core_internet_gateway" "neuro_igw" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.neuro_vcn.id
  display_name   = "neuro-genomic-igw-${var.environment}"
}

# Route Table
resource "oci_core_route_table" "neuro_route" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.neuro_vcn.id
  display_name   = "neuro-genomic-route-${var.environment}"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.neuro_igw.id
  }
}

# Security List
resource "oci_core_security_list" "neuro_sl" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.neuro_vcn.id
  display_name   = "neuro-genomic-sl-${var.environment}"

  # HTTP
  ingress_security_rules {
    protocol    = "6"
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    tcp_options {
      min = 80
      max = 80
    }
  }

  # HTTPS
  ingress_security_rules {
    protocol    = "6"
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    tcp_options {
      min = 443
      max = 443
    }
  }

  # SSH
  ingress_security_rules {
    protocol    = "6"
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    tcp_options {
      min = 22
      max = 22
    }
  }

  # API
  ingress_security_rules {
    protocol    = "6"
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    tcp_options {
      min = 8000
      max = 8000
    }
  }

  # Dashboard
  ingress_security_rules {
    protocol    = "6"
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    tcp_options {
      min = 8501
      max = 8501
    }
  }

  # Allow all outbound
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
    destination_type = "CIDR_BLOCK"
  }
}

# Subnets
resource "oci_core_subnet" "neuro_subnet" {
  compartment_id      = var.compartment_id
  vcn_id              = oci_core_vcn.neuro_vcn.id
  cidr_block          = "10.0.1.0/24"
  display_name        = "neuro-genomic-subnet-${var.environment}"
  route_table_id      = oci_core_route_table.neuro_route.id
  security_list_ids   = [oci_core_security_list.neuro_sl.id]
  dhcp_options_id     = oci_core_vcn.neuro_vcn.default_dhcp_options_id
}

# MySQL Database (HeatWave)
resource "oci_mysql_mysql_db_system" "neuro_db" {
  compartment_id           = var.compartment_id
  display_name             = "neuro-genomic-db-${var.environment}"
  availability_domain      = data.oci_identity_availability_domains.ads.availability_domains[0].name
  subnet_id                = oci_core_subnet.neuro_subnet.id
  mysql_version            = "8.0"
  shape_name               = "MySQL.VM.Standard.E3.1.8GB"

  data_storage_size_in_gb  = 50

  backup_policy {
    retention_in_days = 30
    window_start_time = "00:00"
  }

  maintenance {
    window_start_time = "SUN 02:00"
  }

  configuration_id = oci_mysql_configuration.mysql_config.id
}

resource "oci_mysql_configuration" "mysql_config" {
  compartment_id = var.compartment_id
  display_name   = "neuro-genomic-mysql-config"
  shape_name     = "MySQL.VM.Standard.E3.1.8GB"
  description    = "MySQL Configuration for Neuro-Genomic AI"
  variables {
    innodb_buffer_pool_size = 2147483648
    max_connections         = 500
    max_allowed_packet      = 67108864
  }
}

# Object Storage Bucket
resource "oci_objectstorage_bucket" "neuro_bucket" {
  compartment_id = var.compartment_id
  namespace      = data.oci_objectstorage_namespace.ns.namespace
  name           = "neuro-genomic-ecg-${var.environment}"
  access_type    = "NoPublicAccess"
  storage_tier   = "Standard"
  versioning     = "Enabled"
}

data "oci_objectstorage_namespace" "ns" {
  compartment_id = var.compartment_id
}

# Container Registry (OCIR)
resource "oci_artifacts_container_repository" "neuro_registry" {
  compartment_id = var.compartment_id
  display_name   = "neuro-genomic-${var.environment}"
  is_public      = false
}

# Kubernetes Cluster (OKE)
resource "oci_containerengine_cluster" "neuro_cluster" {
  compartment_id     = var.compartment_id
  name               = "neuro-genomic-cluster-${var.environment}"
  kubernetes_version = "v1.28.0"
  vcn_id             = oci_core_vcn.neuro_vcn.id

  options {
    add_ons {
      is_kubernetes_dashboard_enabled = false
      is_tiller_enabled               = false
    }

    kubernetes_network_config {
      pods_cidr     = "10.244.0.0/16"
      services_cidr = "10.96.0.0/16"
    }

    service_lb_subnet_ids = [oci_core_subnet.neuro_subnet.id]
  }
}

resource "oci_containerengine_node_pool" "neuro_node_pool" {
  cluster_id         = oci_containerengine_cluster.neuro_cluster.id
  compartment_id     = var.compartment_id
  name               = "neuro-genomic-nodepool-${var.environment}"
  kubernetes_version = "v1.28.0"
  node_shape         = "VM.Standard.E3.Flex"
  node_shape_config {
    memory_in_gbs = 16
    ocpus         = 2
  }

  node_config_details {
    size          = 3
    placement_configs {
      availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
      subnet_id          = oci_core_subnet.neuro_subnet.id
    }
  }

  node_source_details {
    source_type             = "IMAGE"
    image_id                = data.oci_core_images.node_images.images[0].id
    boot_volume_size_in_gbs = 100
  }
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

data "oci_core_images" "node_images" {
  compartment_id           = var.compartment_id
  operating_system         = "Oracle Linux"
  operating_system_version = "8"
  shape                    = "VM.Standard.E3.Flex"
}