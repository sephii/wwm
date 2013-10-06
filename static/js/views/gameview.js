App.GameView = App.SocketIoView.extend({
    socket_events: {
    },

    el: '#game',
    template: _.template($("#game-template").html()),

    initialize: function() {
        this.model = new App.Game();
        this.model.on('change', this.render, this);

        this.__initialize();
    },

    render: function() {
        this.$el.html(this.template({
            'game': this.model.toJSON()
        }));
        return this;
    }
});
