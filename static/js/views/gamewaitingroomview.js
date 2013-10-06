/**
 * The game waiting room is where the user goes while waiting for players
 * to join his game.
 */
App.GameWaitingRoomView = App.SocketIoView.extend({
    events: {
        'click #start-game': 'start',
        'click #join-game': 'joinGameClick'
    },

    socket_events: {
        'game': {
            //'connect': 'joinGame',
            'players_list': 'updatePlayersList',
            'player_joined': 'playerJoined',
            'game_start': 'gameStarted'
        }
    },

    el: '#game-waitingroom',
    template: _.template($("#game-waitingroom-template").html()),

    initialize: function() {
        this.model = new App.Players();
        this.model.on('reset', this.render, this);

        this.__initialize();
    },

    render: function() {
        this.$el.html(this.template({
            'players': this.model.toJSON()
        }));

        console.log('render');
        return this;
    },

    joinGame: function(player, gameId, password) {
        if(_.isUndefined(password) || password === '') {
            password = null;
        }

        if(player.get('id')) {
            App.getSocket('game').joinGame(
                gameId,
                password
            );
        }
        else {
            console.log('Cannot join game, no player id');
        }
    },

    joinGameClick: function(e) {
        var that = this;
        var password = this.$el.find('input[name="password"]').val();

        e.preventDefault();

        App.player.set('name',
                       this.$el.find('input[name="nickname"]').val());
        App.getSocket('game').setNickname(
            App.player.get('name'),
            function(response, playerId) {
                console.log(playerId);
                console.log('gameid is ', that.options.gameId);
                App.player.set('id', playerId);
                that.joinGame(App.player, that.options.gameId, password);
                $('#nickname-dialog').foundation('reveal', 'close');
            }
        );
    },

    updatePlayersList: function(playersList) {
        console.log('got players list', playersList);
        this.model.reset(playersList);
    },

    playerJoined: function(playerName) {
        console.log(playerName + ' joined');
    },

    start: function(e) {
        e.preventDefault();
        App.getSocket('game').startGame();
    },

    gameStarted: function() {
        console.log('got game started !');
        App.gameWaitingRoomView.hide();
        App.gameView = new App.GameView();
        App.gameView.render();
    },

    hide: function() {
        this.$el.hide();
    }
});
