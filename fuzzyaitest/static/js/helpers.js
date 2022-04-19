// Helpers.js holds helper functions utilized within the game.js module

export const AiMove = (oldPos, newPos, blackActionCounter) => {
    if (blackActionCounter != -1) {
        board.move(oldPos + '-' + newPos);
    }
};

//sorts fen
export const sortAlphabet = (str) => {
    return [...str].sort().join("");
};

export const difference = (previousPos, currentPos) => {
    let keyFound = false;
    Object.keys(previousPos).forEach(key => {
        if(previousPos[key] !== currentPos[key]) {
            return keyFound = key;
        };
    });
    return keyFound || -1;
};

export const haveSameData = (obj1, obj2) => {
    const obj1Length = Object.keys(obj1).length;
    const obj2Length = Object.keys(obj2).length;

    if (obj1Length === obj2Length) {
    return Object.keys(obj1).every(
        key => obj2.hasOwnProperty(key)
            && obj2[key] === obj1[key]);
    }
    return false;
};

export const removeHighlightedSquares = () => {
    $('#my_board .square-55d63').css('background', '')
};

export const redSquare = (square) => {
    const whiteSquareRed = '#e54242';
    const blackSquareRed = '#bf0f0f';  

    var $square = $('#my_board .square-' + square)

    var bg = whiteSquareRed;
    if ($square.hasClass('black-3c85d')) {
        bg = blackSquareRed;
    }

    $square.css('background', bg)
};

export const greenSquare = (square) => {
    const whiteSquareGreen = '#4fdd39';
    const blackSquareGreen = '#27b211';  

    var $square = $('#my_board .square-' + square)

    var bg = whiteSquareGreen;
    if ($square.hasClass('black-3c85d')) {
        bg = blackSquareGreen;
    }

    $square.css('background', bg)
};

export const greySquare = (square) => {
    const whiteSquareGrey = '#a9a9a9';
    const blackSquareGrey = '#696969';  

    var $square = $('#my_board .square-' + square)

    var bg = whiteSquareGrey;
    if ($square.hasClass('black-3c85d')) {
        bg = blackSquareGrey;
    }

    $square.css('background', bg)
};