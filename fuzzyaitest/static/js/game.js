import { removeHighlightedSquares, greySquare, redSquare, greenSquare, sortAlphabet } from './helpers.js';

// Global Variables
var game_id = JSON.parse(document.getElementById('json-lobbyid').textContent);
var userName = JSON.parse(document.getElementById('json-username').textContent);
var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var ws_path = ws_scheme + '://' + window.location.host + "/game/" + game_id;
console.log("Attempting connection on " + ws_path);
var socket = new ReconnectingWebSocket(ws_path);
console.log("Connected on " + ws_path);

// JQuery Element References
// Orientation Dependant
var $playerCapturedCon = $('#player-captured-con');
var $playerLBAuth = $('#playerLBAuth');
var $playerKAuth = $('#playerKAuth');
var $playerRBAuth = $('#playerRBAuth');
var $oppCapturedCon = $('#opp-captured-con');
var $oppLBAuth = $('#oppLBAuth');
var $oppKAuth = $('#oppKAuth');
var $oppRBAuth = $('#oppRBAuth');
// Non-Orientation Dependant
var $move_log = $("#move_log");
var $die = $("#die");
var $attacking_piece = $("#attacking-piece");
var $defending_piece = $("#defending-piece");
var $attack_result = $("#attack-result");
var $gameModalTitle = $('#game-modal-title');
var $gameModalBody = $('#game-modal-body');
var $resModalTitle = $('#res-modal-title');
var $resModalBody = $('#res-modal-body');
var $kingDelegateMenuContents = $("#kingDelegateMenuContents");
var $targetCorpMenuContents = $("#targetCorpMenuContents");
var $chatMessages = $("#chat-messages");
var $chatInput = $("#chat-input");
var $chatSubmit = $("#chat-submit");

// Local Gamestate Var Holders
var local_orientation = null;
var local_opp_online = null;
var local_boardstate = null;
var local_isAIGame = null;
var local_level = null;
var local_whiteMove = null;
var local_corplist = null;
var local_white_captured = null;
var local_black_captured = null;
var local_ai_action_list = null;
var local_ai_move_list = null;
var local_readyToBlitz = null;
var local_delegation_ready = null;
var board = Chessboard('my_board');

var midAnimation = false;

const renderActionHistory = (action_history) => {
    $move_log.empty()
    action_history.forEach((action, index) => {
        $move_log.append(`<b>Action #${index+1}</b>: ${action}<br>`);
    });
};

