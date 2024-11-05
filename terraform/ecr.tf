# ecr.tf

resource "aws_ecr_repository" "frontend" {
  name = "${var.project_name}-frontend"

  tags = {
    Name = "${var.project_name}-frontend-ecr"
  }
}

resource "aws_ecr_repository" "backend" {
  name = "${var.project_name}-backend"

  tags = {
    Name = "${var.project_name}-backend-ecr"
  }
}
