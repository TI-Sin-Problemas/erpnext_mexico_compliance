APP_NAME="mexico_compliance"

variable "FRAPPE_VERSION" {}
variable "ERPNEXT_VERSION" {}

group "default" {
    targets = ["backend", "frontend"]
}

target "backend" {
    dockerfile = "backend.Dockerfile"
    tags = ["ahuahuachi/erpnext-mexico_compliance-worker:latest"]
    args = {
      "ERPNEXT_VERSION" = ERPNEXT_VERSION
      "APP_NAME" = APP_NAME
    }
}

target "frontend" {
    dockerfile = "frontend.Dockerfile"
    tags = ["ahuahuachi/erpnext-mexico_compliance-nginx:latest"]
    args = {
      "FRAPPE_VERSION" = FRAPPE_VERSION
      "ERPNEXT_VERSION" = ERPNEXT_VERSION
      "APP_NAME" = APP_NAME
    }
}
