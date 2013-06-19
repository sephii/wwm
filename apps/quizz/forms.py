from django import forms
from django.contrib.auth.hashers import check_password
from django.template.loader import render_to_string
from .models import Category


class CreateGameForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all()
    )
    max_players = forms.IntegerField(max_value=10, min_value=1, initial=4)
    password = forms.CharField(required=False)


class CreateGameFormWithNickname(CreateGameForm):
    nickname = forms.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        super(CreateGameFormWithNickname, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['nickname', 'categories', 'max_players',
                                'password']


class NicknameForm(forms.Form):
    nickname = forms.CharField(max_length=20)


class PasswordNicknameForm(NicknameForm):
    password = forms.CharField()

    def clean(self):
        cleaned_data = super(PasswordNicknameForm, self).clean()
        password = cleaned_data.get('password')

        if not check_password(password, self.game_password):
            msg = u"The password is not valid."
            self._errors['password'] = self.error_class([msg])

            del cleaned_data['password']

        return cleaned_data


def render_form(form):
    return render_to_string('form.html', {'form': form})
