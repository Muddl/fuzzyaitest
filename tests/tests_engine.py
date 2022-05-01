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
                # case "getBishopValidMoveset-WhiteFullBoard":
                #     current = Boardstate(INITIAL_BOARDSTATE, True, corp_payload)
                #     test_bishop = Piece(test["piece"]["color"], test["piece"]["rank"], test["piece"]["pos"], test["piece"]["corp"])
                #     (test_in_range, test_setup, test_movement) = current.getValidMoveset(test_bishop)
                #     self.assertEqual(test_in_range, [])
                #     self.assertEqual(test_setup, [])
                #     self.assertCountEqual(test_movement, [])
                
                case "getBishopValidMoveset-BlackFullBoard":
                    current = Boardstate(INITIAL_BOARDSTATE, False, corp_payload)
                    test_bishop = Piece(test["piece"]["color"], test["piece"]["rank"], test["piece"]["pos"], test["piece"]["corp"])
                    (test_in_range, test_setup, test_movement) = current.getValidMoveset(test_bishop)
                    self.assertEqual(test_in_range, [])
                    self.assertEqual(test_setup, [])
                    self.assertCountEqual(test_movement, [])
        
        boardstate_file.close()
        corp_file.close()