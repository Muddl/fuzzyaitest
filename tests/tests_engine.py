from django.test import SimpleTestCase, tag
from game.engine import *
import json, os

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

@tag('enum')
class ColorTestCase(SimpleTestCase):
    def testColorEnum(self):
        white = Color('w')
        black = Color('b')
        self.assertEqual(white, Color.WHITE)
        self.assertEqual(black, Color.BLACK)

@tag('enum')
class RankTestCase(SimpleTestCase):
    def testRankEnum(self):
        king = Rank('K')
        queen = Rank('Q')
        knight = Rank('N')
        rook = Rank('R')
        bishop = Rank('B')
        pawn = Rank('P')
        
        self.assertEqual(king, Rank.KING)
        self.assertEqual(queen, Rank.QUEEN)
        self.assertEqual(knight, Rank.KNIGHT)
        self.assertEqual(rook, Rank.ROOK)
        self.assertEqual(bishop, Rank.BISHOP)
        self.assertEqual(pawn, Rank.PAWN)

@tag('enum')
class WinFlagTestCase(SimpleTestCase):
    def testWinFlagEnum(self):
        none = WinFlag(0)
        white = WinFlag(1)
        black = WinFlag(2)
        
        self.assertEqual(none, WinFlag.NONE)
        self.assertEqual(white, WinFlag.WHITE)
        self.assertEqual(black, WinFlag.BLACK)
        
@tag('enum')
class ActionTypeTestCase(SimpleTestCase):
    def testActionTypeEnum(self):
        movement = ActionType('MOVEMENT')
        atk_attempt = ActionType('ATTACK_ATTEMPT')
        highlight = ActionType('HIGHLIGHT')
        
        self.assertEqual(movement, ActionType.MOVEMENT)
        self.assertEqual(atk_attempt, ActionType.ATTACK_ATTEMPT)
        self.assertEqual(highlight, ActionType.HIGHLIGHT)

@tag('core', 'piece')
class PieceTestCase(SimpleTestCase):
    def testPiece(self):
        test_piece = Piece(Color.WHITE, Rank.KING, 'a1')
        
        self.assertEqual(test_piece.color, Color.WHITE)
        self.assertEqual(test_piece.getColor(), 'w')
        self.assertEqual(test_piece.rank, Rank.KING)
        self.assertEqual(test_piece.getRank(), 'K')
        self.assertEqual(test_piece.pos, 'a1')
        self.assertEqual(test_piece.getPos(), 'a1')
        self.assertEqual(test_piece.getPair(), { test_piece.pos: (test_piece.color.value + test_piece.rank.value) })

@tag('core', 'action')
class ActionTestCase(SimpleTestCase):
    def testMovementActionInit(self):
        # TODO: This whole data path situation is a bit jank, holding until persisting actions to history in DB to use fixtures
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_requests.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test_action = Action(json.dumps(payload["test_movement"]))
            
            self.assertEqual(test_action.actionType, ActionType.MOVEMENT)
            self.assertEqual(test_action.activePiece, Piece(Color.WHITE, Rank.ROOK, 'a8'))
            self.assertEqual(test_action.targetPiece, Piece(Color.WHITE, Rank.ROOK, 'a7'))
    
    def testAttackAttemptActionInit(self):
        # TODO: This whole data path situation is a bit jank, holding until persisting actions to history in DB to use fixtures
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_requests.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test_action = Action(json.dumps(payload["test_attack"]))
            
            self.assertEqual(test_action.actionType, ActionType.ATTACK_ATTEMPT)
            self.assertEqual(test_action.activePiece, Piece(Color.WHITE, Rank.PAWN, 'a4'))
            self.assertEqual(test_action.targetPiece, Piece(Color.BLACK, Rank.PAWN, 'a5'))
    
    def testHightlightActionInit(self):
        # TODO: This whole data path situation is a bit jank, holding until persisting actions to history in DB to use fixtures
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_requests.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test_action = Action(json.dumps(payload["test_highlight"]))
            
            self.assertEqual(test_action.actionType, ActionType.HIGHLIGHT)
            self.assertEqual(test_action.activePiece, Piece(Color.BLACK, Rank.ROOK, 'a8'))
            
