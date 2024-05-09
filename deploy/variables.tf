variable "environment" {
  description = "The environment to deploy to (e.g., dev, prod)"
  type        = string
}

variable "api_host" {
    description = "The host name of the api with its protocol"
    type        = string
    default     = "https://5ib38zgat9.execute-api.us-east-2.amazonaws.com"
}

variable "bucket_name" {
    description = "The page bucket to be deployed to"
    type        = string
    default     = "bmdmodules"
}