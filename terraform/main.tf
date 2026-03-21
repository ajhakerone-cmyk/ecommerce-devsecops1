terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket for static assets
resource "aws_s3_bucket" "ecommerce_assets" {
  bucket = "ecommerce-assets-${var.environment}-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name        = "E-commerce Assets"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Block public access by default (security best practice)
resource "aws_s3_bucket_public_access_block" "ecommerce_assets" {
  bucket = aws_s3_bucket.ecommerce_assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning for audit trail
resource "aws_s3_bucket_versioning" "ecommerce_assets" {
  bucket = aws_s3_bucket.ecommerce_assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "ecommerce_assets" {
  bucket = aws_s3_bucket.ecommerce_assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# CloudFront distribution for CDN
resource "aws_cloudfront_distribution" "ecommerce_cdn" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "E-commerce CDN for ${var.environment}"
  default_root_object = "index.html"
  
  origin {
    domain_name = aws_s3_bucket.ecommerce_assets.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.ecommerce_assets.id}"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.ecommerce_oai.cloudfront_access_identity_path
    }
  }
  
  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.ecommerce_assets.id}"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }
  
  price_class = "PriceClass_100"
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  tags = {
    Environment = var.environment
  }
}

# Origin Access Identity for CloudFront
resource "aws_cloudfront_origin_access_identity" "ecommerce_oai" {
  comment = "OAI for e-commerce assets"
}

# Bucket policy to allow CloudFront access
resource "aws_s3_bucket_policy" "ecommerce_assets" {
  bucket = aws_s3_bucket.ecommerce_assets.id
  policy = data.aws_iam_policy_document.ecommerce_assets.json
}

data "aws_iam_policy_document" "ecommerce_assets" {
  statement {
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.ecommerce_oai.iam_arn]
    }
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.ecommerce_assets.arn}/*"]
  }
}

data "aws_caller_identity" "current" {}