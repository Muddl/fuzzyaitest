from engine import *
import pandas as pd
import warnings
import string
import math
import numpy as np
import random
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'
pd.set_option('display.width', 2000)
pd.set_option('display.max_rows', None)

risk_threshold = 0.1
color_cpu = 'b'
color_user = 'w'
initial_piece_reference = []

list_of_turns = range(1, 4)
list_of_colors = ['w', 'b']
list_of_letters = string.ascii_lowercase
list_of_corps = [
    ["a8", 2],
    ["b8", 1],
    ["c8", 1],
    ["d8", 2],
    ["e8", 2],
    ["f8", 3],
    ["g8", 3],
    ["h8", 2],
    ["a7", 1],
    ["b7", 1],
    ["c7", 1],
    ["d7", 2],
    ["e7", 2],
    ["f7", 3],
    ["g7", 3],
    ["h7", 3],
    ["a2", 1],
    ["b2", 1],
    ["c2", 1],
    ["d2", 2],
    ["e2", 2],
    ["f2", 3],
    ["g2", 3],
    ["h2", 3],
    ["a1", 2],
    ["b1", 1],
    ["c1", 1],
    ["d1", 2],
    ["e1", 2],
    ["f1", 3],
    ["g1", 3],
    ["h1", 3]
]

# [piece, [space range], omni-directional]
list_of_possibilities = [
    {'piece': 'k', 'spaces': [-3, 3], 'omniDirectional': 1},
    {'piece': 'q', 'spaces': [-3, 3], 'omniDirectional': 1},
    {'piece': 'n', 'spaces': [-4, 4], 'omniDirectional': 1},
    {'piece': 'b', 'spaces': [-2, 2], 'omniDirectional': 1},
    {'piece': 'r', 'spaces': [-2, 2], 'omniDirectional': 1},
    {'piece': 'p', 'spaces': [-1, 1], 'omniDirectional': 0},
]

# [attacking piece, defending piece, probability of capture]
list_of_probabilities = [
    ['k', 'k', 1.5],
    ['k', 'q', 0.5],
    ['k', 'n', 0.5],
    ['k', 'b', 0.5],
    ['k', 'r', 0.33],
    ['k', 'p', 1],

    ['q', 'k', 1.5],
    ['q', 'q', 0.5],
    ['q', 'n', 0.5],
    ['q', 'b', 0.5],
    ['q', 'r', 0.33],
    ['q', 'p', 0.83],

    ['n', 'k', 1.33],
    ['n', 'q', 0.33],
    ['n', 'n', 0.33],
    ['n', 'b', 0.33],
    ['n', 'r', 0.33],
    ['n', 'p', 0.83],

    ['b', 'k', 1.33],
    ['b', 'q', 0.33],
    ['b', 'n', 0.33],
    ['b', 'b', 0.5],
    ['b', 'r', 0.33],
    ['b', 'p', 0.66],

    ['r', 'k', 1.5],
    ['r', 'q', 0.5],
    ['r', 'n', 0.5],
    ['r', 'b', 0.33],
    ['r', 'r', 0.33],
    ['r', 'p', 0.33],

    ['p', 'k', 1.167],
    ['p', 'q', 0.167],
    ['p', 'n', 0.167],
    ['p', 'b', 0.33],
    ['p', 'r', 0.167],
    ['p', 'p', 0.5],
]
df_possibilities = pd.DataFrame(list_of_possibilities)

current_turn_color = list_of_colors[0]
current_turn_iteration = list_of_turns[0]

# initial board state dimension
dict_initial_board_state = {'a8': 'bR', 'b8': 'bN', 'c8': 'bB', 'd8': 'bQ', 'e8': 'bK', 'f8': 'bB', 'g8': 'bN',
                            'h8': 'bR', 'a7': 'bP',  'c7': 'bP', 'd7': 'bP', 'e7': 'bP', 'f7': 'bP',
                            'g7': 'bP', 'h7': 'bP', 'a2': 'wP', 'b2': 'wP', 'c2': 'wP', 'd2': 'wP', 'e2': 'wP',
                            'f2': 'wP', 'g2': 'wP', 'h2': 'wP', 'a1': 'wR', 'b1': 'wN', 'c1': 'wB', 'd1': 'wQ',
                            'e1': 'wK', 'f1': 'wB', 'g1': 'wN', 'h1': 'wR'}

#b7: bp

