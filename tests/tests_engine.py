from django.test import SimpleTestCase, tag
from game.engine import *
import json, os, time

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

@tag('core', 'piece')
class PieceTestCase(SimpleTestCase):
    def testPiece(self):
        test_piece = Piece('w', 'K', 'a1', 'kingCorp')
        
        self.assertEqual(test_piece.color, 'w')
        self.assertEqual(test_piece.rank, 'K')
        self.assertEqual(test_piece.pos, 'a1')
        self.assertEqual(test_piece.corp, 'kingCorp')
        self.assertEqual(test_piece.getTraits(), "color:w,rank:K,corp:kingCorp,pos:a1")

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
    
    @tag('moveset', 'pawn')
    def testGetValidPawnMoveset(self):
        # Filedata import
        module_dir = os.path.dirname(__file__)
        boardstate_data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        corp_data_path = os.path.join(module_dir, 'mockups/example_corp_shape.json')
        boardstate_file = open(boardstate_data_path, 'r')
        corp_file = open(corp_data_path, 'r')
        
        boardstate_payload = json.load(boardstate_file)
        corp_payload = json.load(corp_file)
        test_cases = boardstate_payload["pawnTests"]
        for test in test_cases:
            match test["label"]:
                case "getPawnValidMoveset-WhiteFullBoard":
                    current = Boardstate(INITIAL_BOARDSTATE, True, corp_payload)
                    test_pawn = Piece(test["piece"]["color"], test["piece"]["rank"], test["piece"]["pos"], test["piece"]["corp"])
                    (test_in_range, test_setup, test_movement) = current.getValidMoveset(test_pawn)
                    self.assertEqual(test_in_range, [])
                    self.assertEqual(test_setup, [])
                    self.assertCountEqual(test_movement, ["c3", "d3", "e3"])
                
                # case "getPawnValidMoveset-BlackFullBoard":
                #     current = Boardstate(INITIAL_BOARDSTATE, False, corp_payload)
                #     test_pawn = Piece(test["piece"]["color"], test["piece"]["rank"], test["piece"]["pos"], test["piece"]["corp"])
                #     (test_in_range, test_setup, test_movement) = current.getValidMoveset(test_pawn)
                #     self.assertEqual(test_in_range, [])
                #     self.assertEqual(test_setup, [])
                #     self.assertCountEqual(test_movement, ["c6", "d6", "e6"])
        
        boardstate_file.close()
        corp_file.close()        
        
    @tag('moveset', 'bishop')
    def testGetValidBishopMoveset(self):
        # Filedata import
        module_dir = os.path.dirname(__file__)
        boardstate_data_path = os.path.join(module_dir, 'mockups/sample_boardstates.json')
        corp_data_path = os.path.join(module_dir, 'mockups/example_corp_shape.json')
        boardstate_file = open(boardstate_data_path, 'r')
        corp_file = open(corp_data_path, 'r')
        
        boardstate_payload = json.load(boardstate_file)
        corp_payload = json.load(corp_file)
        test_cases = boardstate_payload["bishopTests"]
        for test in test_cases:
            match test["label"]:
                case "getBishopValidMoveset-WhiteFullBoard":
                    current = Boardstate(INITIAL_BOARDSTATE, True, corp_payload)
                    test_bishop = Piece(test["piece"]["color"], test["piece"]["rank"], test["piece"]["pos"], test["piece"]["corp"])
                    (test_in_range, test_setup, test_movement) = current.getValidMoveset(test_bishop)
                    self.assertEqual(test_in_range, [])
                    self.assertEqual(test_setup, [])
                    self.assertCountEqual(test_movement, [])
                
                # case "getBishopValidMoveset-BlackFullBoard":
                #     current = Boardstate(INITIAL_BOARDSTATE, False, corp_payload)
                #     test_bishop = Piece(test["piece"]["color"], test["piece"]["rank"], test["piece"]["pos"], test["piece"]["corp"])
                #     (test_in_range, test_setup, test_movement) = current.getValidMoveset(test_bishop)
                #     self.assertEqual(test_in_range, [])
                #     self.assertEqual(test_setup, [])
                #     self.assertCountEqual(test_movement, [])
        
        boardstate_file.close()
        corp_file.close() 
    
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
    