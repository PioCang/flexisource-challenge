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
### Single Trade
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

Possible Responses:
```
{
    "message": "100 shares of GOOG bought"
}
```
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
```
{
    "sell": [
        "Trying to sell 300 shares of GOOG, but user only owns 250 shares"
    ]
}
```
