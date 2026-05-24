# infrastructure/terraform/outputs.tf
output "vcn_id" {
  value = oci_core_vcn.neuro_vcn.id
}

output "subnet_id" {
  value = oci_core_subnet.neuro_subnet.id
}

output "database_endpoint" {
  value = oci_mysql_mysql_db_system.neuro_db.ip_address
}

output "bucket_name" {
  value = oci_objectstorage_bucket.neuro_bucket.name
}

output "registry_endpoint" {
  value = oci_artifacts_container_repository.neuro_registry.name
}

output "cluster_id" {
  value = oci_containerengine_cluster.neuro_cluster.id
}

output "cluster_endpoint" {
  value = oci_containerengine_cluster.neuro_cluster.endpoints[0].kubernetes
}