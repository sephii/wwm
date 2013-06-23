var csrftoken = $.cookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/*
Chat = function() {
}();

GamesList = function() {
    var socket;

    function connect() {
        socket = io.connect('/games-list');

        $(window).bind("beforeunload", function() {
            socket.disconnect();
        });

        bindSocketFunctions();
        socket.emit('hello');
    }

    function bindSocketFunctions() {
        socket.on('connect', function (s) {
            console.log('connected to games list');
        });

        socket.on('games_list', function (games) {
            $('#games-list tbody').empty();
            for (var i in games) {
                // TODO XSS
                $('#games-list tbody').append($(
                    '<tr><td>' + games[i].creator + '</td><td>' + games[i].money +
                    '</td><td>' + games[i].categories.join(', ') + '</td><td>' +
                    games[i].nb_players + ' / ' + games[i].max_players +
                    '</td><td ' + (games[i].has_password ? 'class="locked"' : '') + '>' +
                    (games[i].status == 1 ? ('<a href="games/' + games[i].id + '/">Join</a>') : '') + '</td>'));
            }

            $('#games-list tbody a').click(function() {
                socket.emit('join', $(this).text());
            });
        });
    }

    return {
        'connect': connect
    }
}();

Game = function() {
    var socket;

    function connect() {
        socket = io.connect('/quizz');

        $(window).bind("beforeunload", function() {
            socket.disconnect();
        });

        console.log('hello');
        if(window.session !== undefined && window.session) {
            socket.emit('hello', window.session);
        }
        else {
            socket.emit('hello');
        }

        bindSocketFunctions();
    }

    function bindSocketFunctions() {
        socket.on('connect', function (s) {
            console.log('connected');
        });

        socket.on('reconnect', function () {
            console.log('System', 'Reconnected to the server');
        });

        socket.on('reconnecting', function () {
            console.log('System', 'Attempting to re-connect to the server');
        });

        socket.on('error', function (e) {
            console.log('System', e ? e : 'A unknown error occurred');
        });

        socket.on('player_joined', function(nickname) {
            console.log('player ' + nickname + ' joined');
        });

        socket.on('player_left', function(nickname) {
            console.log('player ' + nickname + ' left');
        });

        socket.on('games_list', function (games) {
            console.log('errrrrr');
        });

        socket.on('players_list', function(players) {
            $('#players-list').empty();
            for (var i in players) {
              $('#players-list').append($('<li>').text(players[i]));
            }
        });

        socket.on('question', function(player, question) {
            console.log('received question ' + question.question);
            $('#waiting-screen').hide();
            $('#game-board').show();
            showQuestion(player, question);
        });

        socket.on('answered', function(answer) {
            console.log('the other player answered ' + answer);
            $('#answers li a').each(function() {
                if($(this).find('.answer').text() == answer) {
                    $(this).addClass('answer');
                    return true;
                }
            });
        });

        socket.on('game_start', function() {
            console.log('game started');
        });

        socket.on('correct_answer', function() {
            console.log('correct!');
            console.log('adding success class');
            $('#answers li a.answer').removeClass('answer').addClass('success');
        });

        socket.on('wrong_answer', function(correct_answer) {
        console.log('wrong answer, correct is ' + correct_answer);
            console.log('adding alert class');
            $('#answers li a.answer').removeClass('answer').addClass('alert');

            setTimeout(function() {
                $('#answers li a').each(function() {
                    if($(this).find('.answer').text() == correct_answer) {
                        $(this).addClass('success');
                        return true;
                    }
                });
            }, 2000);
        });
    }

    function showQuestion(player, question) {
        $('#current-money').text(question.value);
        $('#question').text(question.question);

        if(player.id == window.player_id) {
            $('#current-player').text('you').addClass('you');
        }
        else {
            $('#current-player').text(player.name).removeClass('you');
        }

        $('#answers').empty();
        for(var i in question.answers) {
            var answer = $('<li>');
            answer.append($('<a class="button disabled">').html(String.fromCharCode(65 + parseInt(i)) + ': <span class="answer">' + question.answers[i] + '</span>'));
            $('#answers').append(answer);
        }

        console.log('question is for ' + player.id + ', current is ' + window.player_id);
        if(player.id == window.player_id) {
            $('#answers li a').each(function() {
                $(this).removeClass('disabled');
            });

            $('#answers li a').click(function() {
                var answer = $(this).find('.answer').text();
                $(this).addClass('answer');

                $('#answers li a').each(function() {
                    $(this).addClass('disabled');
                });

                console.log('answering ' + answer);
                socket.emit('answer', answer);
            });
        }
    }

    function startGame() {
        console.log('start game');
        socket.emit('start_game');

        $('#start-game').prop('disabled', true);
    }

    function joinGame() {
        console.log('join game');
        socket.emit('join_game');
    }

    function announceGame() {
        console.log('announce game');
        socket.emit('create_game');
    }

    return {
        'connect': connect,
        'startGame': startGame,
        'joinGame': joinGame,
        'announceGame': announceGame
    }
}();
*/

window.App = {
    gamesView: null,
    createGameView: null,
    player: null,
    sessionId: _.isUndefined(window.sessionId) ? null : window.sessionId,
    sockets: {},
    getSocket: function(socket) {
        if(!this.sockets[socket].isInitialized()) {
            this.sockets[socket].initialize();
        }

        return this.sockets[socket];
    },
    initialize: function() {
        this.player = new App.Player({
            id: _.isUndefined(window.playerId) ? null : window.playerId
        });
    }
}

App.Router = Backbone.Router.extend({
    routes: {
        '': 'home',
        'games/new': 'newGame',
        'games/:id': 'joinGame'
    },

    home: function() {
        App.gamesView = new App.GamesView();
        App.gamesView.render();
    },

    newGame: function() {
        if(App.gamesView == null) {
            App.gamesView = new App.GamesView();
            App.gamesView.render();
        }

        App.createGameView = new App.CreateGameView();
        App.createGameView.render();
    },

    joinGame: function(id) {
        var needsPassword = false;

        if(App.createGameView != null) {
            App.createGameView.hide();
        }

        if(App.gamesView != null) {
            App.gamesView.hide();
        }

        App.gameWaitingRoomView = new App.GameWaitingRoomView({
            'gameId': id
        });

        $.get('/games/' + id + '/info/', function(data) {
            needsPassword = data.needs_password;

            if(data.needs_password) {
                App.gameWaitingRoomView.$el.find('input[name="password"]').parents('div.row').show();
            }
            else {
                App.gameWaitingRoomView.$el.find('input[name="password"]').parents('div.row').hide();
            }
        });

        App.gameWaitingRoomView.render();

        if(App.player.get('id') == null || needsPassword) {
            $('#nickname-dialog').foundation('reveal', 'open', {
                closeOnBackgroundClick: true
            });
        }
        else {
            App.gameWaitingRoomView.joinGame(App.player, id);
        }
    }
});

$(function() {
    App.router = new App.Router();
    App.sockets = {
        gamesList: new App.GamesListSocket(),
        game: new App.GameSocket()
    };
    App.initialize();

    Backbone.history.start();
});