dict_test_board_state_1 = {
    "a8": "bR",
    "b8": "bN",
    "d8": "bQ",
    "e8": "bK",
    "f8": "bB",
    "a7": "bP",
    "f7": "bP",
    "h7": "bP",
    "a2": "wP",
    "d2": "wP",
    "h2": "wP",
    "a1": "wR",
    "c1": "wB",
    "d1": "wQ",
    "f1": "wB",
    "f5": "wP",
    "c4": "bP",
    "b6": "bP",
    "e5": "bB",
    "h3": "wN",
    "h5": "wR",
    "a5": "wP",
    "f6": "bN",
    "g3": "bR",
    "c6": "wK",
    "e3": "bP",
    "d6": "bP",
    "b1": "bP",
    "b7": "wP",
    "g7": "wP",
    "c8": "wP",
    "g6": "wN"
}

dict_test_board_state_2 = {
    "e8": "bK",
    "a7": "bP",
    "b7": "bP",
    "f7": "bP",
    "h7": "bP",
    "a2": "wP",
    "b2": "wP",
    "c2": "wP",
    "h2": "wP",
    "e1": "wK",
    "f1": "wB",
    "h1": "wR",
    "c4": "wP",
    "e4": "wP",
    "f4": "wP",
    "d3": "wQ",
    "g3": "wP",
    "f3": "wN",
    "c3": "wB",
    "a3": "wN",
    "e2": "wR",
    "e6": "bP",
    "d6": "bP",
    "c5": "bP",
    "f6": "bP",
    "g5": "bN",
    "g7": "bR",
    "c6": "bB",
    "a6": "bN",
    "f5": "bQ",
    "d7": "bB",
    "b8": "bR"
}

dict_test_board_state_3 = {
    "a8": "bR",
    "b8": "bN",
    "c8": "bB",
    "d8": "bQ",
    "e8": "bK",
    "f8": "bB",
    "g8": "bN",
    "h8": "bR",
    "a7": "bP",
    "b7": "bP",
    "c7": "bP",
    "d7": "bP",
    "e7": "bP",
    "f7": "bP",
    "g7": "bP",
    "h7": "bP",
    "b2": "wP",
    "c2": "wP",
    "e2": "wP",
    "f2": "wP",
    "g2": "wP",
    "h2": "wP",
    "a1": "wR",
    "b1": "wN",
    "c1": "wB",
    "d1": "wQ",
    "e1": "wK",
    "f1": "wB",
    "g1": "wN",
    "h1": "wR",
    "a2": "wP",
    "d6": "wP"
}

dict_test_board_state_4 = {
    "a8": "bR",
    "b8": "bN",
    "c8": "bB",
    "d8": "bQ",
    "e8": "bK",
    "f8": "bB",
    "g8": "bN",
    "h8": "bR",
    "a7": "bP",
    "b7": "bP",
    "d7": "bP",
    "e7": "bP",
    "f7": "bP",
    "g7": "bP",
    "b2": "wP",
    "c2": "wP",
    "e2": "wP",
    "f2": "wP",
    "g2": "wP",
    "h2": "wP",
    "a1": "wR",
    "b1": "wN",
    "c1": "wB",
    "d1": "wQ",
    "e1": "wK",
    "f1": "wB",
    "g1": "wN",
    "h1": "wR",
    "a2": "wP",
    "d2": "wP",
    "h7": "bP",
    "c6": "bP"
}

dict_test_pawn_board_state = {
    "g7": "bP",
    "f2": "wP",
    "h2": "wP",
    "a2": "wP",
    "d4": "bP",
    "e4": "wP",
    "b4": "wP",
    "c3": "wP",
    "g4": "wP",
    "d6": "bP",
    "a7": "bP",
    "b6": "bP",
    "c5": "bP",
    "f6": "bP",
    "h6": "bP"
}