const updateAuthRemaining = () => {
    // First iterate through local_corplist and create a sublist of remaining command authorities
    const sublist_of_auth_remain = [[], []];
    Object.entries(local_corplist.w).forEach((corpKey) => {
        sublist_of_auth_remain[0].push([corpKey[0], corpKey[1].command_authority_remaining]);
    });
    Object.entries(local_corplist.b).forEach((corpKey) => {
        sublist_of_auth_remain[1].push([corpKey[0], corpKey[1].command_authority_remaining]);
    });

    // Then for each corp p tag, replace any integers or # with the relevant value in local_corplist
    const detected_w_corps = [];
    const detected_b_corps = [];

    sublist_of_auth_remain[0].forEach((auth_remain_array) => {
        switch (auth_remain_array[0]) {
            case "kingCorp":
                detected_w_corps.push("kingCorp");
                if (auth_remain_array[1] == -999) {
                    $playerKAuth.text((`King: 0`));
                } else {
                    $playerKAuth.text((`King: ${auth_remain_array[1]}`));
                }
                break;
            case "leftBishopCorp":
                detected_w_corps.push("leftBishopCorp");
                if (auth_remain_array[1] == -999) {
                    $playerLBAuth.text((`Left Bishop: 0`));
                } else {
                    $playerLBAuth.text((`Left Bishop: ${auth_remain_array[1]}`));
                }
                break;
            case "rightBishopCorp":
                detected_w_corps.push("rightBishopCorp");
                if (auth_remain_array[1] == -999) {
                    $playerRBAuth.text((`Right Bishop: 0`));
                } else {
                    $playerRBAuth.text((`Right Bishop: ${auth_remain_array[1]}`));
                }
                break;
        };
    });
    if (!detected_w_corps.includes('kingCorp')) {
        $playerKAuth.text((`King: Captured`));
    }
    if (!detected_w_corps.includes('leftBishopCorp')) {
        $playerLBAuth.text((`Left Bishop: Captured`));
    }
    if (!detected_w_corps.includes('rightBishopCorp')) {
        $playerRBAuth.text((`Right Bishop: Captured`));
    };

    sublist_of_auth_remain[1].forEach((auth_remain_array) => {
        switch (auth_remain_array[0]) {
            case "kingCorp":
                detected_b_corps.push("kingCorp");
                if (auth_remain_array[1] == -999) {
                    $oppKAuth.text((`King: 0`));
                } else {
                    $oppKAuth.text((`King: ${auth_remain_array[1]}`));
                }
                break;
            case "leftBishopCorp":
                detected_b_corps.push("leftBishopCorp");
                if (auth_remain_array[1] == -999) {
                    $oppLBAuth.text((`Left Bishop: 0`));
                } else {
                    $oppLBAuth.text((`Left Bishop: ${auth_remain_array[1]}`));
                }
                break;
            case "rightBishopCorp":
                detected_b_corps.push("rightBishopCorp");
                if (auth_remain_array[1] == -999) {
                    $oppRBAuth.text((`Right Bishop: 0`));
                } else {
                    $oppRBAuth.text((`Right Bishop: ${auth_remain_array[1]}`));
                }
                break;
        };
    });
    if (!detected_b_corps.includes('kingCorp')) {
        $oppKAuth.text((`King: Captured`));
    }
    if (!detected_b_corps.includes('leftBishopCorp')) {
        $oppLBAuth.text((`Left Bishop: Captured`));
    }
    if (!detected_b_corps.includes('rightBishopCorp')) {
        $oppRBAuth.text((`Right Bishop: Captured`));
    };
};

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
    if ((local_orientation === 'white' && piece.search(/^b/) !== -1) ||
        (local_orientation === 'black' && piece.search(/^w/) !== -1)) {
        return false
    }
    // only pick up pieces for the side to move
    if ((local_whiteMove === true && piece.search(/^b/) !== -1) ||
        (local_whiteMove === false && piece.search(/^w/) !== -1)) {
        return false
    }

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
        };
    };
}

const onSnapEnd = () => {
    board.position(local_boardstate, false);
};

const renderPieceListAnim = (white_captured, black_captured) => {
    let eliminatedPiece = $defending_piece.attr("src");
    let colorOfPiece = (eliminatedPiece.charAt(eliminatedPiece.length - 6) === 'b' ? 'black' : 'white');
    let PlayerCapturedPieces = []
    let OppCapturedPieces = []

    if (local_isAIGame) {
        PlayerCapturedPieces = white_captured;
        OppCapturedPieces = black_captured;

        if (colorOfPiece === "black") {
            OppCapturedPieces.push(eliminatedPiece)
            for (let count = OppCapturedPieces.length; count < OppCapturedPieces.length + 1; count++) {
                var imageElement = $('<img />', { src: OppCapturedPieces[count-1], }).css('width', '40px').css('height', '40px');
                $oppCapturedCon.append(imageElement);
            };
        } else {
            PlayerCapturedPieces.push(eliminatedPiece);
            for (let count = PlayerCapturedPieces.length; count < PlayerCapturedPieces.length + 1; count++) {
                var imageElement = $('<img />', { src: PlayerCapturedPieces[count-1], }).css('width', '40px').css('height', '40px');
                $playerCapturedCon.append(imageElement);
            };
        };
    } else {
        PlayerCapturedPieces = (colorOfPiece === local_orientation ? white_captured : black_captured);
        OppCapturedPieces = (colorOfPiece === local_orientation ? black_captured : white_captured);

        if (colorOfPiece === local_orientation) {
            OppCapturedPieces.push(eliminatedPiece)
            for (let count = OppCapturedPieces.length; count < OppCapturedPieces.length + 1; count++) {
                var imageElement = $('<img />', { src: OppCapturedPieces[count-1], }).css('width', '40px').css('height', '40px');
                $oppCapturedCon.append(imageElement);
            };
        } else {
            PlayerCapturedPieces.push(eliminatedPiece);
            for (let count = PlayerCapturedPieces.length; count < PlayerCapturedPieces.length + 1; count++) {
                var imageElement = $('<img />', { src: PlayerCapturedPieces[count-1], }).css('width', '40px').css('height', '40px');
                $playerCapturedCon.append(imageElement);
            };
        };
    }
};

