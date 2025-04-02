resource "aws_s3_bucket" "rajagopalan-endopheno" {
  bucket = "rajagopalan-endopheno"

  tags = {
    Owner = element(split("/", data.aws_caller_identity.current.arn), 1)
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
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Effect = "Allow"
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
      image     = "${aws_ecr_repository.rajagopalan-endopheno.repository_url}:v3"
      essential = true
      environment = [
        {
          name  = "S3_BUCKET_ARN"
          value = "${aws_s3_bucket.rajagopalan-endopheno.id}"
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