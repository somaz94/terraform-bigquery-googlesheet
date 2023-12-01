## onchain(Dune) agent common -> googlesheet workflow
resource "null_resource" "onchain_agent_common_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./onchain-agent-common-to-sheet
      zip -r onchain-agent-common-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./onchain-agent-common-to-sheet/main.py")
    requirements_content_hash = filesha256("./onchain-agent-common-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./onchain-agent-common-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_agent_common_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_agent_common_sheet_zip_cloud_function]

  name   = "source/onchain-agent-common-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./onchain-agent-common-to-sheet/onchain-agent-common-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_agent_common_sheet_function" {
  depends_on = [null_resource.onchain_agent_common_sheet_zip_cloud_function, google_storage_bucket_object.onchain_agent_common_sheet_cloudfunction_archive]

  name                  = "onchain-agent-common-to-sheet"
  description           = "Function to onchain-agent-common-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_agent_common_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_agent_common_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_agent_common_sheet_function]

  name      = "onchain-agent-common-to-sheet-daily-job"
  region    = var.region
  schedule  = "0 9 * * *" # Daily 09:00 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_agent_common_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

##################################################################################

## onchain(Dune) agent uncommon -> googlesheet workflow
resource "null_resource" "onchain_agent_uncommon_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./onchain-agent-uncommon-to-sheet
      zip -r onchain-agent-uncommon-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./onchain-agent-uncommon-to-sheet/main.py")
    requirements_content_hash = filesha256("./onchain-agent-uncommon-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./onchain-agent-uncommon-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_agent_uncommon_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_agent_uncommon_sheet_zip_cloud_function]

  name   = "source/onchain-agent-uncommon-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./onchain-agent-uncommon-to-sheet/onchain-agent-uncommon-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_agent_uncommon_sheet_function" {
  depends_on = [null_resource.onchain_agent_uncommon_sheet_zip_cloud_function, google_storage_bucket_object.onchain_agent_uncommon_sheet_cloudfunction_archive]

  name                  = "onchain-agent-uncommon-to-sheet"
  description           = "Function to onchain-agent-uncommon-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_agent_uncommon_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_agent_uncommon_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_agent_uncommon_sheet_function]

  name      = "onchain-agent-uncommon-to-sheet-daily-job"
  region    = var.region
  schedule  = "05 9 * * *" # Daily 09:05 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_agent_uncommon_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

################################################################################

## onchain(Dune) agent rare -> googlesheet workflow
resource "null_resource" "onchain_agent_rare_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./onchain-agent-rare-to-sheet
      zip -r onchain-agent-rare-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./onchain-agent-rare-to-sheet/main.py")
    requirements_content_hash = filesha256("./onchain-agent-rare-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./onchain-agent-rare-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_agent_rare_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_agent_rare_sheet_zip_cloud_function]

  name   = "source/onchain-agent-rare-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./onchain-agent-rare-to-sheet/onchain-agent-rare-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_agent_rare_sheet_function" {
  depends_on = [null_resource.onchain_agent_rare_sheet_zip_cloud_function, google_storage_bucket_object.onchain_agent_rare_sheet_cloudfunction_archive]

  name                  = "onchain-agent-rare-to-sheet"
  description           = "Function to onchain-agent-rare-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_agent_rare_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_agent_rare_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_agent_rare_sheet_function]

  name      = "onchain-agent-rare-to-sheet-daily-job"
  region    = var.region
  schedule  = "10 9 * * *" # Daily 09:10 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_agent_rare_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

###################################################################################

## onchain(Dune) agent epic -> googlesheet workflow
resource "null_resource" "onchain_agent_epic_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./onchain-agent-epic-to-sheet
      zip -r onchain-agent-epic-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./onchain-agent-epic-to-sheet/main.py")
    requirements_content_hash = filesha256("./onchain-agent-epic-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./analytics-to-sheet-new-web-visitors-country/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_agent_epic_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_agent_epic_sheet_zip_cloud_function]

  name   = "source/onchain-agent-epic-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./onchain-agent-epic-to-sheet/onchain-agent-epic-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_agent_epic_sheet_function" {
  depends_on = [null_resource.onchain_agent_epic_sheet_zip_cloud_function, google_storage_bucket_object.onchain_agent_epic_sheet_cloudfunction_archive]

  name                  = "onchain-agent-epic-to-sheet"
  description           = "Function to onchain-agent-epic-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_agent_epic_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_agent_epic_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_agent_epic_sheet_function]

  name      = "onchain-agent-epic-to-sheet-daily-job"
  region    = var.region
  schedule  = "15 9 * * *" # Daily 09:15 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_agent_epic_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

###################################################################################

## onchain(Dune) agent legend -> googlesheet workflow
resource "null_resource" "onchain_agent_legend_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./onchain-agent-legend-to-sheet
      zip -r onchain-agent-legend-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./onchain-agent-legend-to-sheet/main.py")
    requirements_content_hash = filesha256("./onchain-agent-legend-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./onchain-agent-legend-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_agent_legend_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_agent_legend_sheet_zip_cloud_function]

  name   = "source/onchain-agent-legend-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./onchain-agent-legend-to-sheet/onchain-agent-legend-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_agent_legend_sheet_function" {
  depends_on = [null_resource.onchain_agent_legend_sheet_zip_cloud_function, google_storage_bucket_object.onchain_agent_legend_sheet_cloudfunction_archive]

  name                  = "onchain-agent-legend-to-sheet"
  description           = "Function to onchain-agent-legend-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_agent_legend_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_agent_legend_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_agent_legend_sheet_function]

  name      = "onchain-agent-legend-to-sheet-daily-job"
  region    = var.region
  schedule  = "20 9 * * *" # Daily 09:20 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_agent_legend_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

###################################################################################

## onchain(Dune) pack basic epic 1 -> googlesheet workflow
resource "null_resource" "onchain_pack_basic_epic1_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./onchain-pack-basic-epic1-to-sheet
      zip -r onchain-pack-basic-epic1-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./onchain-pack-basic-epic1-to-sheet/main.py")
    requirements_content_hash = filesha256("./onchain-pack-basic-epic1-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./onchain-pack-basic-epic1-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_pack_basic_epic1_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_pack_basic_epic1_sheet_zip_cloud_function]

  name   = "source/onchain-pack-basic-epic1-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./onchain-pack-basic-epic1-to-sheet/onchain-pack-basic-epic1-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_pack_basic_epic1_sheet_function" {
  depends_on = [null_resource.onchain_pack_basic_epic1_sheet_zip_cloud_function, google_storage_bucket_object.onchain_pack_basic_epic1_sheet_cloudfunction_archive]

  name                  = "onchain-pack-basic-epic1-to-sheet"
  description           = "Function to onchain-pack-basic-epic1-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_pack_basic_epic1_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_pack_basic_epic1_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_pack_basic_epic1_sheet_function]

  name      = "onchain-pack-basic-epic1-to-sheet-daily-job"
  region    = var.region
  schedule  = "25 9 * * *" # Daily 09:25 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_pack_basic_epic1_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

###################################################################################

## onchain(Dune) materials dp chip -> googlesheet workflow
resource "null_resource" "onchain_materials_dp_chip_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./onchain-materials-dp-chip-to-sheet
      zip -r onchain-materials-dp-chip-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./onchain-materials-dp-chip-to-sheet/main.py")
    requirements_content_hash = filesha256("./onchain-materials-dp-chip-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./onchain-materials-dp-chip-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_materials_dp_chip_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_materials_dp_chip_sheet_zip_cloud_function]

  name   = "source/onchain-materials-dp-chip-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./onchain-materials-dp-chip-to-sheet/onchain-materials-dp-chip-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_materials_dp_chip_sheet_function" {
  depends_on = [null_resource.onchain_materials_dp_chip_sheet_zip_cloud_function, google_storage_bucket_object.onchain_materials_dp_chip_sheet_cloudfunction_archive]

  name                  = "onchain-materials-dp-chip-to-sheet"
  description           = "Function to onchain-materials-dp-chip-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_materials_dp_chip_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_materials_dp_chip_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_materials_dp_chip_sheet_function]

  name      = "onchain-materials-dp-chip-to-sheet-daily-job"
  region    = var.region
  schedule  = "25 9 * * *" # Daily 09:25 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_materials_dp_chip_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

###################################################################################

## onchain(Dune) materials skill exchange ticket -> googlesheet workflow
resource "null_resource" "onchain_materials_skill_exchange_ticket_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./onchain-materials-skill-exchange-ticket-to-sheet
      zip -r onchain-materials-skill-exchange-ticket-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./onchain-materials-skill-exchange-ticket-to-sheet/main.py")
    requirements_content_hash = filesha256("./onchain-materials-skill-exchange-ticket-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./onchain-materials-skill-exchange-ticket-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_materials_skill_exchange_ticket_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_materials_skill_exchange_ticket_sheet_zip_cloud_function]

  name   = "source/onchain-materials-skill-exchange-ticket-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./onchain-materials-skill-exchange-ticket-to-sheet/onchain-materials-skill-exchange-ticket-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_materials_skill_exchange_ticket_sheet_function" {
  depends_on = [null_resource.onchain_materials_skill_exchange_ticket_sheet_zip_cloud_function, google_storage_bucket_object.onchain_materials_skill_exchange_ticket_sheet_cloudfunction_archive]

  name                  = "onchain-materials-skill-exchange-ticket-to-sheet"
  description           = "Function to onchain-materials-skill-exchange-ticket-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_materials_skill_exchange_ticket_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_materials_skill_exchange_ticket_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_materials_skill_exchange_ticket_sheet_function]

  name      = "onchain-materials-skill-exchange-ticket-to-sheet-daily-job"
  region    = var.region
  schedule  = "25 9 * * *" # Daily 09:25 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_materials_skill_exchange_ticket_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}

###################################################################################

## onchain(Dune) quest2.0 daily global -> googlesheet workflow
resource "null_resource" "onchain_quest2_daily_global_sheet_zip_cloud_function" {
  depends_on = [google_storage_bucket.cloud_function_storage]

  provisioner "local-exec" {
    command = <<EOT
      cd ./onchain-quest2-daily-global-to-sheet
      zip -r onchain-quest2-daily-global-to-sheet.zip main.py requirements.txt bigquery.json
    EOT
  }

  triggers = {
    main_content_hash         = filesha256("./onchain-quest2-daily-global-to-sheet/main.py")
    requirements_content_hash = filesha256("./onchain-quest2-daily-global-to-sheet/requirements.txt")
    json_content_hash         = filesha256("./onchain-quest2-daily-global-to-sheet/bigquery.json")
  }
}

resource "google_storage_bucket_object" "onchain_quest2_daily_global_sheet_cloudfunction_archive" {
  depends_on = [null_resource.onchain_quest2_daily_global_sheet_zip_cloud_function]

  name   = "source/onchain-quest2-daily-global-to-sheet.zip"
  bucket = google_storage_bucket.cloud_function_storage.name
  source = "./onchain-quest2-daily-global-to-sheet/onchain-quest2-daily-global-to-sheet.zip"
}

## cloud_function
resource "google_cloudfunctions_function" "onchain_quest2_daily_global_sheet_function" {
  depends_on = [null_resource.onchain_quest2_daily_global_sheet_zip_cloud_function, google_storage_bucket_object.onchain_quest2_daily_global_sheet_cloudfunction_archive]

  name                  = "onchain-quest2-daily-global-to-sheet"
  description           = "Function to onchain-quest2-daily-global-to-sheet"
  runtime               = "python38"
  service_account_email = module.service_accounts_bigquery.email
  docker_registry       = "ARTIFACT_REGISTRY"
  timeout               = 540

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cloud_function_storage.name
  source_archive_object = google_storage_bucket_object.onchain_quest2_daily_global_sheet_cloudfunction_archive.name
  trigger_http          = true
  entry_point           = "main"

  environment_variables = {
    SHEET_ID       = "" # Replace with your Google Sheet ID
    DUNE_API_KEY   = "" # Replace with your Dune API KEY
  }
}

## cloud_scheduler
resource "google_cloud_scheduler_job" "onchain_quest2_daily_global_sheet_job" {
  depends_on = [google_cloudfunctions_function.onchain_quest2_daily_global_sheet_function]

  name      = "onchain-quest2-daily-global-to-sheet-daily-job"
  region    = var.region
  schedule  = "25 9 * * *" # Daily 09:25 AM
  time_zone = "Asia/Seoul"

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.onchain_quest2_daily_global_sheet_function.https_trigger_url
    oidc_token {
      service_account_email = module.service_accounts_bigquery.email
    }
  }
}