const setCombatPieces = (attackingPiece, defendingPiece) => {
    $attacking_piece.attr("src", "/static/chessboard/" + attackingPiece + ".png");
    $defending_piece.attr("src", "/static/chessboard/" + defendingPiece + ".png");
    $attacking_piece.css("visibility","visible");
    $defending_piece.css("visibility","visible");
};

const removeCombatPieces = () => {
    $attacking_piece.css("visibility","hidden");
    $defending_piece.css("visibility","hidden");
    $die.css("visibility","hidden");
};

const rollAnimStart = (data) => {
    setCombatPieces(data.activePiece.color + data.activePiece.rank, data.targetPiece.color + data.targetPiece.rank);
    $attack_result.text("Rolling for Attack!").css("color", "grey");
};

const successfullAttack = (rollVal, blitz, white_captured, black_captured, new_boardstate, activePiece, targetPiece) => {
    console.log("successful attack");
    
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
        renderPieceListAnim(white_captured, black_captured);
    } else {
        $attack_result.text("Successful Attack!").css("color", "green").css("visibility","visible");
        renderPieceListAnim(white_captured, black_captured);
    };

    console.log("triggering boardstate move anim from failedAttack");
    setTimeout(board.position(new_boardstate), 500);

    updateAuthRemaining(local_corplist);
    removeCombatPieces();
};

const failedAttack = (rollVal, blitz, new_boardstate, activePiece, targetPiece) => {
    console.log("failed attack");
    
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
    } else {
        $attack_result.text("Failed Attack!").css("color", "red").css("visibility","visible");
    };

    console.log("triggering boardstate move anim from failedAttack");
    setTimeout(board.position(new_boardstate), 500);

    updateAuthRemaining(local_corplist);
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
        successfullAttack(data.roll_val, data.isBlitz, local_white_captured, local_black_captured, data.new_boardstate, data.activePiece, data.targetPiece);
    } else {
        failedAttack(data.roll_val, data.isBlitz, data.new_boardstate, data.activePiece, data.targetPiece);
    };

    renderActionHistory(data.action_history);

    if ("kingDead" in data) {
        var status = 'Game over, ' + (local_whiteMove ? "black" : "white") + ' is in checkmate.';
        if (!local_whiteMove) {
            socket.send(JSON.stringify({"actionType": "GAME_OVER","result": "Black wins"}));
        } else {
            socket.send(JSON.stringify({"actionType": "GAME_OVER","result": "White wins"}));
        };
        $gameModalTitle.html("Game Over")
        $gameModalBody.html(status)
        $('#gameModal').modal({
            keyboard: false,
            backdrop: 'static'
        });
    };

    if (!local_whiteMove && local_isAIGame) {
        startAITurn();
    }
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
    $gameModalTitle.html("Connection closed");
    $gameModalBody.html("Connection closed unexpectedly please wait while we try to reconnect...");
    $('#gameModal').modal({
      keyboard: false,
      backdrop: 'static'
    });
};

