## BigQuery DB Connection ##
resource "google_bigquery_connection" "prod_somaz_db_connection" {
  connection_id = "prod-somaz-db-connection"
  location      = var.region
  friendly_name = "prod-somaz-db-connection"
  description   = "This is prod-somaz-db connection"
  cloud_sql {
    instance_id = "somaz-bigquery:asia-northeast1:prod-somaz-db"
    database    = "game_log"
    type        = "MYSQL"
    credential {
      username = var.db_admin_user
      password = var.db_admin_password
    }
  }
}


