# The Game Engine for Chess. Interfaces will need to be built to send to this.
# NOTE: We figured the due date for this prototype was the due date listed on D2l, not the presentation date.
# We also were roughly following the sprint cycle chart given in the first week's presentation.
# Next in progress for engine: Add knight blitzes, end states, timers, and a hook for the AI to latch into.
from typing import Dict
import random, re, traceback

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

INITIAL_CORP_LIST = {
    "w": {
        "kingCorp": {
            "leader": {
                "pos": "e1",
                "color" : "w",
                "rank" : "K",
                "corp" : "kingCorp"
            },
            "under_command": [
                {
                    "pos": "a1",
                    "color" : "w",
                    "rank" : "R",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "h1",
                    "color" : "w",
                    "rank" : "R",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "d1",
                    "color" : "w",
                    "rank" : "Q",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "d2",
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "e2",
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "kingCorp"
                }
            ],
            "command_authority_remaining": 1
        },
        "leftBishopCorp": {
            "leader": {
                "pos": "c1",
                "color" : "w",
                "rank" : "B",
                "corp" : "leftBishopCorp"
            },
            "under_command": [
                {
                    "pos": "a2",
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "leftBishopCorp"
                },
                {
                    "pos": "b2",
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "leftBishopCorp"
                },
                {
                    "pos": "c2",
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "leftBishopCorp"
                },
                {
                    "pos": "b1",
                    "color" : "w",
                    "rank" : "N",
                    "corp" : "leftBishopCorp"
                }
            ],
            "command_authority_remaining": 1
        },
        "rightBishopCorp": {
            "leader": {
                "pos": "f1",
                "color" : "w",
                "rank" : "B",
                "corp" : "rightBishopCorp"
            },
            "under_command": [
                {
                    "pos": "f2",
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "rightBishopCorp"
                },
                {
                    "pos": "g2",
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "rightBishopCorp"
                },
                {
                    "pos": "h2",
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "rightBishopCorp"
                },
                {
                    "pos": "g1",
                    "color" : "w",
                    "rank" : "N",
                    "corp" : "rightBishopCorp"
                }
            ],
            "command_authority_remaining": 1
        }
    },
    "b": {
        "kingCorp": {
            "leader": {
                "pos": "e8",
                "color" : "b",
                "rank" : "K",
                "corp" : "kingCorp"
            },
            "under_command": [
                {
                    "pos": "a8",
                    "color" : "b",
                    "rank" : "R",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "h8",
                    "color" : "b",
                    "rank" : "R",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "d8",
                    "color" : "b",
                    "rank" : "Q",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "d7",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "e7",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "kingCorp"
                }
            ],
            "command_authority_remaining": 1
        },
        "leftBishopCorp": {
            "leader": {
                "pos": "c8",
                "color" : "b",
                "rank" : "B",
                "corp" : "leftBishopCorp"
            },
            "under_command": [
                {
                    "pos": "a7",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "leftBishopCorp"
                },
                {
                    "pos": "b7",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "leftBishopCorp"
                },
                {
                    "pos": "c7",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "leftBishopCorp"
                },
                {
                    "pos": "b8",
                    "color" : "b",
                    "rank" : "N",
                    "corp" : "leftBishopCorp"
                }
            ],
            "command_authority_remaining": 1
        },
        "rightBishopCorp": {
            "leader": {
                "pos": "f8",
                "color" : "b",
                "rank" : "B",
                "corp" : "rightBishopCorp"
            },
            "under_command": [
                {
                    "pos": "f7",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "rightBishopCorp"
                },
                {
                    "pos": "g7",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "rightBishopCorp"
                },
                {
                    "pos": "h7",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "rightBishopCorp"
                },
                {
                    "pos": "g8",
                    "color" : "b",
                    "rank" : "N",
                    "corp" : "rightBishopCorp"
                }
            ],
            "command_authority_remaining": 1
        }
    }
}

# Classes

class Piece:
    def __init__(self, color, rank, pos, corp):
        self.color = color
        self.rank = rank
        self.pos = pos
        self.corp = corp
    
    def getColor(self):
        return self.color
    
    def getRank(self):
        return self.rank
    
    def getCorp(self):
        return self.corp
    
    def getPos(self):
        return self.pos
    
    def getTraits(self):
        return eval(f"{{ 'pos': '{self.pos}', 'color': '{self.color}', 'rank': '{self.rank}', 'corp': '{self.corp}' }}")
    
    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.getTraits() == other.getTraits()
        
    def __repr__(self):
        return f"{{ pos: {self.pos}, color: {self.color}, rank: {self.rank}, corp: {self.corp} }}"

