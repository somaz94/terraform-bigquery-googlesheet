## bigquery  -> googlesheet workflow tier badge data
resource "null_resource" "bigquery_sheet_zip_tier_badge_monthly_cloudfunction" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./bigquery-to-sheet-tier-badge-monthly
      zip -r bigquery-to-sheet-tier-badge-monthly.zip main.py requirements.txt bigquery-luxon.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./bigquery-to-sheet-tier-badge-monthly/main.py")
    requirements_content_hash = filesha256("./bigquery-to-sheet-tier-badge-monthly/requirements.txt")
    json_content_hash         = filesha256("./bigquery-to-sheet-tier-badge-monthly/bigquery-luxon.json")
  }
}

resource "google_storage_bucket_object" "bigquery_sheet_tier_badge_monthly_cloudfunction_archive" {
  depends_on = [null_resource.bigquery_sheet_zip_tier_badge_monthly_cloudfunction]

  name   = "source/bigquery-to-sheet-tier-badge-monthly.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./bigquery-to-sheet-tier-badge-monthly/bigquery-to-sheet-tier-badge-monthly.zip"
}


## cloud_function
resource "google_cloudfunctions_function" "bigquery_sheet_tier_badge_monthly_function" {
  depends_on = [null_resource.bigquery_sheet_zip_tier_badge_monthly_cloudfunction, google_storage_bucket_object.bigquery_sheet_tier_badge_monthly_cloudfunction_archive]

  name                  = "bigquery-to-sheet-tier-badge-monthly"
  description           = "Sync data from BigQuery to Google Sheets"
  available_memory_mb   = 256
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  # Set the source_directory property here.
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.bigquery_sheet_tier_badge_monthly_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "update_kpi_table_pack" # Function name in Python code

  environment_variables = {
    SHEET_ID = ""
  }
}


## cloud_scheduler
resource "google_cloud_scheduler_job" "bigquery_sheet_tier_badge_monthly_job" {
  depends_on = [google_cloudfunctions_function.bigquery_sheet_tier_badge_monthly_function]

  name      = "bigquery-to-sheet-tier-badge-monthly-job"
  region    = var.region
  schedule  = "40 10 1 * *" # 매월 1일 10:40 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.bigquery_sheet_tier_badge_monthly_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

