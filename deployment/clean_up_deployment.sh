#!/bin/bash

set -e

# ==== Потребителски настройки ====
LAMBDA_FUNCTION_NAME="aes-visualiser"
LAYER_NAME="aes-visualiser-layer"
ROLE_NAME="aes-visualiser-role"
AWS_REGION="eu-west-1"
# ==================================

# 1. Изчистване на Function URL
echo "🔗 Deleting Function URL if exists..."
aws lambda delete-function-url-config \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --region "$AWS_REGION" || true

# 2. Изтриване на Lambda функцията
echo "🗑️ Deleting Lambda function..."
aws lambda delete-function \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --region "$AWS_REGION" || true

# 3. Изтриване на всички версии на Layer
echo "🗑️ Deleting all Lambda Layer versions..."
LAYER_VERSIONS=$(aws lambda list-layer-versions \
  --layer-name "$LAYER_NAME" \
  --region "$AWS_REGION" \
  --query 'LayerVersions[].Version' \
  --output text 2>/dev/null || true)

for version in $LAYER_VERSIONS; do
  echo "   ➔ Deleting Layer version $version..."
  aws lambda delete-layer-version \
    --layer-name "$LAYER_NAME" \
    --version-number "$version" \
    --region "$AWS_REGION" || true
done

# 4. Премахване на IAM роля
echo "🔒 Deleting IAM role if exists..."
aws iam detach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole || true

aws iam delete-role \
  --role-name "$ROLE_NAME" || true

# 5. Финално съобщение
echo ""
echo "✅ Cleanup completed successfully!"