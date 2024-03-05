## bigquery  -> googlesheet workflow retention data
resource "null_resource" "bigquery_sheet_zip_retention_cloudfunction" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./cloud-functions/bigquery-to-sheet-retention
      zip -r bigquery-to-sheet-retention.zip main.py requirements.txt bigquery-dsp.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./cloud-functions/bigquery-to-sheet-retention/main.py")
    requirements_content_hash = filesha256("./cloud-functions/bigquery-to-sheet-retention/requirements.txt")
    json_content_hash         = filesha256("./cloud-functions/bigquery-to-sheet-retention/bigquery-dsp.json")
  }
}

resource "google_storage_bucket_object" "bigquery_sheet_retention_cloudfunction_archive" {
  depends_on = [null_resource.bigquery_sheet_zip_retention_cloudfunction]

  name   = "source/bigquery-to-sheet-retention.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./cloud-functions/bigquery-to-sheet-retention/bigquery-to-sheet-retention.zip"
}


## cloud_function
resource "google_cloudfunctions_function" "bigquery_sheet_retention_function" {
  depends_on = [null_resource.bigquery_sheet_zip_retention_cloudfunction, google_storage_bucket_object.bigquery_sheet_retention_cloudfunction_archive]

  name                  = "bigquery-to-sheet-retention"
  description           = "Sync data from BigQuery to Google Sheets"
  available_memory_mb   = 512
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  # Set the source_directory property here.
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.bigquery_sheet_retention_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "update_retention_datas_in_sheets" # Function name in Python code

  environment_variables = {
    SHEET_ID = "" # Replace with your Google Sheet ID
  }
}


## cloud_scheduler
resource "google_cloud_scheduler_job" "bigquery_sheet_retention_job" {
  depends_on = [google_cloudfunctions_function.bigquery_sheet_retention_function]

  name      = "bigquery-to-sheet-retention-daliy-job"
  region    = var.region
  schedule  = "0 10 * * *" # Daily 10:00 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.bigquery_sheet_retention_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

##########################################################################################################

## bigquery  -> googlesheet workflow wallet data
resource "null_resource" "bigquery_sheet_zip_wallet_cloudfunction" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./cloud-functions/bigquery-to-sheet-wallet
      zip -r bigquery-to-sheet-wallet.zip main.py requirements.txt bigquery-luxon.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./cloud-functions/bigquery-to-sheet-wallet/main.py")
    requirements_content_hash = filesha256("./cloud-functions/bigquery-to-sheet-wallet/requirements.txt")
    json_content_hash         = filesha256("./cloud-functions/bigquery-to-sheet-wallet/bigquery-luxon.json")
  }
}

resource "google_storage_bucket_object" "bigquery_sheet_wallet_cloudfunction_archive" {
  depends_on = [null_resource.bigquery_sheet_zip_wallet_cloudfunction]

  name   = "source/bigquery-to-sheet-wallet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./cloud-functions/bigquery-to-sheet-wallet/bigquery-to-sheet-wallet.zip"
}


## cloud_function
resource "google_cloudfunctions_function" "bigquery_sheet_wallet_function" {
  depends_on = [null_resource.bigquery_sheet_zip_wallet_cloudfunction, google_storage_bucket_object.bigquery_sheet_wallet_cloudfunction_archive]

  name                  = "bigquery-to-sheet-wallet"
  description           = "Sync data from BigQuery to Google Sheets"
  available_memory_mb   = 256
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  # Set the source_directory property here.
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.bigquery_sheet_wallet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "update_wallet_datas_in_sheets" # Function name in Python code

  environment_variables = {
    SHEET_ID = "" # Replace with your Google Sheet ID
  }
}


## cloud_scheduler
resource "google_cloud_scheduler_job" "bigquery_sheet_wallet_job" {
  depends_on = [google_cloudfunctions_function.bigquery_sheet_wallet_function]

  name      = "bigquery-to-sheet-wallet-daliy-job"
  region    = var.region
  schedule  = "0 10 * * *" # Daily 10:00 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.bigquery_sheet_wallet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}