## metic-value  -> googlesheet workflow
resource "null_resource" "matic_value_sheet_zip_cloudfunction" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./cloud-functions/matic-value-to-sheet
      zip -r matic-value-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./cloud-functions/matic-value-to-sheet/main.py")
    requirements_content_hash = filesha256("./cloud-functions/matic-value-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./cloud-functions/matic-value-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "matic_value_sheet_cloudfunction_archive" {
  depends_on = [null_resource.matic_value_sheet_zip_cloudfunction]

  name   = "source/matic-value-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./cloud-functions/matic-value-to-sheet/matic-value-to-sheet.zip"
}


## cloud_function
resource "google_cloudfunctions_function" "matic_value_sheet_function" {
  depends_on = [null_resource.matic_value_sheet_zip_cloudfunction, google_storage_bucket_object.matic_value_sheet_cloudfunction_archive]

  name                  = "matic-value-to-sheet"
  description           = "Sync data from Matic Value to Google Sheets"
  available_memory_mb   = 512
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  # Set the source_directory property here.
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.matic_value_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "update_polygon_data_in_sheets" # Function name in Python code

  environment_variables = {
    SHEET_ID = "" # Replace with your Google Sheet ID
  }
}


## cloud_scheduler
resource "google_cloud_scheduler_job" "matic_value_sheet_job" {
  depends_on = [google_cloudfunctions_function.matic_value_sheet_function]

  name      = "matic-value-to-sheet-daliy-job"
  region    = var.region
  schedule  = "0 9 * * *" # Daily 09:00 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.matic_value_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

