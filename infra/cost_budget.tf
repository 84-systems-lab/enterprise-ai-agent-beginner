# Optional account-total budget named for this project. Alerts are not a cap.
variable "budget_notification_emails" {
  description = "Recipients owned by this learning project; keep values in ignored tfvars."
  type        = set(string)
  default     = []
}
variable "monthly_budget_usd" {
  type    = number
  default = 25
  validation {
    condition     = var.monthly_budget_usd > 0
    error_message = "The notification budget must be positive."
  }
}
resource "aws_budgets_budget" "book_monthly" {
  count        = length(var.budget_notification_emails) > 0 ? 1 : 0
  name         = "${var.project_name}-monthly"
  budget_type  = "COST"
  limit_amount = tostring(var.monthly_budget_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = tolist(var.budget_notification_emails)
  }
}