// The meat of the JS function here, message processing from WS channel
socket.onmessage = (message) => {
    var data = JSON.parse(message.data);
    console.log(data);

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
            local_readyToBlitz = data.readyToBlitz;
            
            var config = {
                draggable: true,
                dropOffBoard: 'snapback',
                position: 'start',
                onDrop: onDrop,
                onDragStart: onDragStart,
                onSnapEnd: onSnapEnd,
                pieceTheme: '/static/chessboard/{piece}.png',
            };

            // Render chessboard with config
            board = Chessboard('my_board', config);

            board.position(local_boardstate);

            // Set up the captured pieces visualization
            if (local_black_captured != null) {
                local_black_captured.forEach((piece) => {
                    $oppCapturedCon.append($('<img>', {src: `../static/chessboard\\b${piece}.png`, width: "40px", height: "40px"}))
                });
            }
            if (local_white_captured != null) {
                local_white_captured.forEach((piece) => {
                    $playerCapturedCon.append($('<img>', {src: `../static/chessboard\\w${piece}.png`, width: "40px", height: "40px"}))
                });
            }

            updateAuthRemaining(local_corplist);

            renderActionHistory(data.action_history);

            if (!local_whiteMove) {
                startAITurn();
            }
        } else { // Multiplayer game
            // Set local var values
            local_boardstate = data.boardstate;
            local_isAIGame = data.isAIGame;
            local_level = data.level;
            local_whiteMove = data.whiteMove;
            local_corplist = data.corplist;
            local_white_captured = data.white_captured;
            local_black_captured = data.black_captured;
            local_readyToBlitz = data.readyToBlitz;
            local_orientation = data.side;
            local_opp_online = data.local_opp_online;

            var config = {
                draggable: true,
                dropOffBoard: 'snapback',
                position: 'start',
                orientation: local_orientation,
                onDrop: onDrop,
                onDragStart: onDragStart,
                onSnapEnd: onSnapEnd,
                pieceTheme: '/static/chessboard/{piece}.png',
            };

            // Render chessboard with config
            board = Chessboard('my_board', config);

            board.position(local_boardstate);

            // Set up the captured pieces visualization
            if (local_orientation === 'black') {
                if (local_black_captured != null) {
                    local_black_captured.forEach((piece) => {
                        $oppCapturedCon.append($('<img>', {src: `../static/chessboard\\b${piece}.png`, width: "40px", height: "40px"}))
                    });
                }
                if (local_white_captured != null) {
                    local_white_captured.forEach((piece) => {
                        $playerCapturedCon.append($('<img>', {src: `../static/chessboard\\w${piece}.png`, width: "40px", height: "40px"}))
                    });
                };
            };
            if (local_orientation === 'white') {
                if (local_black_captured != null) {
                    local_black_captured.forEach((piece) => {
                        $playerCapturedCon.append($('<img>', {src: `../static/chessboard\\b${piece}.png`, width: "40px", height: "40px"}))
                    });
                }
                if (local_white_captured != null) {
                    local_white_captured.forEach((piece) => {
                        $oppCapturedCon.append($('<img>', {src: `../static/chessboard\\w${piece}.png`, width: "40px", height: "40px"}))
                    });
                };
            };

            updateAuthRemaining(local_corplist);

            renderActionHistory(data.action_history);

            if(local_opp_online != true) {
                $gameModalTitle.html("Please Wait...")
                $gameModalBody.html("Please wait for your opponent to connect to this game")
                $('#gameModal').modal({
                    keyboard: false,
                    backdrop: 'static'
                });
            }
        }
    }
    // On OPPONENT-ONLINE actionType
    else if(data.actionType=="OPPONENT-ONLINE"){
        $('#gameModal').modal('hide');
        $('#gameModal').data('bs.modal',null);
    }
    // On OPPONENT-OFFLINE actionType
    else if(data.actionType=="OPPONENT-OFFLINE"){
        $gameModalTitle.html("Please Wait...")
        $gameModalBody.html("Your opponent suddenly disconnected. Please wait for your opponent to connect to this game")
        $('#gameModal').modal({
            keyboard: false,
            backdrop: 'static'
        });
    }
    // On MOVEMENT actionType
    else if(data.actionType=="MOVEMENT") {
        board.position(local_boardstate, false);

        local_corplist = data.corpList;
        local_boardstate = data.new_boardstate;
        local_whiteMove = data.whiteMove;
        local_readyToBlitz = data.readyToBlitz;
        
        board.position(data.new_boardstate);

        updateAuthRemaining(local_corplist);

        // Append a new entry to the movelog
        renderActionHistory(data.action_history);

        board.position(local_boardstate, false);

        if (!local_whiteMove && local_isAIGame) {
            startAITurn();
        }
    }
    // On ATTACK_ATTEMPT actionType
    else if(data.actionType=="ATTACK_ATTEMPT") {
        board.position(local_boardstate, false);

        local_corplist = data.corpList;
        local_boardstate = data.new_boardstate;
        local_whiteMove = data.whiteMove;
        local_readyToBlitz = data.readyToBlitz;
        
        resolveAttack(data);

        board.position(local_boardstate, false);
    }
    // On HIGHLIGHT actionType
    else if(data.actionType=="HIGHLIGHT") {
        data.in_range.forEach(pos => redSquare(pos));
        data.setup.forEach(pos => greenSquare(pos));
        data.movement.forEach(pos => greySquare(pos));
    }
    // On DELEGATE actionType
    else if(data.actionType=="DELEGATE") {
        local_corplist = data.corpList;
        local_whiteMove = data.whiteMove;
        local_readyToBlitz = data.readyToBlitz;

        updateAuthRemaining(local_corplist);

        if (!local_whiteMove && local_isAIGame) {
            startAITurn();
        }
    }
    // On PASS actionType
    else if(data.actionType=="PASS") {
        local_corplist = data.corpList;
        local_whiteMove = data.whiteMove;
        local_readyToBlitz = data.readyToBlitz;

        updateAuthRemaining(local_corplist);

        if (!local_whiteMove && local_isAIGame) {
            startAITurn();
        }
    }
    // On AI_ACTION_REQ actionType
    else if(data.actionType=="AI_TURN_RES") {
        local_corplist = data.corpList;
        local_boardstate = data.new_boardstate;
        local_whiteMove = data.whiteMove;
        local_readyToBlitz = data.readyToBlitz;
        local_ai_action_list = data.black_actions;
        local_ai_move_list = data.black_moves;

        local_ai_action_list.forEach((action, index) => {
            if (action.actionType == "ATTACK_ATTEMPT") {
                console.log("resolving AI attack");
                resolveAttack(action);
                if (!action.isSuccessfulAttack) {
                    board.position(local_boardstate, false)
                };
            } else if (action.actionType == "MOVEMENT") {
                console.log("resolving AI move");
                console.log(action);
                board.position(action.new_boardstate);
                renderActionHistory(local_ai_action_list[index].action_history);
                setTimeout(() => {}, 3000);
            }

            updateAuthRemaining(local_corplist);
        });
    }
    // On GAME_OVER actionType
    else if(data.actionType=="GAME_OVER") {
        var status = 'Game over, ' + (local_whiteMove ? "black" : "white") + ' successfully captured the opposing king.';
        $gameModalTitle.html("Game Over")
        $gameModalBody.html(status)
        $('#gameModal').modal({
            keyboard: false,
            backdrop: 'static'
        });
    }
    // On OPPONENT_RESIGNED actionType
    else if(data.actionType=="OPPONENT_RESIGNED") {
        $gameModalTitle.html("Game over")
        $gameModalBody.html("Your opponent has resigned from the game. You win!")
        $('#gameModal').modal({
            keyboard: false,
            backdrop: 'static'
        });
    }
    // On CHAT_MESSAGE actionType
    else if(data.actionType=="CHAT_MESSAGE") {
        $chatMessages.append(`<b>${data.username}</b>: ${data.message}<br>`);
    }
};