INITIAL_CORP_LIST_AI = {
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
            "command_authority_remaining": 0
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
                    "pos": "", #HERE B7
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "leftBishopCorp"
                },
                {
                    "pos": "c6",
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

PAWN_CORP_LIST_AI = {
    "w": {
        "kingCorp": {
            "leader": {
                "pos": "",
                "color" : "w",
                "rank" : "K",
                "corp" : "kingCorp"
            },
            "under_command": [
                {
                    "pos": "",
                    "color" : "w",
                    "rank" : "R",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "",
                    "color" : "w",
                    "rank" : "R",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "",
                    "color" : "w",
                    "rank" : "Q",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "", 
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "e4",
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "kingCorp"
                }
            ],
            "command_authority_remaining": 1
        },
        "leftBishopCorp": {
            "leader": {
                "pos": "",
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
                    "pos": "",
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "leftBishopCorp"
                },
                {
                    "pos": "c3",
                    "color" : "w",
                    "rank" : "P",
                    "corp" : "leftBishopCorp"
                },
                {
                    "pos": "",
                    "color" : "w",
                    "rank" : "N",
                    "corp" : "leftBishopCorp"
                }
            ],
            "command_authority_remaining": 1
        },
        "rightBishopCorp": {
            "leader": {
                "pos": "",
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
                    "pos": "g4",
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
                    "pos": "",
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
                "pos": "",
                "color" : "b",
                "rank" : "K",
                "corp" : "kingCorp"
            },
            "under_command": [
                {
                    "pos": "",
                    "color" : "b",
                    "rank" : "R",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "",
                    "color" : "b",
                    "rank" : "R",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "",
                    "color" : "b",
                    "rank" : "Q",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "d6",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "kingCorp"
                },
                {
                    "pos": "e5",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "kingCorp"
                }
            ],
            "command_authority_remaining": 1
        },
        "leftBishopCorp": {
            "leader": {
                "pos": "",
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
                    "pos": "b6",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "leftBishopCorp"
                },
                {
                    "pos": "b4",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "leftBishopCorp"
                },
                {
                    "pos": "",
                    "color" : "b",
                    "rank" : "N",
                    "corp" : "leftBishopCorp"
                }
            ],
            "command_authority_remaining": 0
        },
        "rightBishopCorp": {
            "leader": {
                "pos": "",
                "color" : "b",
                "rank" : "B",
                "corp" : "rightBishopCorp"
            },
            "under_command": [
                {
                    "pos": "f6",
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
                    "pos": "h6",
                    "color" : "b",
                    "rank" : "P",
                    "corp" : "rightBishopCorp"
                },
                {
                    "pos": "",
                    "color" : "b",
                    "rank" : "N",
                    "corp" : "rightBishopCorp"
                }
            ],
            "command_authority_remaining": 0
        }
    }
}


def get_black_squares_available(json_dictionary):


    black_corps = list(json_dictionary['b'].keys())
    

    black_list_of_squares_available = []

    for corp in black_corps:
        if json_dictionary['b'][corp]['command_authority_remaining'] == 1:
            corps_available = json_dictionary['b'][corp]
            leader_in_corp = list(corps_available.keys())[:1]
            under_command_in_corp = list(corps_available.keys())[1:2]
            for piece in leader_in_corp:
                black_list_of_squares_available.append(corps_available[piece]['pos'])
            for piece in under_command_in_corp:
                under_command_list = corps_available[piece]
            for piece in under_command_list:
                black_list_of_squares_available.append(piece['pos'])

    black_res = []
    [black_res.append(x) for x in black_list_of_squares_available if x not in black_res]

    return black_res

def get_white_squares_available(json_dictionary):
    white_corps = list(json_dictionary['w'].keys())
    white_list_of_squares_available = []

    for corp in white_corps:
        if json_dictionary['w'][corp]['command_authority_remaining'] == 1:
            corps_available = json_dictionary['w'][corp]
            leader_in_corp = list(corps_available.keys())[:1]
            under_command_in_corp = list(corps_available.keys())[1:2]
            for piece in leader_in_corp:
                white_list_of_squares_available.append(corps_available[piece]['pos'])
            for piece in under_command_in_corp:
                under_command_list = corps_available[piece]
            for piece in under_command_list:
                white_list_of_squares_available.append(piece['pos'])

    white_res = []
    [white_res.append(x) for x in white_list_of_squares_available if x not in white_res]

    return white_res

def get_black_corp(position, json_dictionary):


    black_corps = list(json_dictionary['b'].keys())



    corp_string = ''
    for corp in black_corps:
        corps_available = json_dictionary['b'][corp]
        leader_in_corp = list(corps_available.keys())[:1]
        under_command_in_corp = list(corps_available.keys())[1:2]
        for pieces in leader_in_corp:
            if corps_available[pieces]['pos'] == position:
                corp_string = corps_available[pieces]['corp']
        for pieces in under_command_in_corp:
            under_command_list = corps_available[pieces]
            for dictionary in under_command_list:
                if dictionary['pos'] == position:
                    corp_string = dictionary['corp']
    return corp_string
    
    

