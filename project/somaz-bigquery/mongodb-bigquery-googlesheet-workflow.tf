## Service Account ##
module "service_accounts_bigquery" {
  source       = "../../modules/service_accounts"
  project_id   = var.project
  names        = ["bigquery"]
  display_name = "bigquery"
  description  = "bigquery admin"
}

## Biguery MongoDB Dataset ##
resource "google_bigquery_dataset" "mongodb_dataset" {
  dataset_id    = "mongodb_dataset"
  friendly_name = "mongodb_dataset"
  description   = "This is a Mongodb dataset"
  location      = var.region
  labels        = local.default_labels

  access {
    role          = "OWNER"
    user_by_email = module.service_accounts_bigquery.email
  }

  access {
    role          = "OWNER"
    user_by_email = "terraform@somaz-bigquery.iam.gserviceaccount.com"
  }
}

## cloudfunction source Bucket
resource "google_storage_bucket" "cloud_function_storage" {

  name                        = "bigquery-sheet-cloud-function-storage"
  location                    = var.region
  labels                      = local.default_labels
  uniform_bucket_level_access = true
  force_destroy               = true
}

##########################################################################################################

## mongodb -> bigquery table workflow
resource "null_resource" "mongodb_bigquery_zip_cloud_function" {
  depends_on = [google_bigquery_dataset.mongodb_dataset, google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./mongodb-to-bigquery
      zip -r mongodb-to-bigquery.zip main.py requirements.txt
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./mongodb-to-bigquery/main.py")
    requirements_content_hash = filesha256("./mongodb-to-bigquery/requirements.txt")
  }
}

