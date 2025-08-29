import os
import json
import boto3
from decimal import Decimal

dynamo = boto3.resource("dynamodb")
sns = boto3.client("sns")

TABLE_NAME = os.environ.get("TABLE_NAME", "PriceAlerts")
table = dynamo.Table(TABLE_NAME)

def sanitize_topic_name(email):
    return "crypto-alert-" + "".join(c if c.isalnum() else "-" for c in email.lower())[:200]

def lambda_handler(event, context):
    # Always return these headers for CORS
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }

    # Handle preflight OPTIONS request
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": ""
        }

    # Handle POST request
    try:
        body = json.loads(event.get("body", "{}"))
        userEmail = body.get("userEmail")
        coin = body.get("coin")
        condition = body.get("condition")
        price = body.get("price")

        if not userEmail or not coin or not condition or price is None:
            return {"statusCode": 400, "headers": headers,
                    "body": json.dumps({"error": "Missing required fields"})}

        coin_lower = coin.lower()
        topic_name = sanitize_topic_name(userEmail)

        topic = sns.create_topic(Name=topic_name)
        topic_arn = topic["TopicArn"]
        sns.subscribe(TopicArn=topic_arn, Protocol="email", Endpoint=userEmail)

        table.put_item(Item={
            "coin": coin_lower,
            "userEmail": userEmail,
            "condition": condition,
            "price": Decimal(str(price)),
            "topicArn": topic_arn
        })

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"message": "Alert saved. Confirm subscription in your email.", "topicArn": topic_arn})
        }

    except Exception as e:
        return {"statusCode": 500, "headers": headers, "body": json.dumps({"error": str(e)})}
