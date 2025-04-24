resource "aws_s3_bucket" "rajagopalan-endopheno" {
  bucket = "rajagopalan-endopheno"

  tags = {
    Owner = element(split("/", data.aws_caller_identity.current.arn), 1)
  }
}

resource "aws_s3_bucket_ownership_controls" "endopheno_data_ownership_controls" {
  bucket = aws_s3_bucket.rajagopalan-endopheno.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "endopheno_data_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.endopheno_data_ownership_controls]

  bucket = aws_s3_bucket.rajagopalan-endopheno.id
  acl    = "private"
}

resource "aws_s3_bucket_lifecycle_configuration" "endopheno_data_expiration" {
  bucket = aws_s3_bucket.rajagopalan-endopheno.id

  rule {
    id      = "compliance-retention-policy"
    status  = "Enabled"

    expiration {
	  days = 100
    }
  }
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs_task_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_execution_role_custom_policy" {
  name = "ecs_task_execution_role_custom_policy"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeNetworkInterfaces",
          "ec2:AttachNetworkInterface",
          "ec2:DetachNetworkInterface",
          "ec2:DeleteNetworkInterface"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "ecs_task_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_role_policy" {
  name = "ecs_task_role_policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"  # Allow listing objects in the bucket
        ]
        Resource = "arn:aws:s3:::rajagopalan-endopheno"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",  # Allow reading objects
          "s3:PutObject"   # Allow writing objects
        ]
        Resource = "arn:aws:s3:::rajagopalan-endopheno/*"
      }
    ]
  })
}

resource "aws_cloudwatch_log_group" "endopheno_ecs_log_group" {
  name              = "/ecs/rajagopalan-endopheno"
  retention_in_days = 30  # Optional: Set log retention
}

resource "aws_ecs_task_definition" "rajagopalan-endopheno" {
  family                   = "rajagopalan-endopheno"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "rajagopalan-endopheno"
      image     = "${aws_ecr_repository.rajagopalan-endopheno.repository_url}:v14"
      essential = true
      environment = [
        {
          name  = "S3_BUCKET_ARN"
          value = "${aws_s3_bucket.rajagopalan-endopheno.bucket}"
        },
        { name = "ENVIRONMENT"
          value = "FARGATE"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.endopheno_ecs_log_group.name
          awslogs-region        = data.aws_region.current_region.name
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  ephemeral_storage {
    size_in_gib = 200
  }
}

resource "aws_s3_bucket_cors_configuration" "rajagopalan_endopheno_cors_configuration" {
  bucket = aws_s3_bucket.rajagopalan-endopheno.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "POST", "PUT", "HEAD"]
    allowed_origins = ["http://localhost:5173", "bmin5100.com", "*.bmin5100"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

locals {
  ecs_task_definition_container_name = "rajagopalan-endopheno"
}

module "invoke_fargate_lambda" {
  source = "git@github.com:BMIN-5100-Spring-2025/infrastructure.git//invoke_fargate_lambda/terraform?ref=f844e9c04f901768ccb99aff77286165bf71b83e"

  project_name = "rajagopalan-endopheno"
  ecs_task_definition_arn = aws_ecs_task_definition.rajagopalan-endopheno.arn
  ecs_task_execution_role_arn = aws_iam_role.ecs_task_execution_role.arn
  ecs_task_task_role_arn = aws_iam_role.ecs_task_role.arn
  ecs_task_definition_container_name = local.ecs_task_definition_container_name

  ecs_cluster_arn = data.terraform_remote_state.infrastructure.outputs.ecs_cluster_arn
  ecs_security_group_id = data.terraform_remote_state.infrastructure.outputs.ecs_security_group_id
  private_subnet_id = data.terraform_remote_state.infrastructure.outputs.private_subnet_id
  api_gateway_authorizer_id = data.terraform_remote_state.infrastructure.outputs.api_gateway_authorizer_id
  api_gateway_execution_arn = data.terraform_remote_state.infrastructure.outputs.api_gateway_execution_arn
  api_gateway_id = data.terraform_remote_state.infrastructure.outputs.api_gateway_id
  environment_variables = {}
}
