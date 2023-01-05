APP_NAME="mexico_compliance"

FRAPPE_DOCKER_VERSION="v14"
FRAPPE_GIT_VERSION="version-14"
ERPNEXT_DOCKER_VERSION="v14"
ERPNEXT_GIT_VERSION="version-14"

group "default" {
    targets = ["backend", "frontend"]
}

target "backend" {
    dockerfile = "backend.Dockerfile"
    tags = ["ahuahuachi/erpnext-mexico_compliance-worker:latest"]
    args = {
      "ERPNEXT_VERSION"=ERPNEXT_DOCKER_VERSION
    }
}

target "frontend" {
    dockerfile = "frontend.Dockerfile"
    tags = ["ahuahuachi/erpnext-mexico_compliance-nginx:latest"]
    args = {
      "FRAPPE_DOCKER_VERSION"=FRAPPE_DOCKER_VERSION
      "FRAPPE_GIT_VERSION"=FRAPPE_GIT_VERSION
      "ERPNEXT_VERSION"=ERPNEXT_GIT_VERSION
      "APP_NAME" = APP_NAME
    }
}
