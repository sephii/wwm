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

        player.on('change:name', function() {
            App.getSocket('game').setNickname(
                player.getName(),
                function(response) {
                    this.joinGame(player);
                }
            );
        }, this);

        this.joinGame(player);

        this.__initialize();
    },

    render: function() {
        this.$el.html(this.template({
            'players': this.model.toJSON()
        }));

        console.log('render');
        return this;
    },

    joinGame: function(player) {
        var gameId = this.options.gameId;

        if(!_.isNull(player.get('name'))) {
            App.getSocket('game').joinGame(
                gameId,
                player.get('name')
            );
        }
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
