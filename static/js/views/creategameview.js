App.CreateGameView = App.SocketIoView.extend({
    events: {
        'click #create-game': 'createGame'
    },

    socket_events: {
    },

    el: '#create-game-container',

    initialize: function() {
        this.model = new App.Games();
        this.model.on('reset', this.render, this);

        this.__initialize();
    },

    createGame: function(e) {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: '/games/new/',
            data: $('#create-game-dialog form').serialize(),
            error: function(xhr, status, data) {
                $('#create-game-dialog div.form').html(xhr.responseJSON.form);
            },
            success: function(data) {
                App.sessionId = data.sessionId;
                App.getSocket('game').createGame();
                App.router.navigate('games/' + data.pk, {trigger: true});
            }
        });
    },

    render: function() {
        $('#create-game-dialog').foundation('reveal', 'open', {
            closeOnBackgroundClick: true
        });

        return this;
    },

    hide: function() {
        $('#create-game-dialog').foundation('reveal', 'close');
        this.$el.hide();
    }
});