@tag('core', 'helpers')
class HelperTestCase(SimpleTestCase):
    @tag('getLine')
    def testGetLineFunc(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            test_cases = json.load(f)["getLineTests"]
            for test in test_cases:
                match test["label"]:
                    case "N":
                        self.assertCountEqual(getLine(test["boardstate"], [], test["selectedPos"], test["targetPos"]), ["d5"])
                    case "S":
                        self.assertCountEqual(getLine(test["boardstate"], [], test["selectedPos"], test["targetPos"]), ["d3"])
                    case "E":
                        self.assertCountEqual(getLine(test["boardstate"], [], test["selectedPos"], test["targetPos"]), ["e4"])
                    case "W":
                        self.assertCountEqual(getLine(test["boardstate"], [], test["selectedPos"], test["targetPos"]), ["c4"])
    
    @tag('getDirection')
    def testGetDirectionFunc(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            test_cases = json.load(f)["getDirectionTests"]
            for test in test_cases:
                match test["label"]:
                    case "N":
                        self.assertEqual(getDirection(test["startPos"], test["endPos"]), 1)
                    case "S":
                        self.assertEqual(getDirection(test["startPos"], test["endPos"]), -1)
                    case "E":
                        self.assertEqual(getDirection(test["startPos"], test["endPos"]), 10)
                    case "W":
                        self.assertEqual(getDirection(test["startPos"], test["endPos"]), -10)
                    case "NE":
                        self.assertEqual(getDirection(test["startPos"], test["endPos"]), 11)
                    case "NW":
                        self.assertEqual(getDirection(test["startPos"], test["endPos"]), -9)
                    case "SE":
                        self.assertEqual(getDirection(test["startPos"], test["endPos"]), 9)
                    case "SW":
                        self.assertEqual(getDirection(test["startPos"], test["endPos"]), -11)

@tag('core', 'boardstate')
class BoardstateTestCase(SimpleTestCase):
    @tag('processAction', 'MOVEMENT')
    def testMovementProcessAction(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)["pawnTests"][0]
            board = Boardstate(payload["boardstate"], True, 0)
            output_bool, output_dict, output_actionCounter, output_whiteMove = board.processAction(payload["action"])
            self.assertEqual(output_bool, True)
            self.assertDictContainsSubset(dict(d5='wP'), output_dict)
            self.assertEqual(output_actionCounter, 1)
            self.assertEqual(output_whiteMove, True)
            
    @tag('processAction', 'ATTACK_ATTEMPT', 'pawn')
    def testPawnAttackAttemptProcessAction(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test = payload["pawnTests"][1]
            test_action = test["action"]
            test_boardstate = json.dumps(payload["pawnTests"][1]["boardstate"])
            board = Boardstate(eval(test_boardstate), True, 0)
            output_isValid, output_isSuccessful, output_new_boardstate, output_roll_val, output_actionCounter, output_whiteMove = board.processAction(test_action)
            self.assertEqual(output_isValid, True)
            self.assertIsInstance(output_isSuccessful, bool)
            if (output_isSuccessful):
                self.assertDictContainsSubset(dict(d5='wP'), output_new_boardstate)
            else:
                self.assertIsInstance(output_new_boardstate, dict)
            self.assertIn(output_roll_val, range(1, 7))
            self.assertEqual(output_actionCounter, 1)
            self.assertEqual(output_whiteMove, True)
    
    @tag('processAction', 'ATTACK_ATTEMPT', 'bishop')
    def testBishopAttackAttemptProcessAction(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test = payload["bishopTests"][1]
            test_action = test["action"]
            test_boardstate = json.dumps(payload["bishopTests"][1]["boardstate"])
            board = Boardstate(eval(test_boardstate), True, 0)
            output_isValid, output_isSuccessful, output_new_boardstate, output_roll_val, output_actionCounter, output_whiteMove = board.processAction(test_action)
            self.assertEqual(output_isValid, True)
            self.assertIsInstance(output_isSuccessful, bool)
            if (output_isSuccessful):
                self.assertDictContainsSubset(dict(d6='wB'), output_new_boardstate)
            else:
                self.assertIsInstance(output_new_boardstate, dict)
            self.assertIn(output_roll_val, range(1, 7))
            self.assertEqual(output_actionCounter, 1)
            self.assertEqual(output_whiteMove, True)
    
    @tag('processAction', 'ATTACK_ATTEMPT', 'rook')
    def testRookAttackAttemptProcessAction(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test = payload["rookTests"][1]
            test_action = test["action"]
            test_boardstate = json.dumps(payload["rookTests"][1]["boardstate"])
            board = Boardstate(eval(test_boardstate), True, 0)
            output_isValid, output_isSuccessful, output_new_boardstate, output_roll_val, output_actionCounter, output_whiteMove = board.processAction(test_action)
            self.assertEqual(output_isValid, True)
            self.assertIsInstance(output_isSuccessful, bool)
            if (output_isSuccessful):
                self.assertDictContainsSubset(dict(d4='wR', d5="wP"), output_new_boardstate)
            else:
                self.assertIsInstance(output_new_boardstate, dict)
            self.assertIn(output_roll_val, range(1, 7))
            self.assertEqual(output_actionCounter, 1)
            self.assertEqual(output_whiteMove, True)
            
    @tag('processAction', 'ATTACK_ATTEMPT', 'king')
    def testKingAttackAttemptProcessAction(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test = payload["royalTests"][2]
            test_action = test["action"]
            test_boardstate = json.dumps(payload["royalTests"][2]["boardstate"])
            board = Boardstate(eval(test_boardstate), True, 0)
            output_isValid, output_isSuccessful, output_new_boardstate, output_roll_val, output_actionCounter, output_whiteMove = board.processAction(test_action)
            self.assertEqual(output_isValid, True)
            self.assertIsInstance(output_isSuccessful, bool)
            if (output_isSuccessful):
                self.assertDictContainsSubset(dict(d5='wK'), output_new_boardstate)
            else:
                self.assertIsInstance(output_new_boardstate, dict)
            self.assertIn(output_roll_val, range(1, 7))
            self.assertEqual(output_actionCounter, 1)
            self.assertEqual(output_whiteMove, True)
    
    @tag('processAction', 'ATTACK_ATTEMPT', 'queen')
    def testQueenAttackAttemptProcessAction(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test = payload["royalTests"][3]
            test_action = test["action"]
            test_boardstate = json.dumps(payload["royalTests"][3]["boardstate"])
            board = Boardstate(eval(test_boardstate), True, 0)
            output_isValid, output_isSuccessful, output_new_boardstate, output_roll_val, output_actionCounter, output_whiteMove = board.processAction(test_action)
            self.assertEqual(output_isValid, True)
            self.assertIsInstance(output_isSuccessful, bool)
            if (output_isSuccessful):
                self.assertDictContainsSubset(dict(d5='wQ'), output_new_boardstate)
            else:
                self.assertIsInstance(output_new_boardstate, dict)
            self.assertIn(output_roll_val, range(1, 7))
            self.assertEqual(output_actionCounter, 1)
            self.assertEqual(output_whiteMove, True)
            
    @tag('processAction', 'ATTACK_ATTEMPT', 'knight')
    def testKnightAttackAttemptNoBlitzProcessAction(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test = payload["knightTests"][1]
            test_action = test["action"]
            test_boardstate = json.dumps(payload["knightTests"][1]["boardstate"])
            board = Boardstate(eval(test_boardstate), True, 0)
            output_isValid, output_isSuccessful, output_new_boardstate, output_roll_val, output_actionCounter, output_whiteMove = board.processAction(test_action)
            self.assertEqual(output_isValid, True)
            self.assertIsInstance(output_isSuccessful, bool)
            if (output_isSuccessful):
                self.assertDictContainsSubset(dict(d5='wN'), output_new_boardstate)
            else:
                self.assertIsInstance(output_new_boardstate, dict)
            self.assertIn(output_roll_val, range(1, 7))
            self.assertEqual(output_actionCounter, 1)
            self.assertEqual(output_whiteMove, True)
    
    @tag('processAction', 'ATTACK_ATTEMPT', 'knight')
    def testKnightAttackAttemptBlitzProcessAction(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test = payload["knightTests"][2]
            test_action = test["action"]
            test_boardstate = json.dumps(payload["knightTests"][2]["boardstate"])
            board = Boardstate(eval(test_boardstate), True, 0)
            board.blitzableKnightSquares = ["d5"] # IMPORTANT FOR BLITZING, falsify boardstate metadata
            output_isValid, output_isSuccessful, output_new_boardstate, output_roll_val, output_actionCounter, output_whiteMove, output_blitz = board.processAction(test_action)
            self.assertEqual(output_isValid, True)
            self.assertIsInstance(output_isSuccessful, bool)
            if (output_isSuccessful):
                self.assertDictContainsSubset(dict(d5='wN'), output_new_boardstate)
            else:
                self.assertIsInstance(output_new_boardstate, dict)
            self.assertIn(output_roll_val, range(1, 7))
            self.assertEqual(output_actionCounter, 1)
            self.assertEqual(output_whiteMove, True)
            self.assertEqual(output_blitz, True)
            self.assertEqual(board.blitzableKnightSquares, [])
            self.assertEqual(board.knightsAttacked, "d5")
        
    @tag('processAction', 'HIGHLIGHT')
    def testHighlightProcessAction(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_requests.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)["test_highlight"]
            board = Boardstate(newboard(), True, 0)
            self.assertEqual(board.processAction(payload)[0],True)
            self.assertCountEqual(board.processAction(payload)[1],['b3', 'c3', 'd3'])
    
    @tag('moveset', 'pawn')
    def testGetValidPawnMoveset(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test_cases = payload["pawnTests"]
            for test in test_cases:
                match test["label"]:
                    case "pawnMovement":
                        current = Boardstate(test["boardstate"], True, 0)
                        selectedPiece = Piece(test["action"]["activePiece"]["color"], test["action"]["activePiece"]["rank"], test["action"]["activePiece"]["pos"])
                        (empt_space, enem_space) = current.getValidMoveset(selectedPiece)
                        self.assertCountEqual(empt_space, ["c5", "d5", "e5"])
                        self.assertEqual(enem_space, [])
                    case "pawnAttack":
                        current = Boardstate(test["boardstate"], True, 0)
                        selectedPiece = Piece(test["action"]["activePiece"]["color"], test["action"]["activePiece"]["rank"], test["action"]["activePiece"]["pos"])
                        (empt_space, enem_space) = current.getValidMoveset(selectedPiece)
                        self.assertCountEqual(empt_space, ["c5", "e5"])
                        self.assertCountEqual(enem_space, ["d5"])
                    case "pawnAttackFromSide":
                        current = Boardstate(test["boardstate"], True, 0)
                        selectedPiece = Piece(test["action"]["activePiece"]["color"], test["action"]["activePiece"]["rank"], test["action"]["activePiece"]["pos"])
                        (empt_space, enem_space) = current.getValidMoveset(selectedPiece)
                        self.assertCountEqual(empt_space, ["b5"])
                        self.assertCountEqual(enem_space, ["a5"])
                    case "pawnAttackFromCorner":
                        current = Boardstate(test["boardstate"], True, 0)
                        selectedPiece = Piece(test["action"]["activePiece"]["color"], test["action"]["activePiece"]["rank"], test["action"]["activePiece"]["pos"])
                        (empt_space, enem_space) = current.getValidMoveset(selectedPiece)
                        self.assertCountEqual(empt_space, ["b2"])
                        self.assertCountEqual(enem_space, ["a2"])
        
    @tag('moveset', 'bishop')
    def testGetValidBishopMoveset(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test = payload["bishopTests"][0]
            current = Boardstate(eval(str(test["boardstate"])), True, 0)
            selectedPiece = Piece(test["action"]["activePiece"]["color"], test["action"]["activePiece"]["rank"], test["action"]["activePiece"]["pos"])
            (empt_space, enem_space) = current.getValidMoveset(selectedPiece)
            self.assertCountEqual(empt_space, ["b2", "b3", "b4", "b5", "b6", "c2", "c3", "c4", "c5", "c6", "d2", "d3", "d5", "d6", "e2", "e3", "e4", "e5", "e6", "f2", "f3", "f4", "f5", "f6"])
            self.assertEqual(enem_space, [])
    
    @tag('moveset', 'rook')
    def testGetValidRookMoveset(self):
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test = payload["rookTests"][0]
            current = Boardstate(eval(str(test["boardstate"])), True, 0)
            selectedPiece = Piece(test["action"]["activePiece"]["color"], test["action"]["activePiece"]["rank"], test["action"]["activePiece"]["pos"])
            (empt_space, enem_space) = current.getValidMoveset(selectedPiece)
            self.assertCountEqual(empt_space, ["b2", "b3", "b4", "b5", "b6", "c2", "c3", "c4", "c5", "c6", "d2", "d3", "d5", "d6", "e2", "e3", "e4", "e5", "e6", "f2", "f3", "f4", "f5", "f6"])
            self.assertEqual(enem_space, [])
    
    @tag('moveset', 'royal')
    def testGetValidRoyalMoveset(self):
        self.maxDiff = None # For long dict comparison printouts
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test_cases = payload["royalTests"]
            for test in test_cases:
                match test["label"]:
                    case "kingMovementNoEnem":
                        current = Boardstate(eval(str(test["boardstate"])), True, 0)
                        selectedPiece = Piece(test["action"]["activePiece"]["color"], test["action"]["activePiece"]["rank"], test["action"]["activePiece"]["pos"])
                        (empt_space, enem_space) = current.getValidMoveset(selectedPiece)
                        self.assertCountEqual(empt_space, ["a1", "a2", "a3", "a4", "a5", "a6", "a7", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "d1", "d2", "d3", "d5", "d6", "d7", "e1", "e2", "e3", "e4", "e5", "e6", "e7", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "g1", "g2", "g3", "g4", "g5", "g6", "g7"])
                        self.assertEqual(enem_space, [])
                    case "queenMovementNoEnem":
                        current = Boardstate(eval(str(test["boardstate"])), True, 0)
                        selectedPiece = Piece(test["action"]["activePiece"]["color"], test["action"]["activePiece"]["rank"], test["action"]["activePiece"]["pos"])
                        (empt_space, enem_space) = current.getValidMoveset(selectedPiece)
                        self.assertCountEqual(empt_space, ["a1", "a2", "a3", "a4", "a5", "a6", "a7", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "d1", "d2", "d3", "d5", "d6", "d7", "e1", "e2", "e3", "e4", "e5", "e6", "e7", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "g1", "g2", "g3", "g4", "g5", "g6", "g7"])
                        self.assertEqual(enem_space, [])

    @tag('moveset', 'knight')
    def testGetValidRoyalMoveset(self):
        self.maxDiff = None # For long dict comparison printouts
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        with open(data_path, 'r') as f:
            payload = json.load(f)
            test_cases = payload["knightTests"]
            for test in test_cases:
                match test["label"]:
                    case "knightMovementNoEnem":
                        current = Boardstate(eval(str(test["boardstate"])), True, 0)
                        selectedPiece = Piece(test["action"]["activePiece"]["color"], test["action"]["activePiece"]["rank"], test["action"]["activePiece"]["pos"])
                        (empt_space, enem_space) = current.getValidMoveset(selectedPiece)
                        self.assertCountEqual(empt_space, ["a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "d1", "d2", "d3", "d5", "d6", "d7", "d8", "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8"])
                        self.assertEqual(enem_space, [])
    