# main.tf
provider "aws" {
  region = "us-east-2"  # Replace with your desired region
}

# Render the template with environment-specific data
data "template_file" "rendered_index_html" {
  template = file("index.html.tmpl")
  vars = {
    EnvName   = var.environment
    ApiHostName   = var.api_host
  }
}

# Upload the rendered index.html to the selected S3 bucket
resource "aws_s3_object" "index_html" {
  bucket = "${var.environment}${var.bucket_name}"
  key    = "index.html"
  content = data.template_file.rendered_index_html.rendered
  source = "get_future_orders_event_datetime/"
}
