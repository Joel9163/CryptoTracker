import os
import json
import boto3
import requests

dynamo = boto3.resource("dynamodb")
sns = boto3.client("sns")

TABLE_NAME = os.environ.get("TABLE_NAME", "PriceAlerts")
table = dynamo.Table(TABLE_NAME)

def fetch_prices(coins):
    ids = ",".join(coins)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def lambda_handler(event, context):
    try:
        # get all coins
        coins_set = set()
        scan_kwargs = {"ProjectionExpression": "coin"}
        done = False
        start_key = None

        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = table.scan(**scan_kwargs)
            for item in response.get("Items", []):
                coins_set.add(item["coin"])
            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None

        coins = list(coins_set)
        if not coins:
            return {"statusCode": 200, "body": json.dumps({"message": "No alerts configured"})}

        prices = fetch_prices(coins)

        # check thresholds
        for coin in coins:
            resp = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key("coin").eq(coin))
            current_price = prices.get(coin, {}).get("usd")
            if current_price is None:
                continue

            for alert in resp.get("Items", []):
                cond = alert["condition"]
                threshold = float(alert["price"])
                triggered = False
                if cond == "above" and current_price > threshold:
                    triggered = True
                if cond == "below" and current_price < threshold:
                    triggered = True

                if triggered:
                    topic_arn = alert.get("topicArn")
                    if topic_arn:
                        message = f"Alert: {coin} is {cond} {threshold}. Current price: ${current_price}"
                        sns.publish(TopicArn=topic_arn, Subject=f"Crypto alert: {coin}", Message=message)

        return {"statusCode": 200, "body": json.dumps({"message": "Check complete", "coins": coins})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
