## common ##
project     = "somaz-bigquery"
region      = "asia-northeast3"
prod_region = "asia-northeast1"
environment = "mgmt"
terraform   = "true"

## terraform tfstate backend ##
tf_state_bucket = "mgmt-terraform-remote-tfstate"

## vpc ##
shared_vpc              = "mgmt-share-vpc"
service_project         = ["dev-somaz"]
subnet_share            = "mgmt-share-sub"
dev_somaz_gke_pod       = "dev-somaz-gke-pod"
dev_somaz_gke_service   = "dev-somaz-gke-service"
mgmt_gke_pod          = "mgmt-gke-pod"
mgmt_gke_service      = "mgmt-gke-service"

## prod_vpc
prod_shared_vpc          = "prod-mgmt-share-vpc"
prod_subnet_share        = "prod-mgmt-share-sub"
prod_service_project     = ["prod-somaz"]
prod_somaz_gke_pod       = "prod-somaz-gke-pod"
prod_somaz_gke_service   = "prod-somaz-gke-service"

## DB(Mysql) ##
db_admin_user              = "admin"
db_admin_password          = "somaz!23"
db_name_prod               = "prod-somaz-db"

prod_somaz_db_additional_databases = [
  {
    name      = "admin"
    charset   = "utf8mb3"
    collation = "utf8mb3_general_ci"
  },
  {
    name      = "game_log"
    charset   = "utf8mb3"
    collation = "utf8mb3_general_ci"
  }
]