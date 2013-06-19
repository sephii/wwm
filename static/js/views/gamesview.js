App.GamesView = App.SocketIoView.extend({
    socket_events: {
        'gamesList': {
            'games_list': 'showGamesList'
        }
    },

    el: '#games-list',
    template: _.template($("#games-list-template").html()),

    initialize: function() {
        this.model = new App.Games();
        this.model.on('reset', this.render, this);

        this.__initialize();
    },

    render: function() {
        this.$el.html(this.template({
            'games': this.model.toJSON()
        }));
        return this;
    },

    showGamesList: function(games) {
        this.model.reset(games);
    },

    hide: function() {
        this.$el.hide();
    }
});
