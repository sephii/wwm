Chat = function() {
}();

Game = function() {
    var socket;

    function connect() {
        socket = io.connect('/quizz');

        $(window).bind("beforeunload", function() {
            socket.disconnect();
        });

        socket.emit('hello');
        bindSocketFunctions();

    }

    function setNickname(nickname) {
        socket.emit('login', nickname);
    }

    function bindSocketFunctions() {
        socket.on('connect', function (s) {
            console.log('connected');
        });

        socket.on('games_list', function (games) {
            console.log(games);
            $('#games-list tbody').empty();
            for (var i in games) {
              $('#games-list tbody').append($('<tr><td>' + games[i].categories.join(', ') + '</td><td>' + games[i].nb_players + ' / ' + games[i].max_players + '</td><td><a href="">Join</a></td>'));
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

        socket.on('players_list', function(list) {
            console.log('players list');
            console.log(list);
        });

        socket.on('question', function(player_id, question, answers) {
            console.log(player_id, question, answers);
        });
    }

    function createGame(nickname, categories, max_players, is_private) {
        socket.emit('login', nickname);
        socket.emit('create_game', categories, max_players, is_private);
    }

    function startGame() {
        socket.emit('start_game');
    }

    return {
        'connect': connect,
        'createGame': createGame,
        'startGame': startGame,
        'setNickname': setNickname
    }
}();

$(function() {
    Game.connect();

    $('#connect').submit(function() {
        Game.setNickname($('#nickname').val());

        return false;
    });

    /*
    $('#create-game').click(function() {
        Game.createGame();
    });
    */

    $('#start').click(function() {
        console.log('lets get ready to rumbleeee');
        Game.startGame();
    });

    $('#create-game').click(function() {
        $('#create-game-dialog').foundation('reveal', 'open', {
            closeOnBackgroundClick: true
        });
    });

    $('#create-game-dialog form').submit(function() {
        Game.createGame($('#nickname').val(), $('#game-categories').val(), $('#game-max-players').val(), $('#game-private').val());
        return false;
    });
});
