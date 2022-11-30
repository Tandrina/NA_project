from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django import forms

from allauth.account.forms import SignupForm


class BaseRegisterForm(UserCreationForm):
    # переопределяю поля, уже указанные в модели User
    first_name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилия')
    email = forms.EmailField(label='email')

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )


# форма для автоматического добавления пользователей при авторизации в группу common
class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user
