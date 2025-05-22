# AES-128 Web Visualizer 🔒✨

An interactive web application that visualizes the complete AES-128 encryption process step by step. The application accepts a 16-byte plaintext and a 16-byte key, and shows all transformations and rounds of the AES algorithm with detailed explanations.

Deployed as an AWS Lambda function with Function URL, built with Flask.

## 📋 Key Features

- **Complete AES-128 Visualization**: Shows all steps from initial state to final encrypted output
- **Detailed Step Explanations**: Each transformation is explained with before/after states
- **Matrix Transformations**: Visualizes how plaintext and key are converted to matrices
- **All AES Operations**: SubBytes, ShiftRows, MixColumns, AddRoundKey for all rounds
- **Night Mode Support**: Toggle between light and dark themes for comfortable viewing
- **Responsive Design**: Works on desktop and mobile devices
- **Comprehensive Testing**: Includes unit tests to verify encryption correctness
- **One-Click Deployment**: Automated AWS Lambda deployment script

## 🎬 Live Demo

See the application in action:

👉 [Live Demo of AES-128 Web Visualizer](https://aes.visualise.click/)

## 🛠️ Technologies

- Python 3.12
- Flask 3.1.0
- AWS Lambda (Function URL)
- AWS Lambda Layers
- AWS CLI for deployment
- pytest for testing

## 🚀 Quick Start (AWS Lambda Deployment)

### Option 1: Manual Deployment

#### 1. Prerequisites

Ensure you have installed:

- Python 3.12+
- pip
- AWS CLI
- zip

And importantly:

- AWS CLI configured with valid credentials via `aws configure`

#### 2. Clone the Project

```bash
git clone https://github.com/your-username/aes-visualiser.git
cd aes-visualiser
```

#### 3. Deploy to Lambda (One-click)

Run the deployment script:

```bash
bash deployment/full_deployment.sh
```

The script will:
1. Run tests to ensure everything works correctly
2. Create a Lambda Layer with all dependencies
3. Create or update the Lambda function
4. Configure a public Function URL
5. Test the deployment

#### 4. Result

After a few seconds, you'll get:

```bash
🎉 Full Smart Deployment Complete!
🌐 Your Lambda Function URL:
https://abcde12345.lambda-url.eu-west-1.on.aws/

✅ Test Passed! Server responded with HTTP 200
```

### Option 2: GitHub Actions Deployment

This project includes a GitHub Actions workflow for automated deployment to AWS Lambda using IAM role assumption.

#### 1. Set up AWS IAM Role for GitHub Actions

1. Create an IAM role in your AWS account that GitHub Actions can assume:

```bash
# Create a trust policy file
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>:*"
        }
      }
    }
  ]
}
EOF

# Create the role
aws iam create-role --role-name GitHubActionsAESVisualiser \
  --assume-role-policy-document file://trust-policy.json

# Attach necessary policies
aws iam attach-role-policy --role-name GitHubActionsAESVisualiser \
  --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess

aws iam attach-role-policy --role-name GitHubActionsAESVisualiser \
  --policy-arn arn:aws:iam::aws:policy/IAMFullAccess
```

2. Get the ARN of the created role:

```bash
aws iam get-role --role-name GitHubActionsAESVisualiser --query 'Role.Arn' --output text
```

#### 2. Configure GitHub Repository

1. In your GitHub repository, go to Settings > Secrets and variables > Actions
2. Add a new repository secret:
   - Name: `AWS_ROLE_TO_ASSUME`
   - Value: The ARN of the IAM role you created (e.g., `arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:role/GitHubActionsAESVisualiser`)

#### 3. Trigger the Deployment

The GitHub Actions workflow will automatically run when you push to the `main` branch. You can also manually trigger it:

1. Go to the "Actions" tab in your GitHub repository
2. Select the "Deploy to AWS Lambda" workflow
3. Click "Run workflow" and select the branch you want to deploy from

#### 4. Deployment Results

After the workflow completes successfully:
1. The Lambda function will be deployed or updated
2. A Function URL will be created if it doesn't exist
3. The workflow output will show the Function URL where your application is accessible

## 🧪 Testing

The project includes comprehensive tests for all aspects of the AES implementation:

```bash
# Run tests
pytest tests/test_aes.py
```

Tests cover:
- Matrix transformation functions
- Individual AES operations (SubBytes, ShiftRows, MixColumns, AddRoundKey)
- Key expansion algorithm
- Complete encryption process
- Comparison with OpenSSL's implementation

## 📁 Project Structure

```
aes-visualiser/
├── app.py                # Main Flask application with routes and visualization logic
├── aes_lib.py            # AES encryption implementation and utility functions
├── lambda_handler.py     # AWS Lambda handler functions
├── templates/            # HTML templates
│   ├── landing.html      # Input form for plaintext and key
│   ├── visualize.html    # Visualization of encryption steps
│   └── partials/         # Partial templates for reusable components
│       ├── mix_columns.html    # Template for MixColumns explanation
│       └── key_expansion.html  # Template for key expansion explanation
├── static/               # CSS/JS files
│   ├── styles.css        # Styling with light/dark mode support
│   └── script.js         # Client-side functionality
├── tests/                # Test files
│   └── test_aes.py       # Unit tests for AES implementation
├── deployment/           # Deployment scripts
│   └── full_deployment.sh # AWS Lambda deployment script
├── .github/              # GitHub configuration
│   └── workflows/        # GitHub Actions workflows
│       └── aws-deploy.yml # AWS Lambda deployment workflow
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## 💡 Usage

1. Open the application in your browser
2. Enter a 16-character plaintext and a 16-character key
3. Click "Visualize Encryption" to see the step-by-step process
4. Toggle between light and dark modes using the button in the top-right corner
5. View details for each step by clicking the "View Details" button
6. Copy the details to clipboard using the copy button

## 🔄 Recent Improvements

The project has undergone several improvements to enhance code quality, maintainability, and testability:

1. **Improved Code Organization**
   - Separated AWS Lambda handler functions into a dedicated `lambda_handler.py` file
   - Moved HTML generation code from Python to Jinja2 templates
   - Created reusable template partials for complex visualizations

2. **Enhanced Testing**
   - Improved test robustness with proper handling of missing dependencies
   - Added predefined test values instead of relying on implementation
   - Made OpenSSL comparison tests more resilient

3. **Template Improvements**
   - Added custom Jinja2 filter for hex formatting
   - Created partial templates for MixColumns and key expansion explanations
   - Improved separation of concerns between logic and presentation

4. **Code Optimization**
   - Removed duplicate code in various functions
   - Improved parameter handling with proper None checks
   - Enhanced code readability and maintainability

## ⚡ Troubleshooting

| Problem | Solution |
|:--------|:---------|
| Missing AWS credentials | Run `aws configure` |
| `No module named flask` in Lambda | Check if the Layer was created correctly |
| `AccessDeniedException` | Check if the IAM user has the necessary permissions |
| Function URL returns nothing | Wait a few seconds after the first deployment |
| Tests failing | Ensure you have pytest installed (`pip install pytest`) |

## 👨‍💻 Author

**Aleksandar Boyadzhiev - [LinkedIn](https://www.linkedin.com/in/aleksandar-boyadzhiev-59087871/)**
