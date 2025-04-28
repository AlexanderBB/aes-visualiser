#!/bin/bash

set -e

# ==== Потребителски настройки ====
LAMBDA_FUNCTION_NAME="aes-visualiser"
LAYER_NAME="aes-visualiser-layer"
ROLE_NAME="aes-visualiser-role"
AWS_REGION="eu-west-1"
RUNTIME="python3.12"
# ==================================

# 1. Почистване
echo "🧹 Cleaning old builds..."
rm -rf layer deployment.zip layer.zip

# 2. Инсталиране на зависимости
echo "📦 Installing dependencies from requirements.txt into layer/python..."
mkdir -p layer/python
pip install -r requirements.txt -t layer/python

# 3. Пакетиране на layer.zip
echo "🗜️ Creating layer.zip..."
cd layer
zip -r9 ../layer.zip .
cd ..

# 4. Проверка дали Layer съществува
echo "🔎 Checking if existing layer version exists..."
EXISTING_LAYER_ARN=$(aws lambda list-layer-versions \
  --layer-name "$LAYER_NAME" \
  --region "$AWS_REGION" \
  --query 'LayerVersions[0].LayerVersionArn' \
  --output text 2>/dev/null || true)

if [ "$EXISTING_LAYER_ARN" == "None" ] || [ -z "$EXISTING_LAYER_ARN" ]; then
    echo "❌ No existing Layer. Uploading new layer..."
    UPLOAD_NEW_LAYER=true
else
    echo "✅ Existing Layer found: $EXISTING_LAYER_ARN"
    UPLOAD_NEW_LAYER=false
fi

# 5. Качване на Layer ако е нужно
if [ "$UPLOAD_NEW_LAYER" = true ]; then
    echo "🚀 Publishing new Lambda Layer version..."
    LAYER_VERSION_ARN=$(aws lambda publish-layer-version \
      --layer-name "$LAYER_NAME" \
      --description "Layer for AES Visualiser App" \
      --zip-file fileb://layer.zip \
      --compatible-runtimes "$RUNTIME" \
      --region "$AWS_REGION" \
      --query 'LayerVersionArn' --output text)
else
    LAYER_VERSION_ARN=$EXISTING_LAYER_ARN
fi

echo "✅ Using Layer ARN: $LAYER_VERSION_ARN"

# 6. Проверка за IAM роля
echo "🔎 Checking if IAM role exists..."
if aws iam get-role --role-name "$ROLE_NAME" > /dev/null 2>&1; then
    echo "✅ IAM role exists."
else
    echo "✨ IAM role not found. Creating a new role..."
    TRUST_POLICY='{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "lambda.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }'
    aws iam create-role \
      --role-name "$ROLE_NAME" \
      --assume-role-policy-document "$TRUST_POLICY" > /dev/null

    echo "🔗 Attaching AWSLambdaBasicExecutionRole policy..."
    aws iam attach-role-policy \
      --role-name "$ROLE_NAME" \
      --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    echo "⌛ Waiting 10 seconds for IAM role propagation..."
    sleep 10
fi

# Получаване на ARN на ролята
ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)

# 7. Проверка дали Lambda функцията съществува
echo "🔎 Checking if Lambda function exists..."
if aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" --region "$AWS_REGION" > /dev/null 2>&1; then
    echo "🔄 Function exists. Updating configuration..."
    aws lambda update-function-configuration \
      --function-name "$LAMBDA_FUNCTION_NAME" \
      --layers "$LAYER_VERSION_ARN" \
      --region "$AWS_REGION"
else
    echo "✨ Function does not exist. Creating a new function..."
    zip -r deployment.zip app.py templates/ static/
    aws lambda create-function \
      --function-name "$LAMBDA_FUNCTION_NAME" \
      --runtime "$RUNTIME" \
      --role "$ROLE_ARN" \
      --handler "app.handler" \
      --layers "$LAYER_VERSION_ARN" \
      --zip-file fileb://deployment.zip \
      --region "$AWS_REGION"
fi

# 8. Пакетиране на приложението
echo "🗜️ Creating deployment.zip..."
zip -r deployment.zip app.py templates/ static/

# 9. Ъпдейтване на кода на Lambda функцията
echo "🚀 Updating Lambda function code..."
aws lambda update-function-code \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --zip-file fileb://deployment.zip \
  --region "$AWS_REGION"

# 10. Проверка за Function URL
echo "🔎 Checking for Function URL..."
FUNCTION_URL=$(aws lambda get-function-url-config \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --region "$AWS_REGION" \
  --query 'FunctionUrl' \
  --output text 2>/dev/null || true)

if [ -z "$FUNCTION_URL" ]; then
    echo "🔗 Function URL not found. Creating one..."
    FUNCTION_URL=$(aws lambda create-function-url-config \
      --function-name "$LAMBDA_FUNCTION_NAME" \
      --auth-type NONE \
      --cors '{
         "AllowOrigins": ["*"],
         "AllowMethods": ["*"],
         "AllowHeaders": ["*"]
      }' \
      --region "$AWS_REGION" \
      --query 'FunctionUrl' \
      --output text)
fi

# 11. Финално съобщение
echo ""
echo "🎉 Full Smart Deployment Complete!"
echo "🌐 Your Lambda Function URL:"
echo "$FUNCTION_URL"

# 12. Автоматичен тест с curl
echo ""
echo "🧪 Running test request to your Lambda Function URL..."
sleep 2
HTTP_RESPONSE=$(curl -s -o /tmp/curl_output.txt -w "%{http_code}" "$FUNCTION_URL")

if [ "$HTTP_RESPONSE" -ge 200 ] && [ "$HTTP_RESPONSE" -lt 300 ]; then
    echo "✅ Test Passed! Server responded with HTTP $HTTP_RESPONSE"
    echo "📄 Response content:"
    cat /tmp/curl_output.txt
else
    echo "❌ Test Failed! Server responded with HTTP $HTTP_RESPONSE"
    echo "📄 Response content:"
    cat /tmp/curl_output.txt
    exit 1
fi