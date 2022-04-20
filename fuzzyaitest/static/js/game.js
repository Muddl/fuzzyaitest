import { removeHighlightedSquares, greySquare, redSquare, greenSquare, sortAlphabet } from './helpers.js';

// Global Variables
var game_id = window.location.pathname.substring(6,window.location.pathname.length); // Check the subtring params here
var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var ws_path = ws_scheme + '://' + window.location.host + "/game/" + game_id;
console.log("Attempting connection on " + ws_path);
var socket = new ReconnectingWebSocket(ws_path);
console.log("Connected on " + ws_path);

// JQuery Element References
var $whiteCapturedCon = $('#white-captured-con');
var $blackCapturedCon = $('#black-captured-con');
var $move_log = $("#move_log");
var $die = $("#die");
var $attacking_piece = $("#attacking-piece");
var $defending_piece = $("#defending-piece");
var $opp_pieces = $("#white-captured-con");
var $own_pieces = $("#black-captured-con");
var $attack_result = $("#attack-result");
var $modalTitle = $('#modal-title');
var $modalBody = $('#modal-body');

// Local Gamestate Var Holders
var local_boardstate = null;
var local_isAIGame = null;
var local_level = null;
var local_whiteMove = null;
var local_corplist = null;
var local_white_captured = null;
var local_black_captured = null;
var local_ai_action_list = null;
var local_ai_move_list = null;

const findCorpOfPiece = (source, piece) => {
    const Apos = source;
    const Acolor = piece.substring(0,1);
    const Arank = piece.substring(1,2);
    let Acorp = "";

    if (Acolor == "w") {
        switch (Arank) {
            case "P":
                Object.entries(local_corplist.w).forEach((corpKey) => {
                    corpKey[1].under_command.forEach((piece) => {
                        if (piece.pos == Apos && piece.color == Acolor && piece.rank == Arank) {
                            Acorp = piece.corp;
                        };
                    });
                });
                console.log(Acorp);
                break;
            case "B":
                Object.entries(local_corplist.w).forEach((corpKey) => {
                    if (corpKey[1].leader.pos == Apos && corpKey[1].leader.color == Acolor && corpKey[1].leader.rank == Arank) {
                        Acorp = corpKey[1].leader.corp;
                    };
                });
                console.log(Acorp);
                break;
            case "N":
                Object.entries(local_corplist.w).forEach((corpKey) => {
                    corpKey[1].under_command.forEach((piece) => {
                        if (piece.pos == Apos && piece.color == Acolor && piece.rank == Arank) {
                            Acorp = piece.corp;
                        };
                    });
                });
                console.log(Acorp);
                break;
            case "R":
                Object.entries(local_corplist.w).forEach((corpKey) => {
                    corpKey[1].under_command.forEach((piece) => {
                        if (piece.pos == Apos && piece.color == Acolor && piece.rank == Arank) {
                            Acorp = piece.corp;
                        };
                    });
                });
                console.log(Acorp);
                break;
            case "Q":
                Object.entries(local_corplist.w).forEach((corpKey) => {
                    corpKey[1].under_command.forEach((piece) => {
                        if (piece.pos == Apos && piece.color == Acolor && piece.rank == Arank) {
                            Acorp = piece.corp;
                        };
                    });
                });
                console.log(Acorp);
                break;
            case "K":
                Object.entries(local_corplist.w).forEach((corpKey) => {
                    if (corpKey[1].leader.pos == Apos && corpKey[1].leader.color == Acolor && corpKey[1].leader.rank == Arank) {
                        Acorp = corpKey[1].leader.corp;
                    };
                });
                console.log(Acorp);
                break;
        };
    } else {
        switch (Arank) {
            case "P":
                Object.entries(local_corplist.b).forEach((corpKey) => {
                    corpKey[1].under_command.forEach((piece) => {
                        if (piece.pos == Apos && piece.color == Acolor && piece.rank == Arank) {
                            Acorp = piece.corp;
                        };
                    });
                });
                console.log(Acorp);
                break;
            case "B":
                Object.entries(local_corplist.b).forEach((corpKey) => {
                    if (corpKey[1].leader.pos == Apos && corpKey[1].leader.color == Acolor && corpKey[1].leader.rank == Arank) {
                        Acorp = corpKey[1].leader.corp;
                    };
                });
                console.log(Acorp);
                break;
            case "N":
                Object.entries(local_corplist.b).forEach((corpKey) => {
                    corpKey[1].under_command.forEach((piece) => {
                        if (piece.pos == Apos && piece.color == Acolor && piece.rank == Arank) {
                            Acorp = piece.corp;
                        };
                    });
                });
                console.log(Acorp);
                break;
            case "R":
                Object.entries(local_corplist.b).forEach((corpKey) => {
                    corpKey[1].under_command.forEach((piece) => {
                        if (piece.pos == Apos && piece.color == Acolor && piece.rank == Arank) {
                            Acorp = piece.corp;
                        };
                    });
                });
                console.log(Acorp);
                break;
            case "Q":
                Object.entries(local_corplist.b).forEach((corpKey) => {
                    corpKey[1].under_command.forEach((piece) => {
                        if (piece.pos == Apos && piece.color == Acolor && piece.rank == Arank) {
                            Acorp = piece.corp;
                        };
                    });
                });
                console.log(Acorp);
                break;
            case "K":
                Object.entries(local_corplist.b).forEach((corpKey) => {
                    if (corpKey[1].leader.pos == Apos && corpKey[1].leader.color == Acolor && corpKey[1].leader.rank == Arank) {
                        Acorp = corpKey[1].leader.corp;
                    };
                });
                console.log(Acorp);
                break;
        };
    };

    return Acorp;
};

