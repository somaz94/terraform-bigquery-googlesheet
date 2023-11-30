## Terraform Backend ##

terraform {
  backend "gcs" {
    bucket = "somaz-bigquery-terraform-remote-tfstate"
    prefix = "somaz-bigquery"
  }
}


