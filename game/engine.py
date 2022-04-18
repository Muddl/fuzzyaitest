# The Game Engine for Chess. Interfaces will need to be built to send to this.
# NOTE: We figured the due date for this prototype was the due date listed on D2l, not the presentation date.
# We also were roughly following the sprint cycle chart given in the first week's presentation.
# Next in progress for engine: Add knight blitzes, end states, timers, and a hook for the AI to latch into.
from typing import Dict
import random, json, uuid
from enum import Enum

# Constants
INITIAL_BOARDSTATE = {
    # Formatted as Position Object for Chessboard.js
    # Black side
    "a8": "bR", "b8": "bN", "c8": "bB", "d8": "bQ", "e8": "bK", "f8": "bB", "g8": "bN", "h8": "bR",
    "a7": "bP", "b7": "bP", "c7": "bP", "d7": "bP", "e7": "bP", "f7": "bP", "g7": "bP", "h7": "bP",
    
    # White side
    "a2": "wP", "b2": "wP", "c2": "wP", "d2": "wP", "e2": "wP", "f2": "wP", "g2": "wP", "h2": "wP",
    "a1": "wR", "b1": "wN", "c1": "wB", "d1": "wQ", "e1": "wK", "f1": "wB", "g1": "wN", "h1": "wR",
}

# Enums
class Color(Enum):
    WHITE = "w"
    BLACK = "b"

class Rank(Enum):
    KING ="K"
    QUEEN = "Q"
    KNIGHT = "N"
    ROOK = "R"
    BISHOP = "B"
    PAWN = "P"

class WinFlag(Enum): # 0 for no kings captured, 1 for white king captured, 2 for black king captured
    NONE = 0
    WHITE = 1
    BLACK = 2

class ActionType(Enum):
    MOVEMENT = "MOVEMENT"
    ATTACK_ATTEMPT = "ATTACK_ATTEMPT"
    HIGHLIGHT = "HIGHLIGHT"

# Classes

class Piece:
    def __init__(self, color, rank, pos):
        self.color = color
        self.rank = rank
        self.pos = pos
    
    def getColor(self):
        return self.color
    
    def getRank(self):
        return self.rank
    
    def getPos(self):
        return self.pos
    
    def getPair(self):
        return { self.pos: (self.color + self.rank) }
    
    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.getPair() == other.getPair()        

class Action:
    def __init__(self, parsedActionType, parsedActivePiece, parsedTargetPiece):
        self.actionType = ActionType(parsedActionType)
        self.activePiece = Piece(Color(parsedActivePiece["color"]), Rank(parsedActivePiece["rank"]), parsedActivePiece["pos"])
        if (self.actionType == ActionType.MOVEMENT) or (self.actionType == ActionType.ATTACK_ATTEMPT):
            self.targetPiece = Piece(Color(parsedTargetPiece["color"]), Rank(parsedTargetPiece["rank"]), parsedTargetPiece["pos"])
        else:
            self.targetPiece = None
        self.actionID = uuid.uuid4()
    
    # Overrides the equal method for moves. A move = another move - IMPORTANT
    def __eq__(self, other):
        if isinstance(other, Action):
            return self.actionID == other.actionID
        return False

