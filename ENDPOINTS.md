# Endpoints
## Auth-related endpoints
### Signup
Signup for a non-super user on http://localhost:8000/auth/signup/ . Django server must be up and running.

### Login
Request:
```
curl --request POST \
  --url http://localhost:8000/auth/login/ \
  --header 'Content-Type: multipart/form-data' \
  --header 'User-Agent: insomnia/10.3.0' \
  --form username=<username> \
  --form password=<password>
```

Response:
```
"{"token":"<YOUR_AUTH_TOKEN>"}"
```

### Logout
Request:
```
curl --request DELETE \
  --url http://localhost:8000/auth/logout/ \
  --header 'Authorization: Token de8de29cfee6b167cabaf2ad089648860b96c3d1' \
  --header 'User-Agent: insomnia/10.3.0'
```

Response:
```
{ Union["Invalid token", "...logged out", "Goodbye"] }
```


## Trade-related endpoints

### 1) Load portfolio
Request:
```
curl --request GET \
  --url http://localhost:8000/portfolio/ \
  --header 'Authorization: Token <YOUR_AUTH_TOKEN>' \
  --header 'User-Agent: insomnia/10.3.0'
```

Response:
```
{
    "APPL": {
        "total_value": 600.0,
        "total_quantity": 300,
        "price": 2.0
    },
    "GOOG": {
        "total_value": 50.0,
        "total_quantity": 50,
        "price": 1.0
    },
    "TSLA": {
        "total_value": 213.77,
        "total_quantity": 1,
        "price": 213.77
    }
}
```


### 2) Single Trade
Request:
```
curl --request POST \
  --url http://localhost:8000/trade/ \
  --header 'Authorization: Token <YOUR_AUTH_TOKEN>' \
  --header 'Content-Type: multipart/form-data' \
  --header 'User-Agent: insomnia/10.3.0' \
  --form symbol=GOOG \
  --form quantity=100 \
  --form action=buy
```

Possible Response: Sucesss
```
{
    "message": "100 shares of GOOG bought"
}
```

Possible Response: Failure
```
{
    "symbol": [
        "no symbol provided"
    ],
    "quantity": [
        "quantity must be a number"
    ],
    "action": [
        "action should be only one of ['buy', 'sell']"
    ]
}
```

Possible Response: Failure
```
{
    "sell": [
        "Trying to sell 300 shares of GOOG, but user only owns 250 shares"
    ]
}
```


### 3) Bulk Trade
This one is tricky because you need to provide the filename inside the `Content-Disposition` header,
while also providing the data as a hash for the `--data` flag

Request:
```
curl --request POST \
  --url http://localhost:8000/bulk_trade/ \
  --header 'Authorization: Token <YOUR_AUTH_TOKEN>' \
  --header 'Content-Disposition: form-data; name="file"; filename="<CSV_FILENAME.csv>"' \
  --header 'Content-Type: multipart/form-data' \
  --header 'User-Agent: insomnia/10.3.0' \
  --data <CSV_FILEHASH>
```

Possible Response: Failure
```
{
    "0": {
        "quantity": [
            "quantity must be a number"
        ]
    },
    "1": {
        "symbol": [
            "no symbol provided"
        ]
    },
    "2": {
        "symbol": [
            "symbol should be max 5 characters"
        ]
    },
    "3": {
        "sell": [
            "Trying to sell 2000 shares of GOOG, but user only owns 50 shares"
        ]
    }
}
```

Possible Response: Success
```
{
    "0": "25 shares of MSFT bought",
    "1": "200 shares of BRK bought",
    "2": "5 shares of DOGE bought",
    "3": "10 shares of GOOG sold"
}
```
