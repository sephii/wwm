import gevent
import logging

from django.contrib.sessions.models import Session
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from socketio.sdjango import namespace

from .mixins import GameMixin
from .models import Game, Player


logger = logging.getLogger('socketio')


@namespace('/game')
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
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def get_games_list(self):
        games = Game.objects.filter(
            status__in=[Game.STATUS_PLAYING, Game.STATUS_WAITING]
        )
        return [game.to_dict() for game in games]

    def get_session(self):
        self.log(self.session)
        return Session.objects.get(pk=self.session['id'])

    def get_game(self):
        return Game.objects.get(pk=self.game.id)

    def send_players_list(self):
        self.emit_to_players(
            'players_list',
            [dict(name=player.name) for player in self.game.players.all()]
        )

    def on_hello(self, session=None):
        self.add_acl_method('on_create_game')
        self.add_acl_method('on_join_game')
        # Not sure why but we need to repeat this
        self.add_acl_method('recv_disconnect')

        self.log('got hellooo from ' + str(self.socket.active_ns))

        if session is not None:
            self.log('received hello with session id ' + session)
            self.session['id'] = session

        return True,

    def on_create_game(self):
        self.broadcast_event_endpoint('games_list', '/games-list',
                                      self.get_games_list())

        return True

    def on_join_game(self, game_id):
        player_id = self.get_session().get_decoded()['player_id']
        self.player = Player.objects.get(pk=player_id)
        self.player.game = Game.objects.get(pk=game_id)
        self.player.save()
        self.log('player id ' + str(self.player.id))
        self.log('game ' + str(self.player.game))
        self.game = self.player.game

        self.game.nb_players += 1
        self.game.save()

        self.join(self.game.id)
        self.emit_to_players('player_joined', self.player.name)
        self.broadcast_event_endpoint('games_list', '/games-list',
                                      self.get_games_list())
        self.send_players_list()

        if self.game.owner.id == self.player.id:
            self.add_acl_method('on_start_game')

        self.add_acl_method('on_answer')

        if self.game.status == Game.STATUS_PLAYING:
            self.emit('question', {
                'id': self.game.current_player_id,
                'name': self.game.current_player.name,
            }, {
                'question': self.game.current_question.question,
                'answers': self.game.get_random_answers(),
                'value': Game.LEVELS_VALUES[self.game.current_level - 1],
                'level': self.game.current_level
            })

        return True

    def on_start_game(self):
        self.log('starting game')

        self.emit_to_players('game_start')
        self.game = self.get_game()
        self.game.status = Game.STATUS_PLAYING
        self.game.current_question = self.game.get_question()
        self.game.current_player = Player.objects.get(
            pk=self.game.get_next_player_id()
        )
        self.game.save()

        self.emit_to_players('question', {
            'id': self.game.current_player_id,
            'name': self.game.current_player.name,
        }, {
            'question': self.game.current_question.question,
            'answers': self.game.get_random_answers(),
            'value': Game.LEVELS_VALUES[self.game.current_level - 1],
            'level': self.game.current_level
        })

        return True

    def on_answer(self, answer):
        self.game = self.get_game()

        if self.game.current_player_id != self.player.id:
            return False

        self.emit_to_players_not_me('answered', answer)

        waiting_time = self.game.get_waiting_time()
        self.log('waiting {0}'.format(waiting_time))
        gevent.sleep(waiting_time)

        if self.game.is_answer_correct(answer):
            self.log('send correct')
            self.emit_to_players('correct_answer')
        else:
            self.log('send wrong')
            self.log(type(answer))
            self.log('answered "{0}", correct was "{1}"'.format(
                answer.encode('utf-8'),
                self.game.current_question.answer_1.encode('utf-8')
            ))
            self.emit_to_players('wrong_answer',
                                 self.game.current_question.answer_1)

        gevent.sleep(5)

        current_level = self.game.current_level
        next_player = Player.objects.get(pk=self.game.get_next_player_id())
        self.log(next_player)
        self.game.current_player = next_player
        self.game.current_question = self.game.get_question()
        self.game.save()

        # We went to the next level, let the others know
        if self.game.current_level > current_level:
            self.log('sending games list due to new level')
            self.broadcast_event_endpoint('games_list', '/games-list',
                                          self.get_games_list())

        self.emit_to_players('question', {
            'id': self.game.current_player_id,
            'name': self.game.current_player.name,
        }, {
            'question': self.game.current_question.question,
            'answers': self.game.get_random_answers(),
            'value': Game.LEVELS_VALUES[self.game.current_level - 1],
            'level': self.game.current_level
        })

        return True

    def recv_disconnect(self):
        user_is_still_here = False
        self.log('received disconnect from ' + str(self.socket.active_ns))

        gevent.sleep(10)

        for sessid, socket in self.socket.server.sockets.iteritems():
            if socket == self.socket:
                continue

            if 'id' in socket.session and socket.session['id'] == self.session['id']:
                user_is_still_here = True
                self.log('user ' + socket.session['id'] + ' is still here')
                break

        if not user_is_still_here:
            self.log('user ' + self.session['id'] + ' is not here')
            if self.player is not None and self.player.id:
                self.log('from ' + self.player.name)
                self.player.game.nb_players -= 1
                self.player.game.save()
                self.player.game = None
                self.player.save()

            if self.game is not None:
                self.emit_to_players('player_left', self.player.name)
                self.send_players_list()

        self.disconnect(silent=True)

        return True

    def get_initial_acl(self):
        return ['on_hello', 'recv_connect', 'recv_disconnect']

    def broadcast_event_endpoint(self, event, endpoint, *args):
        """
        This is sent to all in the sockets in this particular Namespace,
        including itself.
        """
        pkt = dict(type="event",
                   name=event,
                   args=args,
                   endpoint=endpoint)

        for sessid, socket in self.socket.server.sockets.iteritems():
            try:
                socket.send_packet(pkt)
            except KeyError:
                pass


@namespace('/games-list')
class GamesListNamespace(BaseNamespace, BroadcastMixin):
    def on_hello(self):
        logger.info(str(self.socket))
        logger.info('received hello on games list')
        self.emit('games_list', self.get_games_list())

    def get_games_list(self):
        games = Game.objects.filter(
            status__in=[Game.STATUS_PLAYING, Game.STATUS_WAITING]
        )
        return [game.to_dict() for game in games]

    def recv_disconnect(self):
        logger.info('received gameslist disconnect from ' + str(self.socket))

        self.disconnect(silent=True)

        return True