def get_white_corp(position, json_dictionary):

    white_corps = list(json_dictionary['w'].keys())

    corp_string = ''
    for corp in white_corps:
        corps_available = json_dictionary['w'][corp]
        leader_in_corp = list(corps_available.keys())[:1]
        under_command_in_corp = list(corps_available.keys())[1:2]
        for piece in leader_in_corp:
            if corps_available[piece]['pos'] == position:
                corp_string = corps_available[piece]['corp']
        for piece in under_command_in_corp:
            under_command_list = corps_available[piece]
            for dictionary in under_command_list:
                if dictionary['pos'] == position:
                    corp_string = dictionary['corp']
    return corp_string

def get_board_notation(coordinates):
    return str(
        list_of_letters[coordinates[0]-1]) + str(coordinates[1])


def get_board_coordinates(board_notation):
    return [list_of_letters.index(board_notation[0]) + 1, int(board_notation[1])]


def get_list_of_spaces(board_state):
    # return lists of both friendly and enemy positions
    friendly_list = []
    enemy_list = []
    for (key, value) in board_state.items():
        if value[0] == color_cpu:
            friendly_list += [key]
        elif value[0] == color_user:
            enemy_list += [key]
    return friendly_list, enemy_list


def get_list_of_initial_corps_assignments(board_state):
    _corps_list = []
    for key in board_state:
        # _corps = [corp[1] for corp in list_of_corps if key == corp[0]][0]
        _corps = random.randint(1, 3)
        _corps_list += [[key, _corps]]
    return _corps_list


def get_capture_probability(attacker, defender):
    # find corresponding attacker/defender key(s) and return probability of capture
    score = [entry[2] for entry in list_of_probabilities if entry[0]
             == attacker and entry[1] == defender]
    if len(score) == 0:
        # if there are no potential attacks, return 0
        return 0
    else:
        return score[0]


def generate_new_board_state(board_state_df):
    _d = {}
    for entry in board_state_df[['starting_position', 'piece']].values:
        _d[entry[0]] = entry[1]
    return _d


def get_movesets_per_board_state(board_state):
    # take in boardset and explode the moveset results (creating one move per row instead of a list of movesets)
    _df = board_state[board_state['color'] == color_cpu][[
        'piece_ID', 'piece_type', 'starting_position', 'corps', 'moveset']].explode('moveset')
    _df = _df[['piece_ID', 'piece_type', 'starting_position', 'corps', 'moveset']].rename(
        columns={'moveset': 'potential_position'})
    _enemy = board_state[board_state['color'] ==
                         color_user][['starting_position', 'piece_type']]

    # identify enemy locations that occupied
    _df = _df.merge(_enemy, how='left', left_on='potential_position',
                    right_on='starting_position', suffixes=['_attack', '_defend'])

    # calculate capture probability
    _df['capture_probability'] = _df.apply(lambda x: get_capture_probability(
        x['piece_type_attack'], x['piece_type_defend']), axis=1)
    _df = _df[['starting_position_attack',
               'potential_position', 'capture_probability', 'corps']]

    # return potential_position with highest capture probability
    return _df.sort_values(by=['capture_probability'], ascending=[False]) #HERE 


def get_possible_moveset_per_piece(position, piece, team, board_state, whiteMove, corpList):
    if team == 'b':
        available_squares = get_black_squares_available(corpList)
        corp_string = get_black_corp(position,corpList)
        board_state_obj = Boardstate(board_state, False, corpList)
        
    else:
        available_squares = get_white_squares_available(corpList)
        corp_string = get_white_corp(position, corpList)
        board_state_obj = Boardstate(board_state, True, corpList)


    #print(available_squares)
    current_piece_obj = Piece(team, piece.upper(), position, corp_string)
    

    if current_piece_obj.pos not in available_squares:
        pass
    else:
        in_range, setup, movement = board_state_obj.getValidMoveset(current_piece_obj)
        if len(in_range) != 0:
            move_list = in_range
        elif len(in_range) == 0 and len(setup) != 0:
            move_list = setup
        else:
            move_list = movement
        
        print('Piece: ' + team + piece.upper() + ' at position: ' + position)
        print('in range')
        print(in_range)
        print('setup')
        print(setup)
        print('movement')
        print(movement)
        print('move list')
        print(move_list)
        return(move_list)


