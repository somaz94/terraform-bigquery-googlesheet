## common ##
variable "project" {}
variable "region" {}
variable "prod_region" {}
variable "environment" {}
variable "terraform" {}

## terraform tfstate backend ##
variable "tf_state_bucket" {}

## vpc ##
variable "shared_vpc" {}
variable "subnet_share" {}
variable "service_project" {
  type = list(string)
}
variable "dev_somaz_gke_pod" {}
variable "dev_somaz_gke_service" {}
variable "mgmt_gke_pod" {}
variable "mgmt_gke_service" {}

## prod_vpc
variable "prod_shared_vpc" {}
variable "prod_subnet_share" {}
variable "prod_service_project" {
  type = list(string)
}
variable "prod_somaz_gke_pod" {}
variable "prod_somaz_gke_service" {}

# DB(Mysql) ##
variable "db_admin_user" {}
variable "db_admin_password" {}
variable "db_name_prod" {}
variable "prod_dsp_db_additional_databases" {
  description = "Additional databases to be created"
  type = list(object({
    name      = string
    charset   = string
    collation = string
  }))
}