resource "google_storage_bucket_object" "mongodb_bigquery_cloudfunction_archive" {
  depends_on = [null_resource.mongodb_bigquery_zip_cloud_function]

  name   = "source/mongodb-to-bigquery.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./mongodb-to-bigquery/mongodb-to-bigquery.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "mongodb_bigquery_dataflow_function" {
  depends_on = [null_resource.mongodb_bigquery_zip_cloud_function, google_storage_bucket_object.mongodb_bigquery_cloudfunction_archive]

  name                  = "mongodb-to-bigquery-dataflow"
  description           = "Function to mongodb-to-bigquery the Dataflow job"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.mongodb_bigquery_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "start_dataflow"

  environment_variables = {
    PROJECT_ID            = var.project,
    REGION                = var.region,
    SHARED_VPC            = var.shared_vpc,
    SUBNET_SHARE          = var.subnet_share,
    SERVICE_ACCOUNT_EMAIL = module.service_accounts_bigquery.email
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "mongodb_bigquery_job" {
  depends_on = [google_cloudfunctions_function.mongodb_bigquery_dataflow_function]

  name      = "mongodb-to-bigquery-daily-job"
  region    = var.region
  schedule  = "20 9 * * *" # Daily 09:20 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.mongodb_bigquery_dataflow_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

##########################################################################################################

# Compress and upload source code for deduplication Cloud Function deployment
resource "null_resource" "bigquery_deduplication_zip_cloud_function" {
  depends_on = [google_bigquery_dataset.mongodb_dataset, google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./bigquery-deduplication
      zip -r bigquery-deduplication.zip main.py requirements.txt
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./bigquery-deduplication/main.py")
    requirements_content_hash = filesha256("./bigquery-deduplication/requirements.txt")
  }
}

resource "google_storage_bucket_object" "bigquery_deduplication_cloudfunction_archive" {
  depends_on = [null_resource.bigquery_deduplication_zip_cloud_function]

  name   = "source/bigquery-deduplication.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./bigquery-deduplication/bigquery-deduplication.zip"
}

# Deduplication Cloud Function Resources
resource "google_cloudfunctions_function" "bigquery_deduplication_function" {
  depends_on = [
    null_resource.bigquery_deduplication_zip_cloud_function,
    google_storage_bucket_object.bigquery_deduplication_cloudfunction_archive
  ]

  name                  = "bigquery-deduplication-function"
  description           = "Function to remove duplicates from BigQuery"
  runtime               = "python38"
  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.bigquery_deduplication_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "remove_duplicates"
  timeout               = 540

  service_account_email = module.service_accounts_bigquery.email

  environment_variables = {
    PROJECT_ID = var.project
  }
}

# Deduplication Cloud Scheduler Task Resources
resource "google_cloud_scheduler_job" "bigquery_remove_duplicates_job" {
  depends_on = [google_cloudfunctions_function.bigquery_deduplication_function]

  name      = "bigquery-remove-duplicates-daily-job"
  region    = var.region
  schedule  = "50 9 * * *" # Daily 10:00 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "GET"
    uri         = google_cloudfunctions_function.bigquery_deduplication_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

##########################################################################################################

## bigquery table  -> googlesheet workflow simple data
resource "null_resource" "bigquery_sheet_zip_simple_cloudfunction" {
  depends_on = [google_bigquery_dataset.mongodb_dataset, google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./bigquery-to-sheet-simple
      zip -r bigquery-to-sheet-simple.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./bigquery-to-sheet-simple/main.py")
    requirements_content_hash = filesha256("./bigquery-to-sheet-simple/requirements.txt")
    json_content_hash         = filesha256("./bigquery-to-sheet-simple/bigquery.json")
  }
}

resource "google_storage_bucket_object" "bigquery_sheet_simple_cloudfunction_archive" {
  depends_on = [null_resource.bigquery_sheet_zip_simple_cloudfunction]

  name   = "source/bigquery-to-sheet-simple.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./bigquery-to-sheet-simple/bigquery-to-sheet-simple.zip"
}


## cloud_function
resource "google_cloudfunctions_function" "bigquery_sheet_simple_function" {
  depends_on = [null_resource.bigquery_sheet_zip_simple_cloudfunction, google_storage_bucket_object.bigquery_sheet_simple_cloudfunction_archive]

  name                  = "bigquery-to-sheet-simple"
  description           = "Sync data from BigQuery to Google Sheets"
  available_memory_mb   = 512
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  # 여기서 source_directory 속성을 설정합니다.
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.bigquery_sheet_simple_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "update_data_in_sheets" # Python 코드 내 함수 이름

  environment_variables = {
    BIGQUERY_TABLE = "${var.project}.mongodb_dataset.mongodb-internal-table",
    SHEET_ID       = "" # Replace with your Google Sheet ID
  }
}


## cloud_scheduler
resource "google_cloud_scheduler_job" "bigquery_sheet_simple_job" {
  depends_on = [google_cloudfunctions_function.bigquery_sheet_simple_function]

  name      = "bigquery-to-sheet-simple-daliy-job"
  region    = var.region
  schedule  = "0 10 * * *" # Daily 10:00 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.bigquery_sheet_simple_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

##########################################################################################################

## bigquery table  -> googlesheet workflow multiple data
resource "null_resource" "bigquery_sheet_zip_multiple_cloudfunction" {
  depends_on = [google_bigquery_dataset.mongodb_dataset, google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./bigquery-to-sheet-multiple
      zip -r bigquery-to-sheet-multiple.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./bigquery-to-sheet-multiple/main.py")
    requirements_content_hash = filesha256("./bigquery-to-sheet-multiple/requirements.txt")
    json_content_hash         = filesha256("./bigquery-to-sheet-simple/bigquery.json")
  }
}

resource "google_storage_bucket_object" "bigquery_sheet_multiple_cloudfunction_archive" {
  depends_on = [null_resource.bigquery_sheet_zip_multiple_cloudfunction]

  name   = "source/bigquery-to-sheet-multiple.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./bigquery-to-sheet-multiple/bigquery-to-sheet-multiple.zip"
}


## cloud_function
resource "google_cloudfunctions_function" "bigquery_sheet_multiple_function" {
  depends_on = [null_resource.bigquery_sheet_zip_multiple_cloudfunction, google_storage_bucket_object.bigquery_sheet_multiple_cloudfunction_archive]

  name                  = "bigquery-to-sheet-multiple"
  description           = "Sync data from BigQuery to Google Sheets"
  available_memory_mb   = 512
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  # Set the source_directory property here.
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.bigquery_sheet_multiple_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "update_multiple_datas_in_sheets" # Function name in Python code

  environment_variables = {
    BIGQUERY_TABLE = "${var.project}.mongodb_dataset.mongodb-internal-table",
    SHEET_ID       = "" # Replace with your Google Sheet ID
  }
}


## cloud_scheduler
resource "google_cloud_scheduler_job" "bigquery_sheet_multiple_job" {
  depends_on = [google_cloudfunctions_function.bigquery_sheet_multiple_function]

  name      = "bigquery-to-sheet-multiple-daliy-job"
  region    = var.region
  schedule  = "5 10 * * *" # Daily 10:05 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.bigquery_sheet_multiple_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

