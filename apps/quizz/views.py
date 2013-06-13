from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from .models import Game, Category
from .sockets import QuizzNamespace

MAX_DIFFICULTY = 15
CALL_A_FRIEND_MAX_CONFIDENCE = 95
CALL_A_FRIEND_MIN_CONFIDENCE = 5


def home(request):
    return render_to_response('base.html', {
        'categories': Category.objects.all()
    }, RequestContext(request))


def game(request, id):
    g = Game.objects.get(pk=id)

    return render_to_response('game.html', {
        'game': g
    }, RequestContext(request))

#def call_a_friend(question):
#    confidence = question.difficulty * (CALL_A_FRIEND_MAX_CONFIDENCE -
#            CALL_A_FRIEND_MIN_CONFIDENCE) / (MAX_DIFFICULTY - 1)
#    friend_is_right = random.randrange(confidence_min, confidence_max)
