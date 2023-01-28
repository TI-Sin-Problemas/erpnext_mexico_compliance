APP_NAME="mexico_compliance"

APPS_JSON_BASE64=""

target "default" {
  dockerfile = "Containerfile"
  tags = ["ahuahuachi/erpnext-mexico_compliance:latest"]
  args = {
    "FRAPPE_PATH"="https://github.com/frappe/frappe"
    "FRAPPE_BRANCH"="version-14"
    "APPS_JSON_BASE64"=APPS_JSON_BASE64
  }
}
