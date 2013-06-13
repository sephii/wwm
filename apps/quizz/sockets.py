import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from socketio.sdjango import namespace

from .mixins import GameMixin
from .models import Category, Game, Player


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

    def on_hello(self):
        self.add_acl_method('on_login')

        self.emit('games_list', self.get_games_list())

    def on_login(self, nickname):
        self.log(nickname)
        self.nickname = nickname

        self.player = Player.objects.create(name=nickname)

        self.add_acl_method('on_join')
        self.add_acl_method('on_create_game')

        return True

    def on_join(self, game_id):
        self.log(game_id)
        self.game = Game.objects.get(pk=game_id)

        self.player.game = self.game
        self.player.save()

        self.join(self.game.id)
        self.emit_to_players('player_joined', self.player.name)
        self.emit('players_list',
                  [player.name for player in self.game.players.all()])

        self.log("player {0} joined game {1}".format(self.player, self.game))

        return True

    def on_create_game(self, categories, max_players, is_private):
        self.game = Game.objects.create(max_players=max_players,
                                        is_private=is_private)

        for category in categories:
            self.game.categories.add(Category.objects.get(pk=category))

        self.add_acl_method('on_start_game')
        self.broadcast_event_not_me('games_list', self.get_games_list())

        return True

    def on_start_game(self):
        self.log('starting game')
        question = self.game.get_question()
        answers = question.get_random_answers()
        self.log(answers)

        self.emit_to_players('question', self.player.id, question.question,
                             answers)

        return True

    def recv_disconnect(self):
        if self.game is not None:
            self.emit_to_players('player_left', self.player.name)

        if self.player is not None and self.player.id:
            self.player.delete()

            if self.game.players.count() == 0:
                self.game.delete()

        self.disconnect(silent=True)

        return True

    def get_initial_acl(self):
        return ['on_hello', 'recv_connect', 'recv_disconnect']
