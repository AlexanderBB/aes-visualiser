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
    return response(app, event, context)