class Boardstate:
    # Initializes an empty board and game in code (not gui)
    def __init__(self, boardstate: Dict[str, str], whiteMove: bool, actionCounter: int):
        # Game board from white's perspective
        # NOTE - I've seen this done with just strings, numbers, etc.
        # All are probably more efficient but a pain to read and work with
        
        self.board = boardstate
        
        self.attackDict = {
            "K": {"K": 4, "Q": 4, "N": 4, "B": 4, "R": 5, "P": 1},
            "Q": {"K": 4, "Q": 4, "N": 4, "B": 4, "R": 5, "P": 2},
            "N": {"K": 4, "Q": 4, "N": 4, "B": 4, "R": 5, "P": 2},
            "B": {"K": 5, "Q": 5, "N": 5, "B": 4, "R": 5, "P": 3},
            "R": {"K": 4, "Q": 4, "N": 4, "B": 5, "R": 5, "P": 5},
            "P": {"K": 6, "Q": 6, "N": 6, "B": 5, "R": 5, "P": 4},
        }
        
        self.whiteMove = whiteMove  # Keeps track of whose turn it is
        self.actionCounter = actionCounter  # Counts number of moves (or actions) made
        self.kingDead = WinFlag(0) # Initially no kings dead  
        self.knightsAttacked = []  # Stores the position of knights that have attempted an attack already
        self.blitzableKnightSquares = []  # Stores the possible squares a knight could blitz from.
        self.gameHistory = []  # Keeps a history of the actions in a game.
    
    # Function that moves the pieces, adds it to the game history, and swaps players - IMPORTANT
    def processAction(self, parsedAction):
        if (parsedAction["actionType"] == "MOVEMENT"):
            activePos = parsedAction["activePiece"]["pos"]
            activeColor = parsedAction["activePiece"]["color"]
            activeRank = parsedAction["activePiece"]["rank"]
            
            targetPos = parsedAction["targetPiece"]["pos"]
            targetRank = parsedAction["targetPiece"]["rank"]
            
            (empt_spaces, enem_spaces) = self.getValidMoveset(Piece(activeColor, activeRank, activePos))
            
            if activePos in self.board: # Selected tile must contain a piece on the board
                if targetPos in empt_spaces:  # If the square is in the piece's empty_squares set
                    curPiece = self.board.pop(activePos)  # Sets the square that the piece is on to empty (the piece is "lifted" from the table)
                    self.board[targetPos] = curPiece  # "Places" the piece onto that square
                    
                    # Cleanup
                    self.actionCounter = self.actionCounter + 1

                    if (activeRank == "N"): # Add knight to moved
                        self.knightsAttacked.append(targetPos)
                        # TODO: Add knight blitzable squares calc here
                    if (self.actionCounter == 3):
                        self.actionCounter = 0
                        self.whiteMove = not self.whiteMove  # Swaps players.
                        self.knightsAttacked = []
                        self.altKnightSquares = {}
                    self.gameHistory.append(parsedAction)  # Adds the action to the game history
                    
                    return True, self.board, self.actionCounter, self.whiteMove
                else:
                    return False, None
            else:
                return False, None
                    
        elif (parsedAction["actionType"] == "ATTACK_ATTEMPT"):
            activePos = parsedAction["activePiece"]["pos"]
            activeColor = parsedAction["activePiece"]["color"]
            activeRank = parsedAction["activePiece"]["rank"]
            
            targetPos = parsedAction["targetPiece"]["pos"]
            targetRank = parsedAction["targetPiece"]["rank"]
            
            (empt_spaces, enem_spaces) = self.getValidMoveset(Piece(activeColor, activeRank, activePos))
            
            if activePos in self.board: # Selected tile must contain a piece on the board
                if targetPos in enem_spaces:
                    if activeRank == "N" and parsedAction["blitz"]: # Check for blitz flag
                        if ((activePos not in self.knightsAttacked) and (targetPos in self.blitzableKnightSquares)): # Check for valid blitz parameters
                            (outcome, roll_val) = self.attackResolver(activeRank, targetRank, True) # Blitz outcome
                            self.knightsAttacked = targetPos
                            self.blitzableKnightSquares = []
                    else:
                        (outcome, roll_val) = self.attackResolver(activeRank, targetRank, False) # Normal combat outcome
                    
                    if outcome and activeRank != "R": # On successful capture
                        curPiece = self.board.pop(activePos)  # Sets the square that the piece is on to empty (the piece is "lifted" from the table)
                        self.board[targetPos] = curPiece  # "Places" the piece onto that square
                    elif outcome and activeRank == "R":
                        self.board.pop(targetPos)
                    
                    # Cleanup
                    self.actionCounter = self.actionCounter + 1
                    # Post combat check
                    if (outcome and targetRank == "K"): # Game over?
                        self.kingDead = WinFlag(1) if activeColor == "w" else WinFlag(2) # Set to proper color
                    if self.actionCounter == 3:
                        self.actionCounter = 0
                        self.whiteMove = not self.whiteMove  # Swaps players.
                        self.knightsAttacked = []
                        self.altKnightSquares = {}
                    self.gameHistory.append(parsedAction)  # Adds the action to the game history
                    
                    if activeRank == "N" and parsedAction["blitz"]:
                        return True, outcome, self.board, roll_val, self.actionCounter, self.whiteMove, parsedAction["blitz"]
                    else:
                        return True, outcome, self.board, roll_val, self.actionCounter, self.whiteMove
                else:
                    print("failed targetPos in enem_spaces")
                    return False, False, None, -1, False
            else:
                print("failed activePos in self.board")
                return False, False, None, -1, False
                    
        elif (parsedAction["actionType"] == "HIGHLIGHT"):
            activePos = parsedAction["activePiece"]["pos"]
            activeColor = parsedAction["activePiece"]["color"]
            activeRank = parsedAction["activePiece"]["rank"]
            (empt_spaces, enem_spaces) = self.getValidMoveset(Piece(activeColor, activeRank, activePos))
            
            if activePos in self.board:
                return True, (empt_spaces + enem_spaces)
            else:
                return False, None
    
    # Resolves an attack attempt, taking in the rank of the attacker, the rank of the defender, and whether the attack is a blitz or not (prevalidated)
    def attackResolver(self, attacker, defender, blitz):
        roll = random.randint(1, 6)  # Rolls the dice
        if roll >= (self.attackDict[attacker][defender] - 1 if blitz else self.attackDict[attacker][defender]):
            print("Attack succeeds")
            return (True, roll)
        else:
            print("Attack fails")
            return (False, roll)

    def getValidMoveset(self, selected):
        match selected.rank:
            case 'P':
                return self.getPawnValidMoveset(selected)
            case 'B':
                return self.getBishopValidMoveset(selected)
            case 'R':
                return self.getRookValidMoveset(selected)
            case 'K':
                return self.getValidRoyalMoveset(selected)
            case 'Q':
                return self.getValidRoyalMoveset(selected)
            case 'N':
                return self.getValidKnightMoveset(selected)
            case _:
                return ([], [])
    
    # Pawns can only move forward, but they CAN move diagonally as well as attack diagonally, so long as it's toward enemy
    def getPawnValidMoveset(self, selected):
        selectedColor = selected.getColor()
        selectedRank = selected.getRank()
        selectedPos = selected.getPos()
        
        empty_spaces = []
        enemy_spaces = []
        
        base_list = getAdjSquares(selectedPos, True) # Base surrounding adjacent squares for current pawn position
        
        if selectedRank == "P" and self.actionCounter < 3: # Confirm we've been passed a pawn & actions remain
            if (self.whiteMove and selectedColor == "w"): # Relative forward movement to white play
                for position in base_list:
                    if int(position[1]) > int(selectedPos[1]): # If space is relatively forward
                        if (not (position in self.board)): # If empty
                            empty_spaces.append(position)
                        elif (self.board.get(position)[0] == "b"): # If enemy
                            enemy_spaces.append(position)
            elif ((not self.whiteMove) and selectedColor == "b"): # Relative forward movement to black play
                for position in base_list:
                    if int(position[1]) < int(selectedPos[1]): # If space is relatively forward
                        if (not (position in self.board)): # If empty
                            empty_spaces.append(position)
                        elif (self.board.get(position)[0] == "w"): # If enemy
                            enemy_spaces.append(position)
        
        return (empty_spaces, enemy_spaces)
    
    def getBishopValidMoveset(self, selected):
        selectedColor = selected.getColor()
        selectedRank = selected.getRank()
        selectedPos = selected.getPos()
        enemy = 'b' if self.whiteMove else 'w'

        base_list = getAdjSquares(selectedPos, True)
        empty_spaces = []
        enemy_spaces = []

        if selectedRank == 'B' and self.actionCounter < 3:
            if selectedColor != enemy:
                for position in base_list:
                    sublist = getAdjSquares(position, True)
                    for subpos in sublist:
                        if subpos not in self.board:
                            if subpos not in empty_spaces:
                                empty_spaces.append(subpos)
                        elif self.board.get(subpos)[0] == enemy:
                            enemy_spaces.append(subpos)

        return (empty_spaces, enemy_spaces)
    
    def getRookValidMoveset(self, selected):
        selectedColor = selected.getColor()
        selectedRank = selected.getRank()
        selectedPos = selected.getPos()
        enemy = 'b' if self.whiteMove else 'w'

        base_list = getAdjSquares(selectedPos, True)
        empty_spaces = []
        enemy_spaces = []

        if selectedRank == 'R' and self.actionCounter < 3:
            if selectedColor != enemy:
                # Movement
                for position in base_list:
                    sublist = getAdjSquares(position, True)
                    for subpos in sublist:
                        if subpos not in self.board:
                            if subpos not in empty_spaces:
                                empty_spaces.append(subpos)
                        elif self.board.get(subpos)[0] == enemy:
                            enemy_spaces.append(subpos)

                # Calculate all the squares the rook can target for an attack
                east_range = ord(selectedPos[0]) + 3
                west_range = ord(selectedPos[0]) - 3
                north_range = int(selectedPos[1]) + 3
                south_range = int(selectedPos[1]) - 3

                # Iterates through each square and checks that a square is not out of bounds and is an enemy
                for r in range(south_range, north_range + 1):
                    if 0 < r < 9:
                        for c in range(west_range, east_range + 1):
                            if 96 < c < 106:
                                target = str(chr(c)) + str(r)
                                if target in self.board:
                                    if self.board[target][0] == enemy and target not in enemy_spaces:
                                        enemy_spaces.append(target)
        return (empty_spaces, enemy_spaces)
    
    # For both kings and queens
    def getValidRoyalMoveset(self, selected):
        selectedColor = selected.getColor()
        selectedRank = selected.getRank()
        selectedPos = selected.getPos()
        enemy = 'b' if self.whiteMove else 'w'

        base_list = getAdjSquares(selectedPos, True)
        empty_spaces = []
        enemy_spaces = []

        if (selectedRank in ["K", "Q"] and self.actionCounter < 3):
            if selectedColor != enemy:
                for position in base_list:
                    sublist = getAdjSquares(position, True)
                    for subpos in sublist:
                        metalist = getAdjSquares(subpos, True)
                        for metapos in metalist:
                            if metapos not in self.board:
                                if metapos not in empty_spaces:
                                    empty_spaces.append(metapos)
                            elif self.board.get(metapos)[0] == enemy:
                                if metapos not in enemy_spaces:
                                    enemy_spaces.append(metapos)
        
        return (empty_spaces, enemy_spaces)
    
    def getValidKnightMoveset(self, selected):
        selected_color = selected.getColor()
        selected_rank = selected.getRank()
        selected_pos = selected.getPos()
        enemy = 'b' if self.whiteMove else 'w'

        empty_squares = []
        enemy_squares = []

        base_list = getAdjSquares(selected_pos, True)
        if selected_rank == 'N':
            if selected_color != enemy:
                # A knight cannot attack then move, but it can repeatedly attack after its initial attack.
                # As such, adjacent enemies will still be added.
                if selected_pos in self.knightsAttacked:
                    for position in base_list:
                        if position in self.board:
                            if self.board[0] == enemy:
                                enemy_squares.append(position)

                else:
                    counter = 0
                    container = []
                    while counter < 5:
                        step_list = []
                        if counter == 0:
                            for position in base_list:
                                if position not in self.board:
                                    empty_squares.append(position)
                                    step_list.append(position)
                                elif self.board[position][0] is enemy:
                                    enemy_squares.append(position)
                            container.append(step_list)
                        elif counter < 4:
                            for position in container[counter - 1]:
                                step_list2 = getAdjSquares(position, True)
                                for i in step_list2:
                                    if i not in self.board and i not in empty_squares:
                                        empty_squares.append(i)
                                        step_list.append(i)
                                    elif i in self.board and i not in enemy_squares:
                                        if self.board[i][0] == enemy:
                                            enemy_squares.append(i)

                            container.append(step_list)
                        else:
                            for position in container[counter - 1]:
                                step_list2 = getAdjSquares(position, True)
                                for i in step_list2:
                                    if i in self.board and i not in enemy_squares:
                                        if self.board[i][0] == enemy:
                                            enemy_squares.append(i)
                        counter += 1

            # Cross check the empty squares and enemy squares and give valid landing squares for a blitz
            # IMPORTANT NOTE - I don't know how the knightLanding Squares are going to be stored/handled.
            # The following code creates a dictionary that stores an array of the valid squares the knight can land for a blitz.
            blitzDict = {}
            for i in enemy_squares:
                blitzDict[i] = []

            for i in blitzDict:
                tempList = getAdjSquares(i, True)
                for j in tempList:
                    if j in empty_squares:
                        blitzDict[i].append(j)
            self.blitzableKnightSquares = blitzDict

        return (empty_squares, enemy_squares)
            

