App.Game = Backbone.Model.extend({
    attributes: {
        'status': '',
        'creator': '',
        'current_money': 0,
        'categories': [],
        'nb_players': 0,
        'max_players': 0,
        'has_password': false,
        'current_player': null,
        'current_question': null,
        'answers': []
    }
});
