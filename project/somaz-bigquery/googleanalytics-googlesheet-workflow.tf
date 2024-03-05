## googleanalytics  -> googlesheet workflow (New Web Visitors)
resource "null_resource" "analytics_sheet_new_web_visitors_zip_cloudfunction" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./cloud-functions/analytics-to-sheet-new-web-visitors
      zip -r analytics-to-sheet-new-web-visitors.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./cloud-functions/analytics-to-sheet-new-web-visitors/main.py")
    requirements_content_hash = filesha256("./cloud-functions/analytics-to-sheet-new-web-visitors/requirements.txt")
    json_content_hash         = filesha256("./cloud-functions/analytics-to-sheet-new-web-visitors/bigquery.json")
  }
}

resource "google_storage_bucket_object" "analytics_sheet_new_web_visitors_cloudfunction_archive" {
  depends_on = [null_resource.analytics_sheet_new_web_visitors_zip_cloudfunction]

  name   = "source/analytics-to-sheet-new-web-visitors.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./cloud-functions/analytics-to-sheet-new-web-visitors/analytics-to-sheet-new-web-visitors.zip"
}


## cloud_function
resource "google_cloudfunctions_function" "analytics_sheet_new_web_visitors_function" {
  depends_on = [null_resource.analytics_sheet_new_web_visitors_zip_cloudfunction, google_storage_bucket_object.analytics_sheet_new_web_visitors_cloudfunction_archive]

  name                  = "analytics-to-sheet-new-web-visitors"
  description           = "Sync data from New Web Vistors Value to Google Sheets"
  available_memory_mb   = 512
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  # Set the source_directory property here.
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.analytics_sheet_new_web_visitors_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "update_analytics_data_in_sheets" # Function name in Python code

  environment_variables = {
    SHEET_ID       = ""  # Replace with your Google Sheet ID
    GA_PROPERTY_ID = ""  # Replace with your GA4 property ID
  }
}


## cloud_scheduler
resource "google_cloud_scheduler_job" "analytics_sheet_new_web_visitors_job" {
  depends_on = [google_cloudfunctions_function.analytics_sheet_new_web_visitors_function]

  name      = "analytics-to-sheet-new-web-visitors-daliy-job"
  region    = var.region
  schedule  = "30 9 * * *" # Daily 09:30 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.analytics_sheet_new_web_visitors_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

##########################################################################################################

## googleanalytics  -> googlesheet workflow (New Web Visitors by Country)
resource "null_resource" "analytics_sheet_new_web_visitors_country_zip_cloudfunction" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./cloud-functions/analytics-to-sheet-new-web-visitors-country
      zip -r analytics-to-sheet-new-web-visitors-country.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./cloud-functions/analytics-to-sheet-new-web-visitors-country/main.py")
    requirements_content_hash = filesha256("./cloud-functions/analytics-to-sheet-new-web-visitors-country/requirements.txt")
    json_content_hash         = filesha256("./cloud-functions/analytics-to-sheet-new-web-visitors-country/bigquery.json")
  }
}

resource "google_storage_bucket_object" "analytics_sheet_new_web_visitors_country_cloudfunction_archive" {
  depends_on = [null_resource.analytics_sheet_new_web_visitors_country_zip_cloudfunction]

  name   = "source/analytics-to-sheet-new-web-visitors-country.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./cloud-functions/analytics-to-sheet-new-web-visitors-country/analytics-to-sheet-new-web-visitors-country.zip"
}


## cloud_function
resource "google_cloudfunctions_function" "analytics_sheet_new_web_visitors_country_function" {
  depends_on = [null_resource.analytics_sheet_new_web_visitors_zip_cloudfunction, google_storage_bucket_object.analytics_sheet_new_web_visitors_cloudfunction_archive]

  name                  = "analytics-to-sheet-new-web-visitors-country"
  description           = "Sync data from New Web Vistors Value by Country to Google Sheets"
  available_memory_mb   = 512
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  # Set the source_directory property here.
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.analytics_sheet_new_web_visitors_country_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "update_analytics_data_in_sheets" # Function name in Python code

  environment_variables = {
    SHEET_ID       = ""   # Replace with your Google Sheet ID
    GA_PROPERTY_ID = ""   # Replace with your GA4 property ID
  }
}


## cloud_scheduler
resource "google_cloud_scheduler_job" "analytics_sheet_new_web_visitors_country_job" {
  depends_on = [google_cloudfunctions_function.analytics_sheet_new_web_visitors_country_function]

  name      = "analytics-to-sheet-new-web-visitors-country-daliy-job"
  region    = var.region
  schedule  = "40 9 * * *" # Daily 09:40 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.analytics_sheet_new_web_visitors_country_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}
