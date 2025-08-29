# Crypto Tracker

Crypto Tracker is a web application that allows users to set price alerts for cryptocurrencies. When a coin's price crosses a user-defined threshold, an email notification is sent.

## Features

- Set alerts for any coin and price threshold
- Receive email notifications when conditions are met
- Simple React frontend
- AWS Lambda backend with DynamoDB and SNS

## Project Structure

```
frontend/         # React frontend
lambda/           # AWS Lambda functions
```

## Getting Started

### Frontend

1. Install dependencies:
    ```sh
    cd frontend
    npm install
    ```
2. Start the development server:
    ```sh
    npm start
    ```
3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Backend (AWS Lambda)

- Deploy the Lambda functions in `lambda/save_threshold/` and `lambda/check_prices/` to AWS.
- Ensure a DynamoDB table named `PriceAlerts` exists.
- Set up AWS SNS for email notifications.


## API Endpoints

- `POST /set-alert` — Set a price alert (see [lambda/save_threshold/save_threshold.py](lambda/save_threshold/save_threshold.py))
- Scheduled trigger — Checks prices and sends notifications (see [lambda/check_prices/check_prices.py](lambda/check_prices/check_prices.py))
