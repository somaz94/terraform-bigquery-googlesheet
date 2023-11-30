## DB(Mysql) ##
module "prod_mysql" {
  source                          = "../../modules/mysql"
  name                            = var.db_name_prod
  project_id                      = var.project
  database_version                = "MYSQL_8_0"
  region                          = var.region
  zone                            = "${var.region}-a"
  tier                            = "db-custom-2-3840"
  deletion_protection             = false
  root_password                   = var.db_admin_password
  availability_type               = "ZONAL"
  maintenance_window_day          = "1"
  maintenance_window_hour         = "0"
  maintenance_window_update_track = "stable"

  ip_configuration = {
    ipv4_enabled                                  = false
    require_ssl                                   = false
    private_network                               = "projects/${var.project}/global/networks/${var.shared_vpc}"
    authorized_networks                           = []
    allocated_ip_range                            = "google-managed-services-prod-mgmt-share-vpc"
    enable_private_path_for_google_cloud_services = true
  }

  user_labels = local.default_labels

  database_flags = [
    {
      name  = "long_query_time"
      value = "1"
    }
  ]

  additional_users = [
    {
      name            = var.db_admin_user
      password        = var.db_admin_password
      host            = "%" // host from where the user can connect.
      random_password = false
      type            = "BUILT_IN" // normal user or admin.
    }
  ]

  additional_databases = var.prod_dsp_db_additional_databases

}