const attackOrMove = (oldPos, newPos) => {
    // The following code block diffs the boards locally so that a move/attack can be detected
    // Odd approach and fairly insecure, so we gotta figure out a beter solution in the future

    let previousFen = oldPos;
    let currentFen = newPos;

    //removes numbers and / from current fen
    let noNumbersCurrent = Chessboard.objToFen(currentFen).toString().replace(/[0-9]/g, '');
    noNumbersCurrent = noNumbersCurrent.replace(/\//g, '');
    noNumbersCurrent = sortAlphabet(noNumbersCurrent);

    //removes numbers and / from previous fen
    let noNumbersPrevious = Chessboard.objToFen(previousFen).toString().replace(/[0-9]/g, '');
    noNumbersPrevious = noNumbersPrevious.replace(/\//g, '');
    noNumbersPrevious = sortAlphabet(noNumbersPrevious);

    //checks to see if piece is missing from previous fen
    let defendingPiece = "";

    for (let i = 0, j = 0; i <= noNumbersPrevious.length; i++, j++) {
        if (noNumbersPrevious[i] !== noNumbersCurrent[j]) { 
            defendingPiece += noNumbersPrevious[i];
            i++;
        };
    };

    if (defendingPiece.length != 0){
        return true;
    } else {
        return false;
    }
};

// This triggers on a piece pickup & sends a highlight request to the backend
const onDragStart = (source, piece) => {
    const Apos = source;
    const Acolor = piece.substring(0,1);
    const Arank = piece.substring(1,2);
    const Acorp = findCorpOfPiece(source, piece);

    const highlightJson = JSON.stringify({
        'actionType': 'HIGHLIGHT',
        'isAIGame': local_isAIGame,
        'activePiece': {
            'pos': Apos,
            'color': Acolor,
            'rank': Arank,
            'corp': Acorp
        }
    });
    
    socket.send(highlightJson);
};

const onDrop = (source, target, piece, newPos, oldPos) => {
    removeHighlightedSquares();

    // if ATTACK_ATTEMPT
    if (attackOrMove(oldPos, newPos)) {
        //activePiece
        var Apos = source;
        var Acolor = String(piece).substring(0,1);
        var Arank = String(piece).substring(1,2);
        var Acorp = findCorpOfPiece(source, piece);
        //targetPiece
        var Tpos = target;
        var Tcolor = board.position()[Tpos].substring(0,1);
        var Trank = board.position();
        Trank = Trank[String(Tpos)].substring(1,2);
        var Tcorp = findCorpOfPiece(target, String(Tcolor + Trank));

        const attackAttemptJson = JSON.stringify({
            'actionType': 'ATTACK_ATTEMPT',
            'isAIGame': local_isAIGame,
            'activePiece': {
                'pos': Apos,
                'color': Acolor,
                'rank': Arank,
                'corp': Acorp
            },
            'targetPiece': {
                'pos': Tpos,
                'color': Tcolor,
                'rank': Trank,
                'corp': Tcorp
            },
            'corpList': local_corplist,
            'whiteMove': local_whiteMove
        });

        socket.send(attackAttemptJson);
    }
    // if MOVEMENT
    else {
        var pos = source;
        var color = String(piece).substring(0,1);
        var rank = String(piece).substring(1,2);
        var corp = findCorpOfPiece(source, piece);

        if (pos != target) {
            const movementJson = JSON.stringify({
                'actionType': 'MOVEMENT',
                'isAIGame': local_isAIGame,
                'activePiece': {
                    'pos': source,
                    'color': color,
                    'rank': rank,
                    'corp': corp
                },
                'targetPiece': {
                    'pos': target,
                    'color': color,
                    'rank': rank,
                    'corp': corp
                },
                'corpList': local_corplist,
                'whiteMove': local_whiteMove
            });

            socket.send(movementJson);

            // Append a new entry to the movelog
            var textElement = document.createElement('p');
            textElement.textContent = color + rank + ' ' + source + ' -> ' + target;
            $move_log.append(textElement);
            $move_log.css("display",'inline');
        };
    };
}

// const onSnapEnd = () => {
//     setTimeout(() => {
//         board.position(local_boardstate, false);
//     }, 500);
// };

// Configure for AI Game funcs
var config = {
    draggable: true,
    dropOffBoard: 'snapback',
    position: 'start',
    onDrop: onDrop,
    onDragStart: onDragStart,
    // onSnapEnd: onSnapEnd,
    pieceTheme: '/static/chessboard/{piece}.png',
};

// Render chessboard with config
var board = Chessboard('my_board', config);

const renderPieceListAnim = (white_captured, black_captured) => {
    let eliminatedPiece = $defending_piece.attr("src");
    let colorOfPiece = eliminatedPiece.charAt(eliminatedPiece.length - 6);
    let PlayerCapturedPieces = black_captured;
    let OppCapturedPieces = white_captured;

    if (colorOfPiece == 'b') {
        PlayerCapturedPieces.push(eliminatedPiece);
        for (let count = PlayerCapturedPieces.length; count < PlayerCapturedPieces.length + 1; count++) {
            var imageElement = document.createElement('img');
            imageElement.setAttribute('src', PlayerCapturedPieces[count-1]);
            $own_pieces.append(imageElement).css("width",'25px');
        };
    } else {
        OppCapturedPieces.push(eliminatedPiece)
        for (let count = OppCapturedPieces.length; count < OppCapturedPieces.length + 1; count++) {
            var imageElement = document.createElement('img');
            imageElement.setAttribute('src', OppCapturedPieces[count-1]);
            $opp_pieces.append(imageElement).css("width",'25px');
        };
    };
};

const setCombatPieces = (attackingPiece, defendingPiece) => {
    $attacking_piece.attr("src", "/static/chessboard/" + attackingPiece + ".png");
    $defending_piece.attr("src", "/static/chessboard/" + defendingPiece + ".png");
    $attacking_piece.css("visibility","visible");
    $defending_piece.css("visibility","visible");
};

const removeCombatPieces = () => {
    setTimeout(() => {
        $attacking_piece.css("visibility","hidden");
        $defending_piece.css("visibility","hidden");
        $die.css("visibility","hidden");
    }, 3000);
};

const rollAnimStart = (data) => {
    let dice = document.querySelectorAll("img.dice");

    setCombatPieces(data.activePiece, data.targetPiece);
    $attack_result.text("Rolling for Attack!").css("color", "grey");

    dice.forEach((die) => {
        die.classList.add("shake");
    });
};

const successfullAttack = (rollVal, blitz, white_captured, black_captured, new_boardstate) => {
    let dice = document.querySelectorAll("img.dice");
    var moveToBeLogged = document.createElement('p');

    dice.forEach((die) => {
        die.classList.remove("shake");
    });

    const dieValue = rollVal;
    if (dieValue == 1) {
        $die.attr("src", "../static/dice/dice_1.png");
    } else if (dieValue == 2) {
        $die.attr("src", "../static/dice/dice_2.png");
    } else if (dieValue == 3) {
        $die.attr("src", "../static/dice/dice_3.png")
    } else if (dieValue == 4) {
        $die.attr("src", "../static/dice/dice_4.png");
    } else if (dieValue == 5) {
        $die.attr("src", "../static/dice/dice_5.png");
    } else if (dieValue == 6) {
        $die.attr("src", "../static/dice/dice_6.png");
    }

    if (blitz) {
        $attack_result.text("Successful Attack + Blitz!").css("color", "green").css("visibility","visible");
        moveToBeLogged.textContent = `Attack succeeded with blitz and a roll of ${dieValue}`;
        renderPieceListAnim(white_captured, black_captured);
    } else {
        $attack_result.text("Successful Attack!").css("color", "green").css("visibility","visible");
        moveToBeLogged.textContent = `Attack succeeded with a roll of ${dieValue}`;
        renderPieceListAnim(white_captured, black_captured);
    };

    board.position(new_boardstate);

    $move_log.append(moveToBeLogged);
    removeCombatPieces();
};

const failedAttack = (rollVal, blitz, new_boardstate) => {
    let dice = document.querySelectorAll("img.dice");
    var moveToBeLogged = document.createElement('p');

    dice.forEach((die) => {
        die.classList.remove("shake");
    });

    const dieValue = rollVal;
    if (dieValue == 1) {
        $die.attr("src", "../static/dice/dice_1.png");
    } else if (dieValue == 2) {
        $die.attr("src", "../static/dice/dice_2.png");
    } else if (dieValue == 3) {
        $die.attr("src", "../static/dice/dice_3.png")
    } else if (dieValue == 4) {
        $die.attr("src", "../static/dice/dice_4.png");
    } else if (dieValue == 5) {
        $die.attr("src", "../static/dice/dice_5.png");
    } else if (dieValue == 6) {
        $die.attr("src", "../static/dice/dice_6.png");
    }

    if (blitz) {
        $attack_result.text("Failed Attack + Blitz!").css("color", "red").css("visibility","visible");
        moveToBeLogged.textContent = `Attack failed with blitz and a roll of ${dieValue}`;
    } else {
        $attack_result.text("Failed Attack!").css("color", "red").css("visibility","visible");
        moveToBeLogged.textContent = `Attack failed with a roll of ${dieValue}`;
    };

    board.position(new_boardstate);

    $move_log.append(moveToBeLogged);
    removeCombatPieces();
};

const resolveAttack = (data) => {
    rollAnimStart(data);

    if (typeof data.white_captured == 'undefined') {
        local_white_captured = [];
    } else {
        local_white_captured = data.white_captured;
    }
    
    if (typeof data.black_captured == 'undefined') {
        local_black_captured = [];
    } else {
        local_black_captured = data.black_captured;
    }

    if (data.isSuccessfulAttack) {
        setTimeout(successfullAttack(data.roll_val, data.blitz, local_white_captured, local_black_captured, data.new_boardstate), 3000);
    }
    else {
        setTimeout(failedAttack(data.roll_val, data.blitz, data.new_boardstate), 3000);
    };
};

const startAITurn = () => {
    const requestAIJSON = JSON.stringify({
        'actionType': 'AI_TURN_REQ',
        'isAIGame': local_isAIGame,
        'corpList': local_corplist,
        'whiteMove': local_whiteMove
    });

    socket.send(requestAIJSON);
};

// Fires whenever socket connection opens (On page open)
socket.onopen = () => {
    $('#gameModal').modal('hide');
    $('#gameModal').data('bs.modal',null);
};

// Fires whenever socket connection is dropped unexpectedly
socket.onclose = () => {
    $modalTitle.html("Connection closed");
    $modalBody.html("Connection closed unexpectedly please wait while we try to reconnect...");
    $('#gameModal').modal({
      keyboard: false,
      backdrop: 'static'
    });
};

// The meat of the JS function here, message processing from WS channel
socket.onmessage = (message) => {
    console.log("Got websocket message " + message.data);
    var data = JSON.parse(message.data);

    // On JOIN actionType
    if (data.actionType=="JOIN") {
        // Handle AI Game version
        if (data.isAIGame) {
            // Set local var values
            local_boardstate = data.boardstate;
            local_isAIGame = data.isAIGame;
            local_level = data.level;
            local_whiteMove = data.whiteMove;
            local_corplist = data.corplist;
            local_white_captured = data.white_captured;
            local_black_captured = data.black_captured;

            board.position(local_boardstate);

            // Set up the captured pieces visualization
            if (local_black_captured != null) {
                local_black_captured.forEach((piece) => {
                    $blackCapturedCon.append($('<img>', {src: `..\chessboard\\b${piece}.png`}))
                });
            }
            if (local_white_captured != null) {
                local_white_captured.forEach((piece) => {
                    $whiteCapturedCon.append($('<img>', {src: `..\chessboard\w${piece}.png`}))
                });
            }

            if (!local_whiteMove) {
                startAITurn();
            }
        }
    }
    // On MOVEMENT actionType
    else if(data.actionType=="MOVEMENT") {
        local_corplist = data.corpList;
        local_boardstate = data.new_boardstate;
        local_whiteMove = data.whiteMove;
        
        board.position(data.new_boardstate);

        if (!local_whiteMove) {
            startAITurn();
        }
    }
    // On ATTACK_ATTEMPT actionType
    else if(data.actionType=="ATTACK_ATTEMPT") {
        local_corplist = data.corpList;
        local_boardstate = data.new_boardstate;
        local_whiteMove = data.whiteMove;
        
        resolveAttack(data);

        if (!local_whiteMove) {
            startAITurn();
        }
    }
    // On HIGHLIGHT actionType
    else if(data.actionType=="HIGHLIGHT") {
        data.in_range.forEach(pos => redSquare(pos));
        data.setup.forEach(pos => greenSquare(pos));
        data.movement.forEach(pos => greySquare(pos));
    }
    // On AI_ACTION_REQ actionType
    else if(data.actionType=="AI_TURN_RES") {
        local_ai_action_list = data.black_actions;
        local_ai_move_list = data.black_moves;

        console.log(local_ai_action_list[0].activePiece.rank);
        console.log(local_ai_move_list);

        for (let i = 0; i < 3; i++) {
            if (local_ai_move_list[i] != null && local_ai_action_list[i].activePiece.rank != 'R') {
                board.move(local_ai_move_list[i]);
            }
        }
    }
};

// Initial resign button click
$(document).on('click','#resign', () => {
    $('#resignModal').modal({
        keyboard: false,
        backdrop: 'static'
    });
});

// Choose not to resign
$(document).on('click','#noRes', () => {
    $('#resignModal').modal('hide');
    $('#resignModal').data('bs.modal',null);
});

// Double down on resigning
$(document).on('click','#yesRes', () => {
    socket.send(JSON.stringify({"actionType": "RESIGN","result": "Black wins"}));
    $('#resignModal').modal('hide');
    $('#resignModal').data('bs.modal',null);
    $modalTitle.html("Game over");
    $modalBody.html("You have resigned from the game. You lose!");
    $('#gameModal').modal({
        keyboard: false,
        backdrop: 'static'
    });
});