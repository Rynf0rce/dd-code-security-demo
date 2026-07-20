## Datadog Code Security — IaC(terraform) 룰 탐지 시연용 의도적 취약 구성
## 실제 배포용이 아닙니다. terraform apply 하지 마십시오.

provider "aws" {
  region = "ap-northeast-2"
}

# terraform-aws: S3 버킷 서버측 암호화 미설정 + 버저닝 미설정
resource "aws_s3_bucket" "scada_archive" {
  bucket = "gseps-scada-archive-demo"
}

# terraform-aws: S3 버킷 퍼블릭 read ACL
resource "aws_s3_bucket_acl" "scada_archive_acl" {
  bucket = aws_s3_bucket.scada_archive.id
  acl    = "public-read"
}

# terraform-aws: 퍼블릭 액세스 차단 전부 해제
resource "aws_s3_bucket_public_access_block" "scada_archive_pab" {
  bucket                  = aws_s3_bucket.scada_archive.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# terraform-aws: 0.0.0.0/0 에서 SSH(22) 및 전체 포트 인바운드 허용
resource "aws_security_group" "scada_gateway" {
  name        = "gseps-scada-gateway-demo"
  description = "SCADA gateway ingress"

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "OPC UA from anywhere"
    from_port   = 4840
    to_port     = 4840
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# terraform-aws: RDS 인스턴스 암호화 미설정 + 퍼블릭 접근 허용 + 하드코딩 비밀번호
resource "aws_db_instance" "equipment" {
  identifier           = "gseps-equipment-demo"
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  username             = "gseps_app"
  password             = "Gs3ps!Prod#2024"
  publicly_accessible  = true
  storage_encrypted    = false
  skip_final_snapshot  = true
}

# terraform-aws: IAM 정책 와일드카드 권한
resource "aws_iam_policy" "scada_full" {
  name = "gseps-scada-full-demo"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}
