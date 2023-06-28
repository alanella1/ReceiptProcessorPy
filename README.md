# Receipt API

This is a Flask-based RESTful API for managing receipts. It provides endpoints for creating and retrieving receipts, as well as calculating reward points for each receipt.

## Getting Started

To run the Receipt API locally, follow the steps below.

### Prerequisites

- Docker

### Build the Docker Container

1. Clone the repository to your local machine.
2. Open a terminal and navigate to the project directory.
3. Build the Docker container by running the following command:

`docker build -t myapp:latest .`

### Run the Docker Container

Once the Docker container is built, you can run it using the following steps:

1. Start the Docker container by running the following command:

`docker run -p 5000:5000 myapp:latest`

This command starts the container and maps port 5000 of the container to port 5000 of your local machine.

### Run the Unit Tests

To run the unit tests for the Flask Receipt API, follow these steps:

1. Open a new terminal.
2. Navigate to the project directory.
3. Run the following commands:

`docker ps` to get the container ID for the next step

`docker exec {container_id} python -it test_server.py`

You should then see the following output

```
.............
----------------------------------------------------------------------
Ran 13 tests in 0.010s

OK
```

### Test the Endpoints with cURL

You can use cURL to test the GET and POST endpoints of the Flask Receipt API. Here's an example:

- To create a receipt (cURL):
```
curl --location 'http://localhost:5000/receipts/process' \
--header 'Content-Type: application/json' \
--data '{
    "retailer": "Target",
    "purchaseDate": "2022-01-01",
    "purchaseTime": "13:01",
    "items": [
        {
            "shortDescription": "Mountain Dew 12PK",
            "price": "6.49"
        },
        {
            "shortDescription": "Emils Cheese Pizza",
            "price": "12.25"
        },
        {
            "shortDescription": "Knorr Creamy Chicken",
            "price": "1.26"
        },
        {
            "shortDescription": "Doritos Nacho Cheese",
            "price": "3.35"
        },
        {
            "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
            "price": "12.00"
        }
    ],
    "total": "35.35"
}'
```

To create a receipt (Powershell)
```
$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("Content-Type", "application/json")

$body = @"
{
    `"retailer`": `"Target`",
    `"purchaseDate`": `"2022-01-01`",
    `"purchaseTime`": `"13:01`",
    `"items`": [
        {
            `"shortDescription`": `"Mountain Dew 12PK`",
            `"price`": `"6.49`"
        },
        {
            `"shortDescription`": `"Emils Cheese Pizza`",
            `"price`": `"12.25`"
        },
        {
            `"shortDescription`": `"Knorr Creamy Chicken`",
            `"price`": `"1.26`"
        },
        {
            `"shortDescription`": `"Doritos Nacho Cheese`",
            `"price`": `"3.35`"
        },
        {
            `"shortDescription`": `"   Klarbrunn 12-PK 12 FL OZ  `",
            `"price`": `"12.00`"
        }
    ],
    `"total`": `"35.35`"
}
"@

$response = Invoke-RestMethod 'http://localhost:5000/receipts/process' -Method 'POST' -Headers $headers -Body $body
$response | ConvertTo-Json
```


Then, to read back the points for that receipt

cURL:

`curl --location 'http://localhost:5000/receipts/{your_id}/points'`

powershell: 

```
$response = Invoke-RestMethod 'http://localhost:5000/receipts/{your_id}/points' -Method 'GET' -Headers $headers
$response | ConvertTo-Json
```