def parse_board_state(board_state, iteration, corps_list, initial_piece_reference, list_of_corps_assignments, whiteMove, actionCounter):
    df_converted_board_state = pd.DataFrame(
        columns=['piece_ID', 'piece', 'piece_type', 'color', 'starting_position', 'corps', 'moveset', 'possible_moves', ])
    # get all possible movesets per piece (and respective positions)
    for i, position in enumerate(board_state.keys(), start=1000):
        _starting_position = position
        if iteration == 1:
            _pieceID = i
            _corps = [corp[1]
                      for corp in list_of_corps_assignments if _starting_position == corp[0]][0]
            initial_piece_reference += [[i, _starting_position,
                                         _corps, [_starting_position]]]
        else:
            _initial_state = [
                corps for corps in initial_piece_reference if corps[3][-1] == _starting_position]
            # print(_initial_state)
            _pieceID = _initial_state[0][0]
            _corps = _initial_state[0][2]
        if _corps not in corps_list:
            pass
        else:
            _piece = board_state.get(position)
            _piece_type = _piece[1].lower()
            _team = _piece[0]
            _moveset = get_possible_moveset_per_piece(
                _starting_position, _piece_type, _team, board_state, whiteMove, actionCounter)
            try:
                _possible_moves = len(_moveset)
            except:
                _possible_moves = 0
                pass
            # convert piece data into series
            _series = pd.Series([_pieceID, _piece, _piece_type, _team,
                                _starting_position, _corps, _moveset, _possible_moves], index=df_converted_board_state.columns)
            # add piece series to current board state
            df_converted_board_state = df_converted_board_state.append(
                _series, ignore_index=True)

    # find the current movesets and potential battles (along w/ probabilities)

    current_turn_movesets = get_movesets_per_board_state(
        df_converted_board_state)
    # print('moveset in function: ', current_turn_movesets)

    #new_board_state = generate_new_board_state(df_converted_board_state)

    #return new_board_state, current_turn_movesets
    current_turn_movesets.dropna(inplace=True)
    current_turn_movesets = current_turn_movesets.head(1)
    print(current_turn_movesets)
    return current_turn_movesets 




def produceAction(boardstate, whiteMove, actionCounter):
    current_board_state = boardstate #set to board_state_from_frontend
    list_of_corps_assignments = get_list_of_initial_corps_assignments(current_board_state)
    
    moves_to_send = []

    command_list = [1, 2, 3]
    i = 1
    while len(command_list) > 2:
        current_turn_movesets = parse_board_state(current_board_state, i, command_list, initial_piece_reference, list_of_corps_assignments, whiteMove, actionCounter)
        move_to_send = current_turn_movesets.iloc[0]['starting_position_attack'] + '-' + current_turn_movesets.iloc[0]['potential_position']
        moves_to_send.append(move_to_send)
        command_list.remove(current_turn_movesets.iloc[0][3])
        i += 1
    
    #active piece
    Apos = move_to_send[0:2]
    Acolor = boardstate[Apos][:1]
    Arank = boardstate[Apos][1:2]
    #target piece
    Tpos = move_to_send[3:]
    
    try:
        Tcolor = boardstate[Tpos][:1]
        Trank = boardstate[Tpos][1:2]
        
    except:
        Tcolor = Acolor
        Trank = Arank
        
    
    if (Acolor == Tcolor):
        action_to_send = {
            'actionType': 'MOVEMENT',
            'isAIGame': True,
            'activePiece': {
                'pos': Apos,
                'color': Acolor,
                'rank': Arank
            },
            'targetPiece': {
                'pos': Tpos,
                'color': Tcolor,
                'rank': Trank
            },
            'actionCount': actionCounter,
            'whiteMove': whiteMove
        }
    else:
        action_to_send = {
            'actionType': 'ATTACK_ATTEMPT',
            'isAIGame': True,
            'activePiece': {
                'pos': Apos,
                'color': Acolor,
                'rank': Arank
            },
            'targetPiece': {
                'pos': Tpos,
                'color': Tcolor,
                'rank': Trank
            },
            'actionCount': actionCounter,
            'whiteMove': whiteMove
        }

    print(action_to_send)
    #return action_to_send

#produceAction(dict_test_board_state_4,False,INITIAL_CORP_LIST_AI)

#produceAction(dict_test_pawn_board_state, False, PAWN_CORP_LIST_AI)

#get_possible_moveset_per_piece('c8','B','b', INITIAL_BOARDSTATE, False, INITIAL_CORP_LIST_AI)

#print(get_black_squares_available(INITIAL_CORP_LIST_AI))