// ***** DELEGATE MODAL EVENT HANDLERS ***
// Initial delegate button click
$(document).on('click','#delegate', () => {
    $('#delegateModal').modal({
        keyboard: false,
        backdrop: 'static'
    });

    if (local_isAIGame) {
        const kingDelegatables = [];
        $kingDelegateMenuContents.empty();
        $kingDelegateMenuContents.append($('<h5>').text('Which Piece'));
        if ((local_whiteMove) === true) {
            if (local_whiteMove) {
                Object.entries(local_corplist.w).forEach((corpKey) => {
                    if (corpKey[0] == 'kingCorp') {
                        corpKey[1].under_command.forEach((piece) => {
                            kingDelegatables.push(piece);
                        });
                    };
                });
            } else {
                Object.entries(local_corplist.b).forEach((corpKey) => {
                    if (corpKey[0] == 'kingCorp') {
                        corpKey[1].under_command.forEach((piece) => {
                            kingDelegatables.push(piece);
                        });
                    };
                });
            };

            kingDelegatables.forEach((piece) => {
                const $interimCheckGroup = $('<div>', {class: "form-check"});
                $interimCheckGroup.append($('<input>', {class: "form-check-input", type:"radio", name:`kingDelegateablesRadio`, id:`${piece.color}${piece.rank}-radio`, value:JSON.stringify(piece)}));
                $interimCheckGroup.append($('<label>', {class: "form-check-label", for:`${piece.color}${piece.rank}-radio`}).text(`${piece.color}${piece.rank} at ${piece.pos}`));
                $kingDelegateMenuContents.append($interimCheckGroup);
            });
        }
        
        const targetCorps = [];
        $targetCorpMenuContents.empty();
        $targetCorpMenuContents.append($('<h5>').text('Which Destination Corp'));
        if (local_whiteMove) {
            Object.entries(local_corplist.w).forEach((corpKey) => {
                if (corpKey[0] != 'kingCorp' && corpKey[1].under_command.length <= 6) {
                    targetCorps.push(corpKey[0]);
                };
            });

            targetCorps.forEach((corp) => {
                const $interimCheckGroup = $('<div>', {class: "form-check"});
                $interimCheckGroup.append($('<input>', {class: "form-check-input", type:"radio", name:`targetCorpRadio`, id:`${corp}-radio`, value:corp}));
                $interimCheckGroup.append($('<label>', {class: "form-check-label", for:`${corp}-radio`}).text(corp));
                $targetCorpMenuContents.append($interimCheckGroup);
            });
        };

            
    } else {
        const kingDelegatables = [];
        $kingDelegateMenuContents.empty();
        $kingDelegateMenuContents.append($('<h5>').text('Which Piece'));
        if ((local_whiteMove) === (local_orientation === 'white')) {
            if (local_whiteMove) {
                Object.entries(local_corplist.w).forEach((corpKey) => {
                    if (corpKey[0] == 'kingCorp') {
                        corpKey[1].under_command.forEach((piece) => {
                            kingDelegatables.push(piece);
                        });
                    };
                });
            } else {
                Object.entries(local_corplist.b).forEach((corpKey) => {
                    if (corpKey[0] == 'kingCorp') {
                        corpKey[1].under_command.forEach((piece) => {
                            kingDelegatables.push(piece);
                        });
                    };
                });
            };

            kingDelegatables.forEach((piece) => {
                const $interimCheckGroup = $('<div>', {class: "form-check"});
                $interimCheckGroup.append($('<input>', {class: "form-check-input", type:"radio", name:`kingDelegateablesRadio`, id:`${piece.color}${piece.rank}-radio`, value:JSON.stringify(piece)}));
                $interimCheckGroup.append($('<label>', {class: "form-check-label", for:`${piece.color}${piece.rank}-radio`}).text(`${piece.color}${piece.rank} at ${piece.pos}`));
                $kingDelegateMenuContents.append($interimCheckGroup);
            });
        }
        
        const targetCorps = [];
        $targetCorpMenuContents.empty();
        $targetCorpMenuContents.append($('<h5>').text('Which Destination Corp'));
        if ((!local_whiteMove) === (local_orientation === 'black')) {
            if (local_whiteMove) {
                Object.entries(local_corplist.w).forEach((corpKey) => {
                    if (corpKey[0] != 'kingCorp' && corpKey[1].under_command.length <= 6) {
                        targetCorps.push(corpKey[0]);
                    };
                });
            } else {
                Object.entries(local_corplist.b).forEach((corpKey) => {
                    if (corpKey[0] != 'kingCorp' && corpKey[1].under_command.length <= 6) {
                        targetCorps.push(corpKey[0]);
                    };
                });
            };

            targetCorps.forEach((corp) => {
                const $interimCheckGroup = $('<div>', {class: "form-check"});
                $interimCheckGroup.append($('<input>', {class: "form-check-input", type:"radio", name:`targetCorpRadio`, id:`${corp}-radio`, value:corp}));
                $interimCheckGroup.append($('<label>', {class: "form-check-label", for:`${corp}-radio`}).text(corp));
                $targetCorpMenuContents.append($interimCheckGroup);
            });
        };
    };
});

