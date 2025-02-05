from django.contrib.auth import get_user_model

UserModel = get_user_model()
name_and_pw = "foobar"
if not UserModel.objects.filter(username=name_and_pw).exists():
    user = UserModel.objects.create_user(name_and_pw, password=name_and_pw)
    user.is_superuser = False
    user.is_staff = False
    user.save()
