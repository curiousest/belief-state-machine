# variables.tf

variable "aws_region" {
  description = "AWS region to deploy resources"
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix for resources"
  default     = "belief-state-machine"
}

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)"
  default     = "dev"
}

variable "desired_count" {
  description = "Number of ECS tasks to run"
  default     = 1
}

variable "frontend_port" {
  description = "Port on which the frontend container listens"
  default     = 3000
}

variable "backend_port" {
  description = "Port on which the backend container listens"
  default     = 8000
}

variable "allowed_ips" {
  description = "List of allowed CIDR blocks to access the ALB"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
}

variable "crewai_api_key" {
  description = "CrewAI API Key"
  type        = string
}
