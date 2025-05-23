from awsgi import response
from app import app

def normalize_event(event):
    """Normalize AWS Function URL event to API Gateway v1 style."""
    if "httpMethod" not in event and "requestContext" in event and "http" in event["requestContext"]:
        event["httpMethod"] = event["requestContext"]["http"]["method"]
        event["path"] = event["rawPath"]
        event["queryStringParameters"] = {}
        event["headers"] = event.get("headers", {})
    return event


def handler(event, context):
    """AWS Lambda handler function."""
    event = normalize_event(event)
    # Specify binary content types that should be base64 encoded
    binary_content_types = [
        'image/png',
        'image/jpeg',
        'image/gif',
        'image/webp',
        'image/svg+xml',
        'image/x-icon',
        'application/octet-stream',
        'application/pdf',
        'font/woff',
        'font/woff2'
    ]
    return response(app, event, context, base64_content_types=binary_content_types)
