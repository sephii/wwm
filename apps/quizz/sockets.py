import logging

from django.contrib.sessions.models import Session
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from socketio.sdjango import namespace

from .mixins import GameMixin
from .models import Game, Player


@namespace('/quizz')
class QuizzNamespace(BaseNamespace, GameMixin, BroadcastMixin):
    def __init__(self, *args, **kwargs):
        self.game = None
        self.player = None
        self.nickname = None

        super(QuizzNamespace, self).__init__(*args, **kwargs)

    def initialize(self):
        self.logger = logging.getLogger("socketio.chat")
        self.log("Socketio session started")

    def log(self, message):
        self.logger.error("[{0}] {1}".format(self.socket.sessid, message))

    def get_games_list(self):
        games = Game.objects.filter(is_private=False,
                                    status=Game.STATUS_WAITING)
        return [game.to_dict() for game in games]

    def get_session(self):
        return Session.objects.get(pk=self.session['id'])

    def get_game(self):
        return Game.objects.get(pk=self.game.id)

    def send_players_list(self):
        self.emit_to_players('players_list',
                             [player.name
                              for player in self.game.players.all()])

    def on_hello(self, session=None):
        self.add_acl_method('on_create_game')
        self.add_acl_method('on_join_game')

        if session is not None:
            self.session['id'] = session

        self.emit('games_list', self.get_games_list())

    def on_join_game(self):
        player_id = self.get_session().get_decoded()['player_id']
        self.player = Player.objects.get(pk=player_id)
        self.game = self.player.game

        if self.game.status != Game.STATUS_WAITING:
            return False

        self.game.nb_players += 1
        self.game.save()

        self.join(self.game.id)
        self.emit_to_players('player_joined', self.player.name)
        self.send_players_list()

        if self.game.owner.id == self.player.id:
            self.add_acl_method('on_start_game')

        self.add_acl_method('on_answer')

        return True

    def on_start_game(self):
        self.log('starting game')

        self.emit_to_players('game_start')
        self.game = self.get_game()
        self.game.status = Game.STATUS_PLAYING
        self.game.current_question = self.game.get_question()
        self.game.current_player_id = self.player.id
        self.game.save()

        answers = self.game.current_question.get_random_answers()

        self.emit_to_players('question', self.game.current_player_id,
                             self.game.current_question.question, answers,
                             Game.LEVELS_VALUES[self.game.current_level - 1])

        return True

    def on_answer(self, answer):
        self.game = self.get_game()

        if self.game.current_player_id != self.player.id:
            return False

        if answer == self.game.current_question.answer_1:
            self.emit_to_players('correct_answer', self.player.id)
        else:
            self.emit_to_players('wrong_answer', self.player.id)

        next_player = self.game.get_next_player_id()
        self.log(next_player)
        self.game.current_player_id = next_player
        self.game.current_question = self.game.get_question()
        self.game.save()

        answers = self.game.current_question.get_random_answers()

        self.emit_to_players('question', self.game.current_player_id,
                             self.game.current_question.question, answers,
                             Game.LEVELS_VALUES[self.game.current_level - 1])

        return True

    def recv_disconnect(self):
        if self.player is not None and self.player.id:
            self.player.game.nb_players -= 1
            self.player.game = None
            self.player.save()

        if self.game is not None:
            self.emit_to_players('player_left', self.player.name)
            self.send_players_list()

        self.disconnect(silent=True)

        return True

    def get_initial_acl(self):
        return ['on_hello', 'recv_connect', 'recv_disconnect']