// 
$(document).on('click','#confirmDelegate', () => {
    const delegatedPiece = $('input[name="kingDelegateablesRadio"]').filter(':checked').val();
    const targetCorp = $('input[name="targetCorpRadio"]').filter(':checked').val();
    console.log(delegatedPiece);
    socket.send(JSON.stringify({"actionType": "DELEGATE", "isAIGame": local_isAIGame, "whiteMove": local_whiteMove, "delegatedPiece": delegatedPiece, "targetCorp": targetCorp}));
    $('#delegateModal').modal('hide');
    $('#delegateModal').data('bs.modal',null);
});

// ***** PASS MODAL EVENT HANDLERS ***
// Initial pass button click
$(document).on('click','#pass', () => {
    $('#passModal').modal({
        keyboard: false,
        backdrop: 'static'
    });
});

// Choose not to pass
$(document).on('click','#noPass', () => {
    $('#passModal').modal('hide');
    $('#passModal').data('bs.modal',null);
});

// Double down on passing
$(document).on('click','#yesPass', () => {
    socket.send(JSON.stringify({"actionType": "PASS", "isAIGame": local_isAIGame, "whiteMove": local_whiteMove}));
    $('#passModal').modal('hide');
    $('#passModal').data('bs.modal',null);
});

// ***** RESIGN MODAL EVENT HANDLERS ***
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
    $resModalTitle.html("Game over");
    $resModalBody.html("You have resigned from the game. You lose!");
    $('#gameModal').modal({
        keyboard: false,
        backdrop: 'static'
    });
});

// Move log autoscroll down + absolute pos
$move_log.ready(() => {
    $move_log.scrollTop($move_log.prop("scrollHeight"));
});
$move_log.on('DOMSubtreeModified', () => {
    $move_log.scrollTop($move_log.prop("scrollHeight"));
});

// Chat autoscroll down + absolute pos
$chatMessages.ready(() => {
    $chatMessages.scrollTop($chatMessages.prop("scrollHeight"));
});
$chatMessages.on('DOMSubtreeModified', () => {
    $chatMessages.scrollTop($chatMessages.prop("scrollHeight"));
});

// Enter in chat is a submit
$chatInput.keyup((event) => {
    if (event.keyCode == 13) {
        $chatSubmit.click();
    };
});

$chatSubmit.on('click',() => {
    const message = $chatInput.val();
    console.log()

    socket.send(JSON.stringify({
        'actionType': "CHAT_MESSAGE",
        'isAIGame': local_isAIGame,
        'message': message,
        'username': userName,
        'game_id': game_id
    }));

    $chatInput.val('');
});
