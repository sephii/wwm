/**
 * The game waiting room is where the user goes while waiting for players
 * to join his game.
 */
App.GameWaitingRoomView = App.SocketIoView.extend({
    events: {
        'click #start-game': 'start'
    },

    socket_events: {
        'game': {
            'connect': 'joinGame',
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

        return this;
    },

    joinGame: function() {
        console.log('join game');
        App.getSocket('game').joinGame(this.options.gameId);
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
