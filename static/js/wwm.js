Chat = function() {
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
            socket.emit('hello', window.session, function() {
                joinGame();
            });
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
        $('#current-player-container').text(player.name);

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

    else if(window.session == '') {
        console.log('no session');
        $('#nickname-dialog').foundation('reveal', 'open', {
            animation: ''
        });
    }
});
