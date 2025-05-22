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

### 1. Prerequisites

Ensure you have installed:

- Python 3.12+
- pip
- AWS CLI
- zip

And importantly:

- AWS CLI configured with valid credentials via `aws configure`

### 2. Clone the Project

```bash
git clone https://github.com/your-username/aes-visualiser.git
cd aes-visualiser
```

### 3. Deploy to Lambda (One-click)

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

### 4. Result

After a few seconds, you'll get:

```bash
🎉 Full Smart Deployment Complete!
🌐 Your Lambda Function URL:
https://abcde12345.lambda-url.eu-west-1.on.aws/

✅ Test Passed! Server responded with HTTP 200
```

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
├── app.py                # Main Flask application with AES implementation
├── templates/            # HTML templates
│   ├── landing.html      # Input form for plaintext and key
│   └── visualize.html    # Visualization of encryption steps
├── static/               # CSS/JS files
│   ├── styles.css        # Styling with light/dark mode support
│   └── script.js         # Client-side functionality
├── tests/                # Test files
│   └── test_aes.py       # Unit tests for AES implementation
├── deployment/           # Deployment scripts
│   └── full_deployment.sh # AWS Lambda deployment script
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
