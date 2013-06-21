/**
 * The game waiting room is where the user goes while waiting for players
 * to join his game.
 */
App.GameWaitingRoomView = App.SocketIoView.extend({
    events: {
        'click #start-game': 'start',
        'click #join-game': 'joinGame'
    },

    socket_events: {
        'game': {
            //'connect': 'joinGame',
            'players_list': 'updatePlayersList',
            'player_joined': 'playerJoined'
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
        if(App.playerId == null) {
            $('#nickname-dialog').foundation('reveal', 'open', {
                closeOnBackgroundClick: true
            });
        }
        else {
            App.getSocket('game').joinGame(this.options.gameId);
        }

        return this;
    },

    joinGame: function(e) {
        var gameId = this.options.gameId;
        e.preventDefault();
        console.log('join game');
        console.log($('#nickname-dialog input[name="nickname"]').val());

        App.getSocket('game').setNickname(
            $('#nickname-dialog input[name="nickname"]').val(),
            function(response) {
                App.getSocket('game').joinGame(
                    gameId,
                    $('#nickname-dialog input[name="password"]').val()
                );
            }
        );
    },

    updatePlayersList: function(playersList) {
        console.log('got players list', playersList);
        this.model.reset(playersList)
    },

    playerJoined: function(playerName) {
        console.log(playerName + ' joined');
    },

    start: function() {
        Game.startGame();
    }
});
