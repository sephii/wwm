from django import forms
from .models import Category


class CreateGameForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all()
    )
    max_players = forms.IntegerField(max_value=10, min_value=1, initial=4)
    is_private = forms.BooleanField(required=False)


class CreateGameFormWithNickname(CreateGameForm):
    nickname = forms.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        super(CreateGameFormWithNickname, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['nickname', 'categories', 'max_players',
                                'is_private']


class NicknameForm(forms.Form):
    nickname = forms.CharField(max_length=20)