class Boardstate:
    # Initializes an empty board and game in code (not gui)
    def __init__(self, boardstate: Dict[str, str], whiteMove: bool, corpList, readyToBlitz):
        # Game board from white's perspective
        # NOTE - I've seen this done with just strings, numbers, etc.
        # All are probably more efficient but a pain to read and work with
        
        self.board = boardstate # Board representation in Position Obj notation
        
        self.corpLists = corpList # Contains the current state of corps & available actions for each

        self.attackDict = {
            "K": {"K": 4, "Q": 4, "N": 4, "B": 4, "R": 5, "P": 1},
            "Q": {"K": 4, "Q": 4, "N": 4, "B": 4, "R": 5, "P": 2},
            "N": {"K": 4, "Q": 4, "N": 4, "B": 4, "R": 5, "P": 2},
            "B": {"K": 5, "Q": 5, "N": 5, "B": 4, "R": 5, "P": 3},
            "R": {"K": 4, "Q": 4, "N": 4, "B": 5, "R": 5, "P": 5},
            "P": {"K": 6, "Q": 6, "N": 6, "B": 5, "R": 5, "P": 4},
        }
        
        self.whiteMove = whiteMove  # Keeps track of whose turn it is
        self.kingDead = None # Initially no kings dead  
        self.readyToBlitz = readyToBlitz  # Stores the traits of knights ready to blitz
        self.gameHistory = []  # Keeps a history of the actions in a game.
        
    # Function that moves the pieces, adds it to the game history, and swaps players - IMPORTANT
    def processAction(self, parsedAction):
        if (parsedAction["actionType"] == "MOVEMENT"):
            # Local vars
            activePos = parsedAction["activePiece"]["pos"]
            activeColor = parsedAction["activePiece"]["color"]
            activeRank = parsedAction["activePiece"]["rank"]
            activeCorp = parsedAction["activePiece"]["corp"]
            targetPos = parsedAction["targetPiece"]["pos"]
            friendly = 'w' if self.whiteMove else 'b'
            
            try:
            # GetValidMoveset
                (in_range, setup, movement) = self.getValidMoveset(Piece(activeColor, activeRank, activePos, activeCorp))

                # processMovement
                if activePos in self.board: # Selected tile must contain a piece on the board
                    if targetPos in movement or targetPos in setup:  # If the square is in the piece's movement or setup set [empty targetPos]
                        # Move piece in engine local board b/c previously validated
                        curPiece = self.board.pop(activePos)
                        self.board[targetPos] = curPiece
                        
                        # Decrement command_authority_remaining, change corp data to reflect move
                        self.corpLists[friendly][activeCorp]["command_authority_remaining"] = self.corpLists[friendly][activeCorp]["command_authority_remaining"] - 1
                        if activeRank == "B" or activeRank == "K":
                            self.corpLists[friendly][activeCorp]["leader"]["pos"] = targetPos
                        else:
                            for piece in self.corpLists[friendly][activeCorp]["under_command"]:
                                if piece["pos"] == activePos:
                                    piece["pos"] = targetPos

                        if (activeRank == "N"): # Add knight to moved
                            self.readyToBlitz.append(targetPos)
                        
                        # Check for any remaining actions
                        turnend = True
                        for corp in self.corpLists[friendly]:
                            if self.corpLists[friendly][corp]["command_authority_remaining"] == 1:
                                turnend = False
                        
                        if turnend:
                            for corp in self.corpLists[friendly]:
                                self.corpLists[friendly][corp]["command_authority_remaining"] = 1
                            self.whiteMove = not self.whiteMove  # Swaps players.
                            self.readyToBlitz = []
                            
                        self.gameHistory.append(parsedAction)  # Adds the action to the game history
                        
                        return True, self.board, self.corpLists, self.whiteMove, self.readyToBlitz
                    else:
                        return False, None, None, None, None
                else:
                    return False, None, None, None, None
            except BaseException:
                tb = traceback.format_exc()
                print(tb)
                    
        elif (parsedAction["actionType"] == "ATTACK_ATTEMPT"):
            activePos = parsedAction["activePiece"]["pos"]
            activeColor = parsedAction["activePiece"]["color"]
            activeRank = parsedAction["activePiece"]["rank"]
            activeCorp = parsedAction["activePiece"]["corp"]
            targetPos = parsedAction["targetPiece"]["pos"]
            targetRank = parsedAction["targetPiece"]["rank"]
            targetCorp = parsedAction["targetPiece"]["corp"]
            friendly = 'w' if self.whiteMove else 'b'
            enemy = 'b' if self.whiteMove else 'w'
            
            try:
                (in_range, setup, movement) = self.getValidMoveset(Piece(activeColor, activeRank, activePos, activeCorp))
            
                if activePos in self.board: # Selected tile must contain a piece on the board
                    if targetPos in in_range:
                            # Roll for outcome of attack
                            if activeRank == "N" and targetPos in self.readyToBlitz: 
                                (outcome, roll_val) = self.attackResolver(activeRank, targetRank, True) # Blitz outcome
                                isBlitz = True
                            else:
                                (outcome, roll_val) = self.attackResolver(activeRank, targetRank, False) # Normal combat outcome
                                isBlitz = False
                            
                            # If an blitzing knight fails its attack, remove the ability to repeat the blitz
                            if not outcome and isBlitz and targetPos in self.readyToBlitz:
                                self.readyToBlitz.pop(targetPos)
                            
                            # Remove successfully attacked pieces from the boardstate
                            if outcome and activeRank != "R": # On successful capture
                                curPiece = self.board.pop(activePos)  # Sets the square that the piece is on to empty (the piece is "lifted" from the table)
                                self.board[targetPos] = curPiece  # "Places" the piece onto that square
                            elif outcome and activeRank == "R":
                                self.board.pop(targetPos)
                            
                            # Update corpList to reflect boardstate changes
                            # Remove successfully attacked pieces from the corpList & delegate under_command as needed
                            if outcome:
                                if activeRank in ["K", "B"]:
                                    self.corpLists[friendly][activeCorp]["leader"]["pos"] = targetPos
                                elif activeRank == "R":
                                    pass
                                else:
                                    for index, piece in enumerate(self.corpLists[friendly][activeCorp]["under_command"]):
                                        if piece == parsedAction["activePiece"]:
                                            self.corpLists[friendly][activeCorp]["under_command"][index]["pos"] = targetPos
                                
                                if targetRank == "K":
                                    self.corpLists[enemy].pop(targetCorp)
                                elif targetRank == "B":
                                    to_be_delegated = []
                                    for piece in self.corpLists[enemy][targetCorp]["under_command"]:
                                        piece["corp"] = "kingCorp"
                                        to_be_delegated.append(piece)
                                    self.corpLists[enemy].pop(targetCorp)
                                    self.corpLists[enemy]["kingCorp"]["under_command"] = self.corpLists[enemy]["kingCorp"]["under_command"] + to_be_delegated
                                else:
                                    for index, piece in enumerate(self.corpLists[enemy][targetCorp]["under_command"]):
                                        if piece == parsedAction["targetPiece"]:
                                            print("Removing successfully defeated piece pos from corpList")
                                            del self.corpLists[enemy][targetCorp]["under_command"][index]
                            
                            # Decrement command_authority_remaining
                            self.corpLists[friendly][activeCorp]["command_authority_remaining"] = self.corpLists[friendly][activeCorp]["command_authority_remaining"] - 1
                            
                            # Check for any remaining actions
                            turnend = True
                            for corp in self.corpLists[friendly]:
                                if self.corpLists[friendly][corp]["command_authority_remaining"] == 1:
                                    turnend = False
                            
                            # Process the end of a turn
                            if turnend:
                                for corp in self.corpLists[friendly]:
                                    self.corpLists[friendly][corp]["command_authority_remaining"] = 1
                                self.whiteMove = not self.whiteMove  # Swaps players.
                                self.readyToBlitz = []
                            
                            self.gameHistory.append(parsedAction)  # Adds the action to the game history
                            
                            # Endgame check
                            isEndGame = False
                            if (outcome and targetRank == "K" and "kingCorp" not in self.corpLists[enemy]): # Game over?
                                self.kingDead = activeColor # Set to proper color
                                isEndGame = True
                            
                            return True, outcome, self.board, roll_val, self.corpLists, self.whiteMove, isBlitz, self.readyToBlitz, isEndGame, self.kingDead
                    else:
                        return False, False, None, None, None, False, False, None, False, None
                else:
                    return False, False, None, None, None, False, False, None, False, None
            except BaseException:
                tb = traceback.format_exc()
                print(tb)
                    
        elif (parsedAction["actionType"] == "HIGHLIGHT"):
            activePos = parsedAction["activePiece"]["pos"]
            activeColor = parsedAction["activePiece"]["color"]
            activeRank = parsedAction["activePiece"]["rank"]
            activeCorp = parsedAction["activePiece"]["corp"]
            
            (in_range, setup, movement) = self.getValidMoveset(Piece(activeColor, activeRank, activePos, activeCorp))
            
            if activePos in self.board:
                return True, in_range, setup, movement
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
                return self.getValidKingMoveset(selected)
            case 'Q':
                return self.getValidQueenMoveset(selected)
            case 'N':
                return self.getValidKnightMoveset(selected)
            case _:
                return ([], [], [])
    
    # Pawns can only move forward, but they CAN move diagonally as well as attack diagonally, so long as it's toward enemy
    def getPawnValidMoveset(self, selected):
        selectedColor = selected.color
        selectedPos = selected.pos
        selectedCorp = selected.corp
        friendly = 'w' if self.whiteMove else 'b'
        
        in_range = []
        setup = []
        movement = []
        
        base_list = getAdjSquares(selectedPos, True) # Base surrounding adjacent squares for current pawn position
        
        if (selected.getTraits() in self.corpLists[friendly][selectedCorp]["under_command"]) and self.corpLists[friendly][selectedCorp]["command_authority_remaining"] == 1: # Confirm we've been passed a pawn in the correct corp & actions remain
            if (self.whiteMove and selectedColor == "w"): # Relative forward movement to white play
                for position in base_list:
                    if int(position[1]) > int(selectedPos[1]): # If space is relatively forward
                        if (not (position in self.board)): # If empty
                            movement.append(position)
                        elif (self.board.get(position)[0] == "b"): # If enemy
                            in_range.append(position)
            elif ((not self.whiteMove) and selectedColor == "b"): # Relative forward movement to black play
                for position in base_list:
                    if int(position[1]) < int(selectedPos[1]): # If space is relatively forward
                        if (not (position in self.board)): # If empty
                            movement.append(position)
                        elif (self.board.get(position)[0] == "w"): # If enemy
                            in_range.append(position)
        
        return (list(set(in_range)), list(set(setup)), list(set(movement)))
    
    def getBishopValidMoveset(self, selected):
        selectedPos = selected.getPos()
        selectedCorp = selected.getCorp()
        friendly = 'w' if self.whiteMove else 'b'
        enemy = 'b' if self.whiteMove else 'w'
        
        in_range = []
        setup = []
        movement = []
        
        base_list = getAdjSquares(selectedPos, True) # Base surrounding adjacent squares for current pawn position
        
        if (selected.getTraits() == self.corpLists[friendly][selectedCorp]["leader"]): # Confirm piece is a bishop & the leader of its corp
            if self.corpLists[friendly][selectedCorp]["command_authority_remaining"] == 1: # Attacks/Captures/Full Movement
                max_bishop_range = [
                    f"{selectedPos[0]}{chr(ord(selectedPos[1])+1)}",  f"{selectedPos[0]}{chr(ord(selectedPos[1])+2)}", # North Pos
                    f"{selectedPos[0]}{chr(ord(selectedPos[1])-1)}",  f"{selectedPos[0]}{chr(ord(selectedPos[1])-2)}", # South Pos
                    f"{chr(ord(selectedPos[0])+1)}{selectedPos[1]}",  f"{chr(ord(selectedPos[0])+2)}{selectedPos[1]}", # East Pos
                    f"{chr(ord(selectedPos[0])-1)}{selectedPos[1]}",  f"{chr(ord(selectedPos[0])-2)}{selectedPos[1]}", # West Pos
                    f"{chr(ord(selectedPos[0])+1)}{chr(ord(selectedPos[1])+1)}",  f"{chr(ord(selectedPos[0])+2)}{chr(ord(selectedPos[1])+2)}", # NE Pos
                    f"{chr(ord(selectedPos[0])-1)}{chr(ord(selectedPos[1])+1)}",  f"{chr(ord(selectedPos[0])-2)}{chr(ord(selectedPos[1])+2)}", # NW Pos
                    f"{chr(ord(selectedPos[0])+1)}{chr(ord(selectedPos[1])-1)}",  f"{chr(ord(selectedPos[0])+2)}{chr(ord(selectedPos[1])-2)}", # SE Pos
                    f"{chr(ord(selectedPos[0])-1)}{chr(ord(selectedPos[1])-1)}",  f"{chr(ord(selectedPos[0])-2)}{chr(ord(selectedPos[1])-2)}", # SW Pos
                ]
                cleaned_range = [pos for pos in max_bishop_range if isValidAlgeNotation(pos)]
                in_range = [pos for pos in cleaned_range if ((pos in base_list) and (str(self.board.get(pos))[0] == enemy))]
                cleaned_no_attackable_range = [pos for pos in cleaned_range if pos not in in_range]
                functional_range = [pos for pos in cleaned_no_attackable_range if not self.isLineBlocked(selectedPos, pos)]
                for pos in functional_range:
                    if pos not in self.board:
                        movement.append(pos)
                for pos in movement:
                    adj_to_move = getAdjSquares(pos, True)
                    enemies_adj_to_pos = [pos for pos in adj_to_move if str(self.board.get(pos))[0] == enemy]
                    if len(enemies_adj_to_pos) > 0:
                        setup.append(pos)
                movement = [pos for pos in movement if pos not in setup]
            elif self.corpLists[friendly][selectedCorp]["command_authority_remaining"] == 0: # Commander's Movement
                for pos in base_list:
                    if pos not in self.board:
                        movement.append(pos)

        return (list(set(in_range)), list(set(setup)), list(set(movement)))
    
    def getRookValidMoveset(self, selected):
        def getRookMoveRange(pos):
            max_rook_move_range =  [
                f"{pos[0]}{chr(ord(pos[1])+1)}", f"{pos[0]}{chr(ord(pos[1])+2)}", # North Pos
                f"{pos[0]}{chr(ord(pos[1])-1)}", f"{pos[0]}{chr(ord(pos[1])-2)}", # South Pos
                f"{chr(ord(pos[0])+1)}{pos[1]}", f"{chr(ord(pos[0])+2)}{pos[1]}", # East Pos
                f"{chr(ord(pos[0])-1)}{pos[1]}", f"{chr(ord(pos[0])-2)}{pos[1]}", # West Pos
                f"{chr(ord(pos[0])+1)}{chr(ord(pos[1])+1)}", f"{chr(ord(pos[0])+2)}{chr(ord(pos[1])+2)}", # NE Pos
                f"{chr(ord(pos[0])-1)}{chr(ord(pos[1])+1)}", f"{chr(ord(pos[0])-2)}{chr(ord(pos[1])+2)}", # NW Pos
                f"{chr(ord(pos[0])+1)}{chr(ord(pos[1])-1)}", f"{chr(ord(pos[0])+2)}{chr(ord(pos[1])-2)}", # SE Pos
                f"{chr(ord(pos[0])-1)}{chr(ord(pos[1])-1)}", f"{chr(ord(pos[0])-2)}{chr(ord(pos[1])-2)}", # SW Pos
            ]
            return [pos for pos in max_rook_move_range if isValidAlgeNotation(pos)]

        def getRookAttackRange(pos):
            max_rook_attack_range = [
                f"{pos[0]}{chr(ord(pos[1])+1)}", f"{pos[0]}{chr(ord(pos[1])+2)}", f"{pos[0]}{chr(ord(pos[1])+3)}", # North Pos
                f"{pos[0]}{chr(ord(pos[1])-1)}", f"{pos[0]}{chr(ord(pos[1])-2)}", f"{pos[0]}{chr(ord(pos[1])-3)}", # South Pos
                f"{chr(ord(pos[0])+1)}{pos[1]}", f"{chr(ord(pos[0])+2)}{pos[1]}", f"{chr(ord(pos[0])+3)}{pos[1]}", # East Pos
                f"{chr(ord(pos[0])-1)}{pos[1]}", f"{chr(ord(pos[0])-2)}{pos[1]}", f"{chr(ord(pos[0])-3)}{pos[1]}", # West Pos
                f"{chr(ord(pos[0])+1)}{chr(ord(pos[1])+1)}", f"{chr(ord(pos[0])+2)}{chr(ord(pos[1])+2)}", f"{chr(ord(pos[0])+3)}{chr(ord(pos[1])+3)}", # NE Pos
                f"{chr(ord(pos[0])+1)}{chr(ord(pos[1])+2)}", f"{chr(ord(pos[0])+1)}{chr(ord(pos[1])+3)}", f"{chr(ord(pos[0])+2)}{chr(ord(pos[1])+3)}", # NE Block Non-Linear Pos - North Half
                f"{chr(ord(pos[0])+2)}{chr(ord(pos[1])+1)}", f"{chr(ord(pos[0])+3)}{chr(ord(pos[1])+1)}", f"{chr(ord(pos[0])+3)}{chr(ord(pos[1])+2)}", # NE Block Non-Linear Pos - South Half
                f"{chr(ord(pos[0])-1)}{chr(ord(pos[1])+1)}", f"{chr(ord(pos[0])-2)}{chr(ord(pos[1])+2)}", f"{chr(ord(pos[0])-3)}{chr(ord(pos[1])+3)}", # NW Pos
                f"{chr(ord(pos[0])-1)}{chr(ord(pos[1])+2)}", f"{chr(ord(pos[0])-1)}{chr(ord(pos[1])+3)}", f"{chr(ord(pos[0])-2)}{chr(ord(pos[1])+3)}", # NW Block Non-Linear Pos - North Half
                f"{chr(ord(pos[0])-2)}{chr(ord(pos[1])+1)}", f"{chr(ord(pos[0])-3)}{chr(ord(pos[1])+1)}", f"{chr(ord(pos[0])-3)}{chr(ord(pos[1])+2)}", # NW Block Non-Linear Pos - South Half
                f"{chr(ord(pos[0])+1)}{chr(ord(pos[1])-1)}", f"{chr(ord(pos[0])+2)}{chr(ord(pos[1])-2)}", f"{chr(ord(pos[0])+3)}{chr(ord(pos[1])-3)}", # SE Pos
                f"{chr(ord(pos[0])+1)}{chr(ord(pos[1])-2)}", f"{chr(ord(pos[0])+1)}{chr(ord(pos[1])-3)}", f"{chr(ord(pos[0])+2)}{chr(ord(pos[1])-3)}", # SE Block Non-Linear Pos - North Half
                f"{chr(ord(pos[0])+2)}{chr(ord(pos[1])-1)}", f"{chr(ord(pos[0])+3)}{chr(ord(pos[1])-1)}", f"{chr(ord(pos[0])+3)}{chr(ord(pos[1])-2)}", # SE Block Non-Linear Pos - South Half
                f"{chr(ord(pos[0])-1)}{chr(ord(pos[1])-1)}", f"{chr(ord(pos[0])-2)}{chr(ord(pos[1])-2)}", f"{chr(ord(pos[0])-3)}{chr(ord(pos[1])-3)}", # SW Pos
                f"{chr(ord(pos[0])-1)}{chr(ord(pos[1])-2)}", f"{chr(ord(pos[0])-1)}{chr(ord(pos[1])-3)}", f"{chr(ord(pos[0])-2)}{chr(ord(pos[1])-3)}", # SW Block Non-Linear Pos - North Half
                f"{chr(ord(pos[0])-2)}{chr(ord(pos[1])-1)}", f"{chr(ord(pos[0])-3)}{chr(ord(pos[1])-1)}", f"{chr(ord(pos[0])-3)}{chr(ord(pos[1])-2)}", # SW Block Non-Linear Pos - South Half
            ]
            return [pos for pos in max_rook_attack_range if isValidAlgeNotation(pos)]
        
        selectedPos = selected.pos
        selectedCorp = selected.corp
        friendly = 'w' if self.whiteMove else 'b'
        enemy = 'b' if self.whiteMove else 'w'
        
        in_range = []
        setup = []
        movement = []
        
        if (selected.getTraits() in self.corpLists[friendly][selectedCorp]["under_command"]) and (self.corpLists[friendly][selectedCorp]["command_authority_remaining"] == 1):
            in_range = [pos for pos in getRookAttackRange(selectedPos) if str(self.board.get(pos))[0] == enemy]
            base_move_range = [pos for pos in getRookMoveRange(selectedPos) if pos not in self.board]
            movement = [pos for pos in base_move_range if not self.isLineBlocked(selectedPos, pos)]
            for pos in in_range:
                attackable_from = getRookAttackRange(pos)
                for pos in attackable_from:
                    if pos in movement:
                        setup.append(pos)
            movement = [pos for pos in movement if pos not in setup]

        return (list(set(in_range)), list(set(setup)), list(set(movement)))
    
    def getValidQueenMoveset(self, selected):
        selectedPos = selected.pos
        selectedCorp = selected.corp
        friendly = 'w' if self.whiteMove else 'b'
        enemy = 'b' if self.whiteMove else 'w'

        base_list = getAdjSquares(selectedPos, True)
        in_range = []
        setup = []
        movement = []

        if (selected.getTraits() in self.corpLists[friendly][selectedCorp]["under_command"]) and (self.corpLists[friendly][selectedCorp]["command_authority_remaining"] == 1):
            in_range = [pos for pos in base_list if str(self.board.get(pos))[0] == enemy]
            
            first_iter_moves = [pos for pos in base_list if pos not in self.board]
            movement = movement + first_iter_moves
            second_iter_moves = []
            for pos in first_iter_moves:
                sublist = getAdjSquares(pos, True)
                for pos in sublist:
                    if pos not in self.board:
                        second_iter_moves.append(pos)
            movement = movement + second_iter_moves
            third_iter_moves = []
            for pos in second_iter_moves:
                sublist = getAdjSquares(pos, True)
                for pos in sublist:
                    if pos not in self.board:
                        third_iter_moves.append(pos)
            movement = movement + third_iter_moves
            movement = list(set(movement))
            
            for pos in movement:
                adj_to_move = getAdjSquares(pos, True)
                enemies_adj_to_pos = [pos for pos in adj_to_move if str(self.board.get(pos))[0] == enemy]
                if len(enemies_adj_to_pos) > 0:
                    setup.append(pos)
            movement = [pos for pos in movement if pos not in setup]
        
        return (list(set(in_range)), list(set(setup)), list(set(movement)))
    
    def getValidKingMoveset(self, selected):
        selectedPos = selected.pos
        selectedCorp = selected.corp
        friendly = 'w' if self.whiteMove else 'b'
        enemy = 'b' if self.whiteMove else 'w'

        base_list = getAdjSquares(selectedPos, True)
        in_range = []
        setup = []
        movement = []
        
        print(selected.getTraits())
        if (selected.getTraits() == self.corpLists[friendly][selectedCorp]["leader"]): # Confirm piece is a bishop & the leader of its corp
            if self.corpLists[friendly][selectedCorp]["command_authority_remaining"] == 1: # Attacks/Captures/Full Movement
                in_range = [pos for pos in base_list if str(self.board.get(pos))[0] == enemy]
                
                first_iter_moves = [pos for pos in base_list if pos not in self.board]
                movement = movement + first_iter_moves
                second_iter_moves = []
                for pos in first_iter_moves:
                    sublist = getAdjSquares(pos, True)
                    for pos in sublist:
                        if pos not in self.board:
                            second_iter_moves.append(pos)
                movement = movement + second_iter_moves
                third_iter_moves = []
                for pos in second_iter_moves:
                    sublist = getAdjSquares(pos, True)
                    for pos in sublist:
                        if pos not in self.board:
                            third_iter_moves.append(pos)
                movement = list(set(third_iter_moves))
                movement = movement + third_iter_moves
                movement = list(set(movement))
                
                for pos in movement:
                    adj_to_move = getAdjSquares(pos, True)
                    enemies_adj_to_pos = [pos for pos in adj_to_move if str(self.board.get(pos))[0] == enemy]
                    if len(enemies_adj_to_pos) > 0:
                        setup.append(pos)
                movement = [pos for pos in movement if pos not in setup]
            elif self.corpLists[friendly][selectedCorp]["command_authority_remaining"] == 0: # Commander's Movement
                for pos in base_list:
                    if pos not in self.board:
                        movement.append(pos)
        
        return (list(set(in_range)), list(set(setup)), list(set(movement)))
    
    def getValidKnightMoveset(self, selected):
        selectedPos = selected.pos
        selectedCorp = selected.corp
        friendly = 'w' if self.whiteMove else 'b'
        enemy = 'b' if self.whiteMove else 'w'

        base_list = getAdjSquares(selectedPos, True)
        in_range = []
        setup = []
        movement = []
        
        if (selected.getTraits() in self.corpLists[friendly][selectedCorp]["under_command"]): # Confirm piece is a knight & under_command of its corp
            if self.corpLists[friendly][selectedCorp]["command_authority_remaining"] == 1: # Non-Blitz Attacks/Setup/Movement
                in_range = [pos for pos in base_list if str(self.board.get(pos))[0] == enemy]
                
                first_iter_moves = [pos for pos in base_list if pos not in self.board]
                movement = movement + first_iter_moves
                second_iter_moves = []
                for pos in first_iter_moves:
                    sublist = getAdjSquares(pos, True)
                    for pos in sublist:
                        if pos not in self.board:
                            second_iter_moves.append(pos)
                movement = movement + second_iter_moves
                third_iter_moves = []
                for pos in second_iter_moves:
                    sublist = getAdjSquares(pos, True)
                    for pos in sublist:
                        if pos not in self.board:
                            third_iter_moves.append(pos)
                movement = movement + third_iter_moves
                fourth_iter_moves = []
                for pos in third_iter_moves:
                    sublist = getAdjSquares(pos, True)
                    for pos in sublist:
                        if pos not in self.board:
                            fourth_iter_moves.append(pos)
                movement = movement + fourth_iter_moves
                movement = list(set(movement))
                
                for pos in movement:
                    adj_to_move = getAdjSquares(pos, True)
                    enemies_adj_to_pos = [pos for pos in adj_to_move if str(self.board.get(pos))[0] == enemy]
                    if len(enemies_adj_to_pos) > 0:
                        setup.append(pos)
                movement = [pos for pos in movement if pos not in setup]
            elif (self.corpLists[friendly][selectedCorp]["command_authority_remaining"] == 0) and (selected.pos in self.readyToBlitz): # Blitz Attacking
                in_range = [pos for pos in base_list if str(self.board.get(pos))[0] == enemy]
        
        return (list(set(in_range)), list(set(setup)), list(set(movement)))
    
    def isLineBlocked(self, selectedPos, targetPos):
        match getDirection(selectedPos, targetPos):
            case 1:  # Directly North
                for row in range(int(selectedPos[1]), int(targetPos[1]), 1):
                    current_pos = selectedPos[0] + str(row+1)
                    if current_pos in self.board:
                        return True

            case -1:  # Directly South
                for row in range(int(selectedPos[1]), int(targetPos[1]), -1):
                    current_pos = selectedPos[0] + str(row-1)
                    if current_pos in self.board:
                        return True

            case 10:  # Directly East
                norm_selectedPos = ord(selectedPos[0]) - ord("a")
                norm_targetPos = ord(targetPos[0]) - ord("a")
                for col in range(norm_selectedPos, norm_targetPos, 1):
                    current_pos = chr(col + 1 + ord("a")) + selectedPos[1]
                    if current_pos in self.board:
                        return True

            case -10:  # Directly West
                norm_selectedPos = ord(selectedPos[0]) - ord("a")
                norm_targetPos = ord(targetPos[0]) - ord("a")
                for col in range(norm_selectedPos, norm_targetPos, -1):
                    current_pos = chr(col - 1 + ord("a")) + selectedPos[1]
                    if current_pos in self.board:
                        return True

            case 11:  # North + East
                norm_selectedCol = ord(selectedPos[0]) - ord("a")
                diagDistance = int(targetPos[1]) - int(selectedPos[1])
                for current_offset in range(1, diagDistance):
                    current_pos = chr(norm_selectedCol + current_offset + ord("a")) + str(int(selectedPos[1]) + current_offset)
                    if current_pos in self.board:
                        return True

            case -9:  # North + West
                norm_selectedCol = ord(selectedPos[0]) - ord("a")
                diagDistance = int(targetPos[1]) - int(selectedPos[1])
                for current_offset in range(1, diagDistance):
                    current_pos = chr(norm_selectedCol - current_offset + ord("a")) + str(int(selectedPos[1]) + current_offset)
                    if current_pos in self.board:
                        return True

            case 9:  # South + East
                norm_selectedCol = ord(selectedPos[0]) - ord("a")
                diagDistance = int(selectedPos[1]) - int(targetPos[1])
                for current_offset in range(1, diagDistance):
                    current_pos = chr(norm_selectedCol + current_offset + ord("a")) + str(int(selectedPos[1]) - current_offset)
                    if current_pos in self.board:
                        return True

            case -11:  # South + West
                norm_selectedCol = ord(selectedPos[0]) - ord("a")
                diagDistance = int(selectedPos[1]) - int(targetPos[1])
                for current_offset in range(1, diagDistance):
                    current_pos = chr(norm_selectedCol - current_offset + ord("a")) + str(int(selectedPos[1]) - current_offset)
                    if current_pos in self.board:
                        return True

        return False

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
            adj = [f"{chr(col_int+1)}1", f"{chr(col_int-1)}1", f"{chr(col_int)}2"] if not diag else [f"{chr(col_int+1)}1", f"{chr(col_int-1)}1", f"{chr(col_int)}2", f"{chr(col_int+1)}2", f"{chr(col_int-1)}2"]
    
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

def newboard():
    return INITIAL_BOARDSTATE

def newcorplist():
    return INITIAL_CORP_LIST

def isValidAlgeNotation(potential_pos):
    alge_notation = re.compile(r"[a-h][1-8]")
    if alge_notation.match(potential_pos):
        return True
    else:
        return False