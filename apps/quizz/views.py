import json
import random

from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response, redirect
from .forms import (
    CreateGameForm, CreateGameFormWithNickname, NicknameForm,
    PasswordNicknameForm, render_form
)
from .models import Game, Category, Player
from .sockets import QuizzNamespace

MAX_DIFFICULTY = 15
CALL_A_FRIEND_MAX_CONFIDENCE = 95
CALL_A_FRIEND_MIN_CONFIDENCE = 5

RANDOM_NAMES = [
    'Robert', 'Cersei', 'Joffrey', 'Ned', 'Jon', 'Bran', 'Catelyn', 'Brienne',
    'Aerys', 'Daenerys', 'Loras', 'Edmure', 'Rickon', 'Jaime', 'Sansa', 'Arya',
    'Davos', 'Tyrion'
]


def render_to_json_response(context, **response_kwargs):
    data = json.dumps(context)
    response_kwargs['content_type'] = 'application/json'
    return HttpResponse(data, **response_kwargs)


def home(request):
    player_id = request.session.get('player_id', None)

    if (player_id is not None
            and Player.objects.filter(pk=player_id).count() > 0):
        form_class = CreateGameForm
        player = Player.objects.get(pk=player_id)
    else:
        # Initialize session
        request.session['player_id'] = None
        form_class = CreateGameFormWithNickname
        player = None

    game_form = form_class(initial={
        'nickname': random.choice(RANDOM_NAMES),
        'categories': [Category.objects.all()[0]],
    })

    nickname_form = PasswordNicknameForm()

    return render_to_response('base.html', {
        'categories': Category.objects.all(),
        'create_game_form': game_form,
        'nickname_form': nickname_form,
        'player_id': player_id,
    }, RequestContext(request))


def game_create(request):
    player_id = request.session.get('player_id', None)

    if (player_id is not None
            and Player.objects.filter(pk=player_id).count() > 0):
        form_class = CreateGameForm
        player = Player.objects.get(pk=player_id)
    else:
        form_class = CreateGameFormWithNickname
        player = None

    game_form = form_class(request.POST)

    if game_form.is_valid():
        if player is None:
            player = Player.objects.create(
                name=game_form.cleaned_data['nickname']
            )
            request.session['player_id'] = player.id

        game = Game.objects.create(
            max_players=game_form.cleaned_data['max_players'],
            owner=player,
        )

        if game_form.cleaned_data['password']:
            game.password = make_password(
                game_form.cleaned_data['password']
            )
            game.save()

        for category in game_form.cleaned_data['categories']:
            game.categories.add(category)

        player.game = game
        player.save()

        return render_to_json_response({
            'pk': game.pk,
        })

    return render_to_json_response({
        'form': render_form(game_form)
    }, status=400)


def game_detail(request, id):
    game = get_object_or_404(Game, pk=id)
    player = None

    form_class = NicknameForm if not game.password else PasswordNicknameForm

    if request.method == "POST":
        nickname_form = form_class(request.POST)

        if game.password:
            nickname_form.game_password = game.password

        if nickname_form.is_valid():
            player = Player.objects.create(
                name=nickname_form.cleaned_data['nickname'],
                game=game
            )
            request.session['player_id'] = player.id

            url_parameters = {'id': game.id}

            return redirect(reverse('game_detail', kwargs=url_parameters))
    else:
        if 'player_id' in request.session:
            player = Player.objects.get(pk=request.session['player_id'])

        if (game.status != Game.STATUS_WAITING
                and (player is None or player.game_id != game.id)):
            raise PermissionDenied

        if player is not None:
            player.game = game
            player.save()

        nickname_form = form_class(initial={
            'nickname': random.choice(RANDOM_NAMES),
        })

    return render_to_response('game_detail.html', {
        'game': game,
        'nickname_form': nickname_form,
        'player': player,
    }, RequestContext(request))

#def call_a_friend(question):
#    confidence = question.difficulty * (CALL_A_FRIEND_MAX_CONFIDENCE -
#            CALL_A_FRIEND_MIN_CONFIDENCE) / (MAX_DIFFICULTY - 1)
#    friend_is_right = random.randrange(confidence_min, confidence_max)


def game_info(request, id):
    game = get_object_or_404(Game, pk=id)

    return render_to_json_response({
        'needs_password': game.password != ''
    })
