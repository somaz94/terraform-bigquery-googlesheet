## onchain(Dune) quest2.0 daily global monthly -> googlesheet workflow
resource "null_resource" "onchain_quest2_daily_global_monthly_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./cloud-functions/onchain-quest2-daily-global-monthly-to-sheet
      zip -r onchain-quest2-daily-global-monthly-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./cloud-functions/onchain-quest2-daily-global-monthly-to-sheet/main.py")
    requirements_content_hash = filesha256("./cloud-functions/onchain-quest2-daily-global-monthly-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./cloud-functions/onchain-quest2-daily-global-monthly-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_quest2_daily_global_monthly_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_quest2_daily_global_monthly_sheet_zip_cloud_function]

  name   = "source/onchain-quest2-daily-global-monthly-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./cloud-functions/onchain-quest2-daily-global-monthly-to-sheet/onchain-quest2-daily-global-monthly-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_quest2_daily_global_monthly_sheet_function" {
  depends_on = [null_resource.onchain_quest2_daily_global_monthly_sheet_zip_cloud_function, google_storage_bucket_object.onchain_quest2_daily_global_monthly_sheet_cloudfunction_archive]

  name                  = "onchain-quest2-daily-global-monthly-to-sheet"
  description           = "Function to onchain-quest2-daily-global-monthly-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_quest2_daily_global_monthly_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_quest2_daily_global_monthly_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_quest2_daily_global_monthly_sheet_function]

  name      = "onchain-quest2-daily-global-monthly-to-sheet-job"
  region    = var.region
  schedule  = "25 10 1 * *" # 매월 1일 10:25 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_quest2_daily_global_monthly_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

###################################################################################

## onchain(Dune) quest2.0 weekly monthly -> googlesheet workflow
resource "null_resource" "onchain_quest2_weekly_monthly_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./cloud-functions/onchain-quest2-weekly-monthly-to-sheet
      zip -r onchain-quest2-weekly-monthly-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./cloud-functions/onchain-quest2-weekly-monthly-to-sheet/main.py")
    requirements_content_hash = filesha256("./cloud-functions/onchain-quest2-weekly-monthly-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./cloud-functions/onchain-quest2-weekly-monthly-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_quest2_weekly_monthly_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_quest2_weekly_monthly_sheet_zip_cloud_function]

  name   = "source/onchain-quest2-weekly-monthly-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./cloud-functions/onchain-quest2-weekly-monthly-to-sheet/onchain-quest2-weekly-monthly-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_quest2_weekly_monthly_sheet_function" {
  depends_on = [null_resource.onchain_quest2_weekly_monthly_sheet_zip_cloud_function, google_storage_bucket_object.onchain_quest2_weekly_monthly_sheet_cloudfunction_archive]

  name                  = "onchain-quest2-weekly-monthly-to-sheet"
  description           = "Function to onchain-quest2-weekly-monthly-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_quest2_weekly_monthly_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_quest2_weekly_monthly_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_quest2_weekly_monthly_sheet_function]

  name      = "onchain-quest2-weekly-monthly-to-sheet-job"
  region    = var.region
  schedule  = "30 10 1 * *" # 매월 1일 10:30 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_quest2_weekly_monthly_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

###################################################################################

## onchain(Dune) quest2.0 premium monthly -> googlesheet workflow
resource "null_resource" "onchain_quest2_premium_monthly_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./cloud-functions/onchain-quest2-premium-monthly-to-sheet
      zip -r onchain-quest2-premium-monthly-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./cloud-functions/onchain-quest2-premium-monthly-to-sheet/main.py")
    requirements_content_hash = filesha256("./cloud-functions/onchain-quest2-premium-monthly-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./cloud-functions/onchain-quest2-premium-monthly-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_quest2_premium_monthly_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_quest2_premium_monthly_sheet_zip_cloud_function]

  name   = "source/onchain-quest2-premium-monthly-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./cloud-functions/onchain-quest2-premium-monthly-to-sheet/onchain-quest2-premium-monthly-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_quest2_premium_monthly_sheet_function" {
  depends_on = [null_resource.onchain_quest2_premium_monthly_sheet_zip_cloud_function, google_storage_bucket_object.onchain_quest2_premium_monthly_sheet_cloudfunction_archive]

  name                  = "onchain-quest2-premium-monthly-to-sheet"
  description           = "Function to onchain-quest2-premium-monthly-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_quest2_premium_monthly_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_quest2_premium_monthly_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_quest2_premium_monthly_sheet_function]

  name      = "onchain-quest2-premium-monthly-to-sheet-job"
  region    = var.region
  schedule  = "35 10 1 * *" # 매월 1일 10:35 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_quest2_premium_monthly_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

#############################################################################################################

## onchain(Dune) pack contribution compensation monthly -> googlesheet workflow
resource "null_resource" "onchain_pack_contribution_compensation_monthly_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./cloud-functions/onchain-pack-contribution-compensation-monthly-to-sheet
      zip -r onchain-pack-contribution-compensation-monthly-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./cloud-functions/onchain-pack-contribution-compensation-monthly-to-sheet/main.py")
    requirements_content_hash = filesha256("./cloud-functions/onchain-pack-contribution-compensation-monthly-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./cloud-functions/onchain-pack-contribution-compensation-monthly-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_pack_contribution_compensation_monthly_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_pack_contribution_compensation_monthly_sheet_zip_cloud_function]

  name   = "source/onchain-pack-contribution-compensation-monthly-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./cloud-functions/onchain-pack-contribution-compensation-monthly-to-sheet/onchain-pack-contribution-compensation-monthly-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_pack_contribution_compensation_monthly_sheet_function" {
  depends_on = [null_resource.onchain_pack_contribution_compensation_monthly_sheet_zip_cloud_function, google_storage_bucket_object.onchain_pack_contribution_compensation_monthly_sheet_cloudfunction_archive]

  name                  = "onchain-pack-contribution-compensation-monthly-to-sheet"
  description           = "Function to onchain-pack-contribution-compensation-monthly-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_pack_contribution_compensation_monthly_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_pack_contribution_compensation_monthly_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_pack_contribution_compensation_monthly_sheet_function]

  name      = "onchain-pack-contribution-compensation-monthly-to-sheet-job"
  region    = var.region
  schedule  = "40 10 1 * *" # 매월 1일 10:40 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_pack_contribution_compensation_monthly_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

#############################################################################################################

## onchain(Dune) pack airdrop monthly -> googlesheet workflow
resource "null_resource" "onchain_pack_airdrop_monthly_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./cloud-functions/onchain-pack-airdrop-monthly-to-sheet
      zip -r onchain-pack-airdrop-monthly-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./cloud-functions/onchain-pack-airdrop-monthly-to-sheet/main.py")
    requirements_content_hash = filesha256("./cloud-functions/onchain-pack-airdrop-monthly-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./cloud-functions/onchain-pack-airdrop-monthly-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_pack_airdrop_monthly_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_pack_airdrop_monthly_sheet_zip_cloud_function]

  name   = "source/onchain-pack-airdrop-monthly-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./cloud-functions/onchain-pack-airdrop-monthly-to-sheet/onchain-pack-airdrop-monthly-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_pack_airdrop_monthly_sheet_function" {
  depends_on = [null_resource.onchain_pack_airdrop_monthly_sheet_zip_cloud_function, google_storage_bucket_object.onchain_pack_airdrop_monthly_sheet_cloudfunction_archive]

  name                  = "onchain-pack-airdrop-monthly-to-sheet"
  description           = "Function to onchain-pack-airdrop-monthly-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_pack_airdrop_monthly_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_pack_airdrop_monthly_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_pack_airdrop_monthly_sheet_function]

  name      = "onchain-pack-airdrop-monthly-to-sheet-job"
  region    = var.region
  schedule  = "50 10 1 * *" # 매월 1일 10:50 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_pack_airdrop_monthly_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}
