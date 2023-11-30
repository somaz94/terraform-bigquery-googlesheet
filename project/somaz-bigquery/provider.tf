provider "google" {
  credentials = file("../../key/terraform.json")
  project     = var.project
  region      = var.region
}

provider "google-beta" {
  credentials = file("../../key/terraform.json")
  project     = var.project
  region      = var.region
}

