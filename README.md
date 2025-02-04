# flexisource-challenge

## 1 Prepping virtual env
Let's prep a virtual env. I assume you have **pyenv** installed.
For a small application, I want to avoid the memory requirements of Dockerizing
this app.

1. Create a virtualenv to sandbox all Pip changes
```bash
newvenv flexisource 3.11.3
pyenv activate flexisource
```

2. Clone the repository
```
git clone https://github.com/PioCang/flexisource-challenge.git
cd flexisource-challenge/flexisource/
```

3. Create a `.env` file inside **flexisource-challenge/flexisource/**
```bash
echo "SECRET_KEY=\"django-insecure-any-random-string\"\nDEBUG=True" > test
```

4. Run the server
```
python manage.py runserver
```












## N Teardown
1. Stop the Django server with `Ctrl + C`
2. Delete the environment with
```
pyenv virtualenv-delete flexisource
```
