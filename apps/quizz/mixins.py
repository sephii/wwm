class GameMixin(object):
    def __init__(self, *args, **kwargs):
        super(GameMixin, self).__init__(*args, **kwargs)
        if 'game' not in self.session:
            self.session['game'] = None

    def join(self, game):
        """Lets a user join a room on a specific Namespace."""
        self.session['game'] = game

    def leave(self, game):
        """Lets a user leave a room on a specific Namespace."""
        self.session['game'] = None

    def emit_to_players(self, event, *args):
        """This is sent to all in the room (in this particular Namespace)"""
        pkt = dict(type="event",
                   name=event,
                   args=args,
                   endpoint=self.ns_name)
        for sessid, socket in self.socket.server.sockets.iteritems():
            if 'game' not in socket.session:
                continue
            if socket.session['game'] == self.session['game']:
                socket.send_packet(pkt)