# Recieves an algebraic position on the board and a boolean representing if the returned list should include diagonal adjancencies
# Returns a list of algebraic positions adjacent to the passed position
def getAdjSquares(pos, diag):
    col_int = ord(pos[0])
    row = int(pos[1])
    adj = []
    corners = ["a1", "a8", "h1", "h8"]
    edges = [
                "a2", "a3", "a4", "a5", "a6", "a7", # Left edge minus corners
                "h2", "h3", "h4", "h5", "h6", "h7", # Right edge minus corners
                "b8", "c8", "d8", "e8", "f8", "g8", # Top edge minus corners
                "b1", "c1", "d1", "e1", "f1", "g1", # Bot edge minus corners
            ]
    if (pos in corners):
        if pos == "a1": adj = ["a2", "b1", "b2"] if diag else ["a2", "b1"]
        if pos == "a8": adj = ["a7", "b7", "b8"] if diag else ["a7", "b8"]
        if pos == "h1": adj = ["g1", "g2", "h2"] if diag else ["g1", "h2"]
        if pos == "h8": adj = ["g7", "g8", "h7"] if diag else ["g8", "h7"]
    
    if (pos in edges):
        if chr(col_int) == "a": # Left edge minus corners
            adj = [f"a{str(row+1)}", f"a{str(row-1)}", f"b{str(row)}"] if not diag else [f"a{str(row+1)}", f"a{str(row-1)}", f"b{str(row)}", f"b{str(row-1)}", f"b{str(row+1)}"]
        if chr(col_int) == "h": # Right edge minus corners
            adj = [f"h{str(row+1)}", f"h{str(row-1)}", f"g{str(row)}"] if not diag else [f"h{str(row+1)}", f"h{str(row-1)}", f"g{str(row)}", f"g{str(row-1)}", f"g{str(row+1)}"]
        if row == 8: # Top edge minus corners
            adj = [f"{chr(col_int+1)}8", f"{chr(col_int-1)}8", f"{chr(col_int)}7"] if not diag else [f"{chr(col_int+1)}8", f"{chr(col_int-1)}8", f"{chr(col_int)}7", f"{chr(col_int+1)}7", f"{chr(col_int-1)}7"]
        if row == 1: # Bot edge minus corners
            adj = [f"{chr(col_int+1)}1", f"{chr(col_int-1)}1", f"{chr(col_int)}2"] if not diag else [f"{chr(col_int+1)}1", f"{chr(col_int-1)}1", f"{chr(col_int)}2", f"{chr(col_int+2)}7", f"{chr(col_int-1)}2"]
    
    if ((pos not in edges) and (pos not in corners)):
        adj = [f"{chr(col_int)}{str(row+1)}", f"{chr(col_int)}{str(row-1)}", f"{chr(col_int+1)}{str(row)}", f"{chr(col_int-1)}{str(row)}"] if not diag else [f"{chr(col_int)}{str(row+1)}", f"{chr(col_int)}{str(row-1)}", f"{chr(col_int+1)}{str(row+1)}", f"{chr(col_int-1)}{str(row-1)}", f"{chr(col_int+1)}{str(row)}", f"{chr(col_int-1)}{str(row)}", f"{chr(col_int+1)}{str(row-1)}", f"{chr(col_int-1)}{str(row+1)}"]
    
    return adj

