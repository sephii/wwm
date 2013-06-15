Chat = function() {
}();

Game = function() {
    var socket;

    function connect() {
        socket = io.connect('/quizz');

        $(window).bind("beforeunload", function() {
            socket.disconnect();
        });

        if(window.session !== undefined) {
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

        socket.on('games_list', function (games) {
            $('#games-list tbody').empty();
            for (var i in games) {
              $('#games-list tbody').append($('<tr><td>' + games[i].categories.join(', ') + '</td><td>' + games[i].nb_players + ' / ' + games[i].max_players + '</td><td><a href="games/' + games[i].id + '/">Join</a></td>'));
            }

            $('#games-list tbody a').click(function() {
                socket.emit('join', $(this).text());
            });
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

        socket.on('players_list', function(players) {
            $('#players-list').empty();
            for (var i in players) {
              $('#players-list').append($('<li>').text(players[i]));
            }
        });

        socket.on('question', function(player_id, question, answers, value) {
            $('#question').text(question);

            $('#answers').empty();
            for(var i in answers) {
                var answer = $('<li>');
                answer.append($('<a class="button">').html(String.fromCharCode(65 + parseInt(i)) + ': <span class="answer">' + answers[i] + '</span>'));
                $('#answers').append(answer);
            }

            $('#answers li a').click(function() {
                console.log('answering ' + $(this).find('.answer').text());
                socket.emit('answer', $(this).find('.answer').text());
            });
        });

        socket.on('game_start', function() {
            console.log('game started');
        });

        socket.on('correct_answer', function() {
            console.log('YES');
        });

        socket.on('wrong_answer', function() {
            console.log('NOES');
        });
    }

    function startGame() {
        socket.emit('start_game');
    }

    function joinGame() {
        socket.emit('join_game');
    }

    return {
        'connect': connect,
        'startGame': startGame,
        'joinGame': joinGame
    }
}();

$(function() {
    Game.connect();

    $('#start-game').click(function() {
        console.log('lets get ready to rumbleeee');
        Game.startGame();

        return false;
    });

    $('#create-game').click(function() {
        $('#create-game-dialog').foundation('reveal', 'open', {
            closeOnBackgroundClick: true
        });
    });

    if($('#create-game-dialog form').hasClass('errors')) {
        $('#create-game-dialog').foundation('reveal', 'open', {
            animation: ''
        });
    }

    if($('#nickname-dialog form').hasClass('errors')) {
        $('#nickname-dialog').foundation('reveal', 'open', {
            animation: ''
        });
    }

    if(window.session !== undefined && window.session) {
        Game.joinGame();
    }
    else if(window.session == '') {
        console.log('no session');
        $('#nickname-dialog').foundation('reveal', 'open', {
            animation: ''
        });
    }
});
