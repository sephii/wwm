App.SocketIoView = Backbone.View.extend({
    initialize: function() {
        this.__initialize();
    },

    __initialize: function() {
        if (this.socket_events && _.size(this.socket_events) > 0) {
            this.delegateSocketEvents(this.socket_events);
        }
    },

    delegateSocketEvents: function(events) {
        for(var socketName in events) {
            var currentSocket = App.getSocket(socketName).socket;

            for (var key in events[socketName]) {
                var method = events[socketName][key];
                if (!_.isFunction(method)) {
                    method = this[method];
                }

                if (!method) {
                    throw new Error('Method "' + events[socketName][key] + '" does not exist');
                }

                method = _.bind(method, this);
                currentSocket.on(key, method);
            };
        }
    }
});
