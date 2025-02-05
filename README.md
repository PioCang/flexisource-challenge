# flexisource-challenge

## IMPORTANT: Design decisions
I've made the following decisions in order to accelerate and simplify the logic
of the app without contravening the bullet points laid out in the Coding Challenge
Document. Admittedly, these design decisions are ***frankly absurd*** for a
trading app. These premises that do not hold in the real world (and would be
catastrophic to the concept of finance as we know it).

1. Users have unlimited purchasing power.
2. Stocks have an unlimited number for shares for trading.
3. The value of the stocks remain constant.
4. A user can unilaterally buy or sell a stock anytime i.e., no counterparty.
5. No fractional shares are allowed to be bought or sold.
6. The market is always open for trading.
7. If a user attempts to buy an unrecognized stock, the stock will be created instantaneously with a randomized price. Essentially, this means the user can buy any stock out of thin air.
8. A user can only sell whatever quantity he has previously owned of a stock.
9. The holdings of a user are calculated by tracing the trades throughout history. The holdings are not saved into database, and so are recalculated each time.


## 1 Prepping the venv to run the server
Let's prep a virtual env. I assume you have **pyenv** installed.
For a small application, I want to avoid the memory requirements of Dockerizing
this app.

1. Create a virtualenv to sandbox all Pip changes
```bash
newvenv flexisource 3.11.3
pyenv activate flexisource
```

2. Clone the repository and enter the project folder
```bash
git clone https://github.com/PioCang/flexisource-challenge.git
```

3. We run everything inside this folder
```bash
cd flexisource-challenge/flexisource/
```

4. Install the requirements. (Ensure the `fleixsource` virtual env is activated.)
```bash
pip install -r requirements
```

5. Create a `.env` file inside **flexisource-challenge/flexisource/**
```bash
echo "SECRET_KEY=\"django-insecure-any-random-string\"\nDEBUG=True" > test
```

5. Run the migrations
```bash
python manage.py migrate
```

6. [Optional step] create a superuser. It's not necessary, but you can do so if you wish.
Run this command and follow the prompts
```
python manage.py createsuperuser
```

7. Run the server
```
python manage.py runserver 8000
```


## 2 Using the app's APIs
Please refer to [ENDPOINTS.md](./ENDPOINTS.md)
I've also attached an HTTP Archive File for Insomnia / Postman [endpoints_requests.har](endpoints_requests.har) so it's easier to follow / use the endpoints.


## 3 Teardown
1. Stop the Django server with `Ctrl + C`
2. Delete the environment with
```
pyenv virtualenv-delete flexisource
```
3. Delete the `flexisource-challenge` folder

# -- END
