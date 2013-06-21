App.BaseSocket = {
    socket: null,
    queue: [],
    hasHelloAck: false,

    initialize: function() {
        console.log('Connecting on ' + this.endpoint);
        this.socket = io.connect(this.endpoint);
        this.delegateSocketEvents(this.socket_events);

        this.socket.on('reconnect', function () {
            console.log('System', 'Reconnected to the server');
        });

        this.socket.on('reconnecting', function () {
            console.log('System', 'Attempting to re-connect to the server');
        });

        this.socket.on('error', function (e) {
            console.log('System', e ? e : 'A unknown error occurred');
        });

        this.socket.on('disconnect', function() {
            console.log('DISCOOO');
            //this.socket.reconnect();
        });

        $(window).bind('beforeunload', function() {
            console.log('before unload');

            if(!_.isUndefined(this.socket)) {
                this.socket.disconnect();
            }
        });
    },

    isInitialized: function() {
        return this.socket !== null;
    },

    delegateSocketEvents: function(events) {
        for (var key in events) {
            var method = events[key];
            if (!_.isFunction(method)) {
                method = this[events[key]];
            }

            if (!method) {
                throw new Error('Method "' + events[key] + '" does not exist');
            }

            method = _.bind(method, this);
            this.socket.on(key, method);
        };
    },

    emit: function(fun, options) {
        if(_.isUndefined(options)) {
            options = {};
        }

        if(this.hasHelloAck) {
            fun(this.socket, options);
        }
        else {
            this.queue.push({'callback': fun, 'options': options});
        }
    },

    onHelloAck: function() {
        this.hasHelloAck = true;

        while(this.queue.length > 0) {
            var fun = this.queue.shift();
            fun.callback(this.socket, fun.options);
        }
    }
};

App.GameSocket = function() {};
_.extend(App.GameSocket.prototype, App.BaseSocket, {
    endpoint: '/game',
    socket_events: {
        'connect': 'onConnect'
    },

    createGame: function() {
        this.emit(this.doCreateGame);
    },

    doCreateGame: function(socket, options) {
        console.log('sending create game packet');
        socket.emit('create_game');
    },

    joinGame: function(gameId) {
        this.emit(this.doJoinGame, {'gameId': gameId});
    },

    setNickname: function(nickname, callback) {
        this.emit(this.doSetNickname, {'nickname': nickname, 'callback': callback});
    },

    doSetNickname: function(socket, options) {
        socket.emit('set_nickname', options.nickname, options.callback);
    },

    doJoinGame: function(socket, options) {
        console.log(options);
        console.log('sending join game packet');
        socket.emit('join_game', options.gameId);
    },

    onConnect: function() {
        console.log('game socket connected, sending hello');
        _.bindAll(this, 'onHelloAck');

        if(App.sessionId) {
            console.log('has a session id');
            this.socket.emit('hello', App.sessionId, this.onHelloAck);
        }
        else {
            console.log(App);
            console.log('no session id');
            this.socket.emit('hello', this.onHelloAck);
        }
    },

});

App.GamesListSocket = function() {};
_.extend(App.GamesListSocket.prototype, App.BaseSocket, {
    endpoint: '/games-list',
    socket_events: {
        'connect': 'onConnect'
    },

    onConnect: function() {
        this.socket.emit('hello');
    }
});
