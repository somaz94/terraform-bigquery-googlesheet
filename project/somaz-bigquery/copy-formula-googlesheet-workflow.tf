## copy formula googlesheet workflow
resource "null_resource" "copy_formula_sheet_zip_cloudfunction" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./copy-formula-to-sheet
      zip -r copy-formula-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./copy-formula-to-sheet/main.py")
    requirements_content_hash = filesha256("./copy-formula-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./copy-formula-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "copy_formula_sheet_cloudfunction_archive" {
  depends_on = [null_resource.copy_formula_sheet_zip_cloudfunction]

  name   = "source/copy-formula-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./copy-formula-to-sheet/copy-formula-to-sheet.zip"
}


## cloud_function
resource "google_cloudfunctions_function" "copy_formula_sheet_function" {
  depends_on = [null_resource.copy_formula_sheet_zip_cloudfunction, google_storage_bucket_object.copy_formula_sheet_cloudfunction_archive]

  name                  = "copy-formula-to-sheet"
  description           = "Sync data from Matic Value to Google Sheets"
  available_memory_mb   = 512
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  # Set the source_directory property here.
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.copy_formula_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "propagate_formulas" # Function name in Python code

  environment_variables = {
    SHEET_ID = "" # Replace with your Google Sheet ID
  }
}


## cloud_scheduler
resource "google_cloud_scheduler_job" "copy_formula_sheet_job" {
  depends_on = [google_cloudfunctions_function.copy_formula_sheet_function]

  name      = "copy-formula-to-sheet-daliy-job"
  region    = var.region
  schedule  = "50 9 * * *" # Daily 09:00 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.copy_formula_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}


