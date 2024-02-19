## log & cloudfunction source bucket
resource "google_storage_bucket" "somaz_cdn_result_log_bucket" {

  name                        = "somaz-cdn-result-logs"
  location                    = var.region
  labels                      = local.default_labels
  uniform_bucket_level_access = true
  force_destroy               = true
  storage_class               = "STANDARD"
}

resource "null_resource" "somaz_cdn_zip_cloud_function" {
  depends_on = [google_storage_bucket.somaz_cdn_result_log_bucket]

  provisioner "local-exec" {
    command = <<EOT
      cd ./somaz-cdn-bucket-file-download
      zip -r somaz-cdn-log-function.zip main.py requirements.txt
    EOT
  }

  triggers = {
    main_py_content_hash          = filesha256("./somaz-cdn-bucket-file-download/main.py")
    requirements_txt_content_hash = filesha256("./somaz-cdn-bucket-file-download/requirements.txt")
  }
}

resource "google_storage_bucket_object" "somaz_cdn_cloud_function_archive" {
  depends_on = [null_resource.somaz_cdn_zip_cloud_function, google_storage_bucket.prod_dsp_cdn_result_log_bucket]

  name   = "source/somaz-cdn-log-function.zip"
  bucket = google_storage_bucket.somaz_cdn_result_log_bucket.name
  source = "./somaz-cdn-bucket-file-download/prod-dsp-cdn-log-function.zip"
}

resource "google_cloudfunctions_function" "somaz_cdn_log_processor_function" {
  depends_on = [
    null_resource.somaz_cdn_zip_cloud_function,
    google_storage_bucket_object.somaz_cdn_cloud_function_archive,
    google_storage_bucket.somaz_cdn_result_log_bucket
  ]

  name                  = "somaz-cdn-log-processor-function"
  description           = "Save Download Log Data from somaz.cdn.luxon.games"
  available_memory_mb   = 512
  runtime               = "python39"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  source_archive_bucket = google_storage_bucket.somaz_cdn_result_log_bucket.name
  source_archive_object = google_storage_bucket_object.somaz_cdn_cloud_function_archive.name
  entry_point           = "retrieve_and_save_logs"
  trigger_http          = true

  environment_variables = {
    LOG_STORAGE_BUCKET = "somaz-cdn-result-logs"
    GCP_PROJECT = "somaz-bigquery"
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "somaz_cdn_job" {
  depends_on = [google_cloudfunctions_function.somaz_cdn_log_processor_function]

  name      = "somaz-cdn-daliy-job"
  region    = var.region
  schedule  = "5 10 * * *" # Daily 10:05 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.somaz_cdn_log_processor_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