# IMPORTANT - Instead of using isMoveBlocked, we have 2 helper functions: getDirection and getLine.
# Each piece that uses this line can move diagonally, so we didn't need that distinction
# getDirection basically just gives numbers to represent N, S, E, and W, and sums them for the diagonals
# The two functions together result in an appended empty_squares array for the bishop and rook calls
def getDirection(startPos, endPos):
    direction = 0
    # The ones digit represents vertical direction with +1 being N, -1 being S, and 0 being neither
    if int(endPos[1]) > int(startPos[1]):  # NORTH
        direction += 1
    elif int(endPos[1]) < int(startPos[1]):  # SOUTH
        direction -= 1

    # Similarly, the tens' digit represents horizontal direction: -10 is West, +10 is East, 0 is neither
    # For diagonal directions, you get values like (+1)(0) = 10 or (+1)(-1) = 9 or (0)(-1) = -1
    if ord(endPos[0]) < ord(startPos[0]):  # WEST
        direction -= 10
    elif ord(endPos[0]) > ord(startPos[0]):  # EAST
        direction += 10

    return direction


def getLine(board, empty_spaces, selectedPos, targetPos):
    # Calculates the squares outside of adjacency for bishops and rooks (can move 2 in any direction in a line)
    match getDirection(selectedPos, targetPos):
        case 1:  # Directly North
            for row in range(int(selectedPos[1]), int(targetPos[1])):
                current_pos = selectedPos[0] + str(row)
                if current_pos not in board:
                    empty_spaces.append(current_pos)

        case -1:  # Directly South
            for row in range(int(targetPos[1]), int(selectedPos[1])):
                current_pos = selectedPos[0] + str(row)
                if current_pos not in board:
                    empty_spaces.append(current_pos)

        case 10:  # Directly East
            norm_selectedPos = ord(selectedPos[0]) - ord("a")
            norm_targetPos = ord(targetPos[0]) - ord("a")
            distance = norm_targetPos - norm_selectedPos
            for col in range(norm_selectedPos, norm_selectedPos + distance):
                current_pos = chr(col + ord("a")) + selectedPos[1]
                if current_pos not in board:
                    empty_spaces.append(current_pos)

        case -10:  # Directly West
            norm_selectedPos = ord(selectedPos[0]) - ord("a")
            norm_targetPos = ord(targetPos[0]) - ord("a")
            distance = norm_selectedPos - norm_targetPos
            for col in range(norm_targetPos, norm_targetPos + distance):
                current_pos = chr(col + ord("a")) + selectedPos[1]
                if current_pos not in board:
                    empty_spaces.append(current_pos)

        case 11:  # North + West
            norm_selectedCol = ord(selectedPos[0]) - ord("a")
            diagDistance = int(targetPos[1]) - int(selectedPos[1])
            for current_offset in range(1, diagDistance):
                current_pos = str(chr(norm_selectedCol - current_offset + ord("a")) + str(int(selectedPos[1] + current_offset)))
                if current_pos not in board:
                    empty_spaces.append(current_pos)

        case -9:  # South + West
            norm_selectedCol = ord(selectedPos[0]) - ord("a")
            diagDistance = int(targetPos[1]) - int(selectedPos[1])
            for current_offset in range(1, diagDistance):
                current_pos = str(chr(norm_selectedCol - current_offset + ord("a")) + str(int(selectedPos[1] - current_offset)))
                if current_pos not in board:
                    empty_spaces.append(current_pos)

        case 9:  # North + East
            norm_selectedCol = ord(selectedPos[0]) - ord("a")
            diagDistance = int(targetPos[1]) - int(selectedPos[1])
            for current_offset in range(1, diagDistance):
                current_pos = str(chr(norm_selectedCol + current_offset + ord("a")) + str(int(selectedPos[1] + current_offset)))
                if current_pos not in board:
                    empty_spaces.append(current_pos)

        case -11:  # South + East
            norm_selectedCol = ord(selectedPos[0]) - ord("a")
            diagDistance = int(targetPos[1]) - int(selectedPos[1])
            for current_offset in range(1, diagDistance):
                current_pos = str(chr(norm_selectedCol + current_offset + ord("a")) + str(int(selectedPos[1] - current_offset)))
                if current_pos not in board:
                    empty_spaces.append(current_pos)

    return empty_spaces

def newboard():
    return INITIAL_BOARDSTATE