App.Game = Backbone.Model.extend({
    attributes: {
        'status': '',
        'creator': '',
        'money': 0,
        'categories': [],
        'nb_players': 0,
        'max_players': 0,
        'has_password': false
    }
});
