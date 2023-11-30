## GCS Bucket

module "gcs_buckets" {
  source          = "../../modules/gcs_buckets"
  names           = keys(local.buckets_versioning)
  project_id      = var.project
  location        = var.region
  labels          = local.default_labels
  versioning      = local.buckets_versioning
  lifecycle_rules = local.lifecycle_rules
}
