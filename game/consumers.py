from threading import local
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from .models import Game, Message, Action
from .engine import Boardstate
from .testAI import produceAction

import traceback, json

class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        
        try: 
            self.game_id=int(self.game_id)
        except:
            await self.close()
            return

        game_metadata = await self.verify(self.game_id)
        if game_metadata == False:
            await self.close()
            return
        
        # Now accept connection request & establish live connection 
        await self.accept()
        # Call join_room(side) to handle establishment of group connection
        await self.join_room(game_metadata)
        if game_metadata[0] == False:
            await self.opp_online()
    
    async def disconnect(self, code):
        await self.disconn()
        await self.opp_offline()
        
    # Handles join room functions from connect()
    async def join_room(self, data):
        # Creates (or connects) to a group on the channel layer with group name of game_id
        await self.channel_layer.group_add(
            str(self.game_id),
            self.channel_name,
        )
        # If isAIGame
        if data[0]:  
            # Send join command to the created (or connected) group
            await self.send_json({
                "actionType": "JOIN",
                "isAIGame": data[0],
                "boardstate": data[1],
                "level": data[2],
                "whiteMove": data[3],
                "corplist": data[4],
                "white_captured": data[5],
                "black_captured": data[6],
                "readyToBlitz": data[7],
                "action_history": data[8]
            })
            print(f"Sending JOIN for AI Game")
        else:
            # Send join command to the created (or connected) group
            await self.send_json({
                "actionType": "JOIN",
                "isAIGame": data[0],
                "boardstate": data[1],
                "level": data[2],
                "whiteMove": data[3],
                "corplist": data[4],
                "white_captured": data[5],
                "black_captured": data[6],
                "readyToBlitz": data[7],
                "side": data[8],
                "local_opp_online": data[9],
                "action_history": data[10]
            })
            print(f"Sending JOIN for Multiplayer Game for {data[8]} side")
    
    @database_sync_to_async
    def verify(self, game_id):
        # Find current game, game isn't valid if it doesn't exist (wrong gameId route?)
        game = Game.objects.all().filter(id=game_id)[0]
        if not game:
            return False
        
        action_history = []
        action_list = list(Action.objects.all().filter(game=game))
        print(type(action_list))
        for action in action_list:
            action_history.append(action.content)
        
        user = self.scope["user"]
        side = 'white'
        local_opp_online = False
        
        # If opponent doesn't exist, it's an AI game
        if game.opponent == user:
            game.opponent_online = True
            side = 'black'
            if game.owner_online == True:
                local_opp_online = True
            print(f"Game_Id:{game_id}\t-\tSetting Opponent_Online In DB")
            game.save()
            return [False, game.boardstate, game.level, game.whitemove, game.corplist, game.white_captured, game.black_captured, game.readytoblitz, side, local_opp_online, action_history]
            
        elif game.opponent == None:
            if game.owner == user:
                game.owner_online = True
                print(f"Game_Id:{game_id}\t-\tSetting Owner_Online In DB")
                game.save()
                return [True, game.boardstate, game.level, game.whitemove, game.corplist, game.white_captured, game.black_captured, game.readytoblitz, action_history]
        
        elif game.owner == user:
            game.owner_online = True
            if game.opponent_online == True:
                local_opp_online = True
            print(f"Game_Id:{game_id}\t-\tSetting Owner_Online In DB")
            game.save()
            return [False, game.boardstate, game.level, game.whitemove, game.corplist, game.white_captured, game.black_captured, game.readytoblitz, side, local_opp_online, action_history]
        
        else:
            return False
    
    async def receive_json(self, content):
        # Grab actionType & isAIGame
        actionType = content.get("actionType")
        isAIGame = content.get("isAIGame")
        print("Received JSON over websockets of type " + actionType + " with an isAIGame bool of " + str(isAIGame))
        
        try:
            if actionType == "MOVEMENT":
                await self.new_move(content)
            elif actionType == "ATTACK_ATTEMPT":
                await self.attack_attempt(content)
            elif actionType == "HIGHLIGHT":
                await self.highlight(content)
            elif actionType == "DELEGATE":
                await self.delegate(content)
            elif actionType == "PASS":
                await self.pass_turn(content)
            elif actionType == "AI_TURN_REQ":
                await self.ai_turn_req(content)
            elif actionType == "GAME_OVER":
                await self.game_over_msg(content)
                await self.game_over(content["result"])
            elif actionType == "RESIGN":
                await self.resign()
                await self.game_over(content["result"])
            elif actionType == "CHAT_MESSAGE":
                await self.chat_message(content)
        except:
            pass
    
    async def opp_offline(self):
        await self.channel_layer.group_send(
            str(self.game_id),
            {
                "type": "offline.opp",
                'sender_channel_name': self.channel_name
            }
        )
    
    async def offline_opp(self,event):
        if self.channel_name != event['sender_channel_name']:
            await self.send_json({
                "actionType":"OPPONENT-OFFLINE",
            })
            print(f"{self.channel_name}\t-\tSending OPPONENT-OFFLINE")
    
    async def opp_online(self):
        await self.channel_layer.group_send(
            str(self.game_id),
            {
                "type": "online.opp",
                'sender_channel_name': self.channel_name
            }
        )
    
    async def online_opp(self,event):
        if self.channel_name != event['sender_channel_name']:
            await self.send_json({
                "actionType":"OPPONENT-ONLINE",
            })
            print(f"{self.channel_name}\t-\tSending OPPONENT-ONLINE")
    
     # Helper function called when a new-move command is recieved, broadcasts move.new event to group, handled in move_new
    async def new_move(self, payload):
        boardstate, whiteMove, corpList, readyToBlitz, white_captured, black_captured = await self.get_boardstate()
        
        board = Boardstate(boardstate=boardstate, whiteMove=whiteMove, corpList=corpList, readyToBlitz=readyToBlitz, white_captured=white_captured, black_captured=black_captured)
        
        isValidAction, new_boardstate, new_corpList, new_whiteMove, readyToBlitz, actionToBeLogged = board.processAction(payload)
        
        action_history = await self.log_action(actionToBeLogged)
        
        if isValidAction:
            await self.channel_layer.group_send(
                str(self.game_id),
                {
                    "type": "move.new",
                    "actionType": payload["actionType"],
                    "activePiece": payload["activePiece"],
                    "targetPiece": payload["targetPiece"],
                    "new_boardstate": new_boardstate,
                    "new_whiteMove": new_whiteMove,
                    "new_corpList": new_corpList,
                    "readyToBlitz": readyToBlitz,
                    "action_history": action_history,
                    'sender_channel_name': self.channel_name
                }
            )
            print(f"{self.channel_name}\t-\tValidated New-Move")
        else:
            print(f"{self.channel_name}\t-\tFailed to validate New-Move")
    
    # Pair handler of new_move(), recieves the event broadcast request & sends relevent message
    async def move_new(self, event):
        await self.send_json({
            "actionType": "MOVEMENT",
            "activePiece": event["activePiece"],
            "targetPiece": event["targetPiece"],
            "new_boardstate": event["new_boardstate"],
            "whiteMove": event["new_whiteMove"],
            "corpList": event["new_corpList"],
            "readyToBlitz": event["readyToBlitz"],
            "action_history": event["action_history"]
        })
        print(f"{event['sender_channel_name']}\t-\tSending New-Move")
        
        # Call update()
        await self.update(event["new_boardstate"], event["new_corpList"], event["new_whiteMove"], event["readyToBlitz"]) #,event["pgn"])
    
    # Helper function called when a new-move command is recieved, broadcasts move.new event to group, handled in move_new
    async def attack_attempt(self, payload):
        try:
            boardstate, whiteMove, corpList, readyToBlitz, white_captured, black_captured = await self.get_boardstate()
            
            board = Boardstate(boardstate=boardstate, whiteMove=whiteMove, corpList=corpList, readyToBlitz=readyToBlitz, white_captured=white_captured, black_captured=black_captured)
            
            isValidAction, isSuccessfulAttack, new_boardstate, roll_val, corpList, whiteMove, isBlitz, readyToBlitz, isEndGame, kingDead, white_captured, black_captured, actionToBeLogged = board.processAction(payload)
            
            action_history = await self.log_action(actionToBeLogged)
            
            if isValidAction:
                if isSuccessfulAttack:
                    if isEndGame:
                        print(f"{self.channel_name}\t-\tValidated Attack-Attempt as Successful [END_OF_GAME]")
                        await self.channel_layer.group_send(
                            str(self.game_id),
                            {
                                "type": "attempt.attack",
                                "actionType": "ATTACK_ATTEMPT",
                                "isSuccessfulAttack": isSuccessfulAttack,
                                "new_boardstate": new_boardstate,
                                "roll_val": roll_val,
                                "readyToBlitz": readyToBlitz,
                                "corpList": corpList,
                                "whiteMove": whiteMove,
                                'isBlitz': isBlitz,
                                'kingDead': kingDead,
                                'white_captured': white_captured,
                                'black_captured': black_captured,
                                'action_history': action_history,
                                "activePiece": payload["activePiece"],
                                "targetPiece": payload["targetPiece"],
                                'sender_channel_name': self.channel_name
                            }
                        )
                    else:
                        print(f"{self.channel_name}\t-\tValidated Attack-Attempt as Successful")
                        await self.channel_layer.group_send(
                            str(self.game_id),
                            {
                                "type": "attempt.attack",
                                "actionType": "ATTACK_ATTEMPT",
                                "isSuccessfulAttack": isSuccessfulAttack,
                                "new_boardstate": new_boardstate,
                                "roll_val": roll_val,
                                "readyToBlitz": readyToBlitz,
                                "corpList": corpList,
                                "whiteMove": whiteMove,
                                'isBlitz': isBlitz,
                                'white_captured': white_captured,
                                'black_captured': black_captured,
                                'action_history': action_history,
                                "activePiece": payload["activePiece"],
                                "targetPiece": payload["targetPiece"],
                                'sender_channel_name': self.channel_name
                            }
                        )
                else:
                    print(f"{self.channel_name}\t-\tValidated Attack-Attempt as Failed")
                    await self.channel_layer.group_send(
                        str(self.game_id),
                        {
                            "type": "attempt.attack",
                            "actionType": "ATTACK_ATTEMPT",
                            "isSuccessfulAttack": isSuccessfulAttack,
                            "new_boardstate": new_boardstate,
                            "roll_val": roll_val,
                            "readyToBlitz": readyToBlitz,
                            "corpList": corpList,
                            "whiteMove": whiteMove,
                            'isBlitz': isBlitz,
                            'action_history': action_history,
                            "activePiece": payload["activePiece"],
                            "targetPiece": payload["targetPiece"],
                            'sender_channel_name': self.channel_name
                        }
                    )
            else:
                print(f"{self.channel_name}\t-\tFailed to validate Attack-Attempt")
        except BaseException:
            tb = traceback.format_exc()
            print(tb)
    
    # Pair handler of new_move(), recieves the event broadcast request & sends relevent message
    async def attempt_attack(self, event):
        if event['isSuccessfulAttack'] == True:
            if 'kingDead' in event:
                print(f"{event['sender_channel_name']}\t-\tSending Attempt-Attack as Successful [END_OF_GAME]")
                await self.send_json({
                    "actionType": event["actionType"],
                    "isSuccessfulAttack": event["isSuccessfulAttack"],
                    "new_boardstate": event["new_boardstate"],
                    "roll_val": event["roll_val"],
                    "readyToBlitz": event["readyToBlitz"],
                    "corpList": event["corpList"],
                    "whiteMove": event["whiteMove"],
                    'isBlitz': event["isBlitz"],
                    'kingDead': event["kingDead"],
                    'white_captured': event["white_captured"],
                    'black_captured': event["black_captured"],
                    "activePiece": event["activePiece"],
                    "targetPiece": event["targetPiece"],
                    'action_history': event["action_history"]
                })
                await self.updateEOG(event["new_boardstate"], event["corpList"], event["whiteMove"], event["readyToBlitz"], event['kingDead'], event["white_captured"], event["black_captured"])
            else:
                print(f"{event['sender_channel_name']}\t-\tSending Attempt-Attack as Successful")
                await self.send_json({
                    "actionType": event["actionType"],
                    "isSuccessfulAttack": event["isSuccessfulAttack"],
                    "new_boardstate": event["new_boardstate"],
                    "roll_val": event["roll_val"],
                    "readyToBlitz": event["readyToBlitz"],
                    "corpList": event["corpList"],
                    "whiteMove": event["whiteMove"],
                    'isBlitz': event["isBlitz"],
                    'white_captured': event["white_captured"],
                    'black_captured': event["black_captured"],
                    "activePiece": event["activePiece"],
                    "targetPiece": event["targetPiece"],
                    'action_history': event["action_history"]
                })
                await self.updateSuccessAttack(event["new_boardstate"], event["corpList"], event["whiteMove"], event["readyToBlitz"], event["white_captured"], event["black_captured"])
        else:
            print(f"{event['sender_channel_name']}\t-\tSending Attempt-Attack as Failed")
            await self.send_json({
                "actionType": event["actionType"],
                "isSuccessfulAttack": event["isSuccessfulAttack"],
                "roll_val": event["roll_val"],
                "readyToBlitz": event["readyToBlitz"],
                "corpList": event["corpList"],
                "whiteMove": event["whiteMove"],
                'isBlitz': event["isBlitz"],
                "activePiece": event["activePiece"],
                "targetPiece": event["targetPiece"],
                'action_history': event["action_history"]
            })
            await self.update(event["new_boardstate"], event["corpList"], event["whiteMove"], event["readyToBlitz"])
        
    async def highlight(self, payload):
        boardstate, whiteMove, corpList, readyToBlitz, white_captured, black_captured = await self.get_boardstate()
        
        board = Boardstate(boardstate=boardstate, whiteMove=whiteMove, corpList=corpList, readyToBlitz=readyToBlitz, white_captured=white_captured, black_captured=black_captured)
        
        isValidAction, in_range, setup, movement = board.processAction(payload)
        
        if isValidAction:
            await self.channel_layer.group_send(
                str(self.game_id),
                {
                    "type": "move.highlight",
                    "actionType": "HIGHLIGHT",
                    "in_range": in_range,
                    "setup": setup,
                    "movement": movement,
                    'sender_channel_name': self.channel_name
                }
            )
            print(f"{self.channel_name}\t-\tValidated Highlight")
        else:
            print(f"{self.channel_name}\t-\tFailed to validate Highlight")
        
    async def move_highlight(self, event):
        # For everyone connected that is highlighting a piece
        if self.channel_name == event['sender_channel_name']:
            await self.send_json({
                "actionType": event['actionType'],
                "in_range": event['in_range'],
                "setup": event["setup"],
                "movement": event["movement"]
            })
            print(f"{event['sender_channel_name']}\t-\tSending Highlight-Move")
            
    async def delegate(self, payload):
        try:
            (whiteMove, corpList, readyToBlitz) = await self.delegate_db_handle(payload)
            
            await self.channel_layer.group_send(
                str(self.game_id), 
                {
                    "type": "send.delegate",
                    "actionType": "DELEGATE",
                    "whiteMove": whiteMove,
                    "corpList": corpList,
                    "readyToBlitz": readyToBlitz,
                    'sender_channel_name': self.channel_name
                }
            )
            print(f"{self.channel_name}\t-\tValidated & Processed DELEGATE")
        except BaseException:
            tb = traceback.format_exc()
            print(tb)
    
    async def send_delegate(self, event):
        await self.send_json({
            "actionType": event['actionType'],
            "whiteMove": event['whiteMove'],
            "corpList": event["corpList"],
            "readyToBlitz": event["readyToBlitz"]
        })
        print(f"{event['sender_channel_name']}\t-\tSending DELEGATE")
        
    @database_sync_to_async
    def delegate_db_handle(self, payload):
        # Find current game, toss update if doesn't exist for some reason
        game = Game.objects.all().filter(id=self.game_id)[0]
        if not game:
            print("DB update failed, game not found")
            return
        
        friendly = 'w' if game.whitemove else 'b'
        enemy = 'b' if game.whitemove else 'w'
        
        if payload["whiteMove"] == game.whitemove and game.corplist[friendly]['kingCorp']["command_authority_remaining"] > 0 and len(game.corplist[friendly][payload["targetCorp"]]["under_command"]) < 6:
            local_delegated_piece = json.loads(payload["delegatedPiece"])
            local_delegated_piece["corp"] = payload["targetCorp"]
            for corp in game.corplist[friendly]:
                if corp == 'kingCorp':
                    game.corplist[friendly][corp]["command_authority_remaining"] = game.corplist[friendly][corp]["command_authority_remaining"] - 1
                    game.corplist[friendly][corp]["under_command"].remove(json.loads(payload["delegatedPiece"]))
                if corp == payload["targetCorp"]:
                    game.corplist[friendly][payload["targetCorp"]]["under_command"].append(local_delegated_piece)
        
        # Check for any remaining actions
        turnend = True
        for corp in game.corplist[friendly]:
            if game.corplist[friendly][corp]["command_authority_remaining"] == 1:
                turnend = False
        
        if turnend:
            for corp in game.corplist[friendly]:
                game.corplist[friendly][corp]["command_authority_remaining"] = -999
            for corp in game.corplist[enemy]:
                game.corplist[enemy][corp]["command_authority_remaining"] = 1
            game.whiteMove = not game.whiteMove  # Swaps players.
            game.readyToBlitz = []
        
        print("Saving game details")
        game.save()
        print("Successfully saved")
        
        return (game.whitemove, game.corplist, game.readytoblitz)
    
    async def pass_turn(self, payload):
        try:
            (whiteMove, corpList, readyToBlitz) = await self.pass_turn_db_handle(payload)
            
            await self.channel_layer.group_send(
                str(self.game_id), 
                {
                    "type": "turn.pass",
                    "actionType": "PASS",
                    "whiteMove": whiteMove,
                    "corpList": corpList,
                    "readyToBlitz": readyToBlitz,
                    'sender_channel_name': self.channel_name
                }
            )
            print(f"{self.channel_name}\t-\tValidated & Processed PASS")
        except BaseException:
            tb = traceback.format_exc()
            print(tb)
        
    async def turn_pass(self, event):
        await self.send_json({
            "actionType": event['actionType'],
            "whiteMove": event['whiteMove'],
            "corpList": event["corpList"],
            "readyToBlitz": event["readyToBlitz"]
        })
        print(f"{event['sender_channel_name']}\t-\tSending PASS")
    
    @database_sync_to_async
    def pass_turn_db_handle(self, payload):
        # Find current game, toss update if doesn't exist for some reason
        game = Game.objects.all().filter(id=self.game_id)[0]
        if not game:
            print("DB update failed, game not found")
            return
        
        friendly = 'w' if game.whitemove else 'b'
        enemy = 'b' if game.whitemove else 'w'
        
        if payload["whiteMove"] == game.whitemove:
            for corp in game.corplist[friendly]:
                game.corplist[friendly][corp]["command_authority_remaining"] = -999
            for corp in game.corplist[enemy]:
                game.corplist[enemy][corp]["command_authority_remaining"] = 1
            game.whitemove = not game.whitemove  # Swaps players.
            game.readytoblitz = []
        
        print("Saving game details")
        game.save()
        print("Successfully saved")
        
        return (game.whitemove, game.corplist, game.readytoblitz)
        
    # Called on recieved request from front-end for an AI turn
    async def ai_turn_req(self, payload):
        try:
            game_ended_flag = False
            whiteMove = payload["whiteMove"]
            new_boardstate = {}
            whiteMove = False
            corpList = {}
            readyToBlitz = []
            white_captured = []
            black_captured = []
            action_history = []
            if (not whiteMove and payload["isAIGame"]):
                black_actions = []
                black_moves = []
                while whiteMove == False and game_ended_flag == False:
                    currentBoardstate, currentWhiteMove, currentCorpList, readyToBlitz, white_captured, black_captured = await self.get_boardstate()
                    
                    AIAction = produceAction(currentBoardstate, currentWhiteMove, currentCorpList, readyToBlitz, white_captured, black_captured)
                    
                    board = Boardstate(boardstate=currentBoardstate, whiteMove=currentWhiteMove, corpList=currentCorpList, readyToBlitz=readyToBlitz, white_captured=white_captured, black_captured=black_captured)
                    
                    match AIAction["actionType"]:
                        case "MOVEMENT":
                            isValidAction, new_boardstate, corpList, whiteMove, readyToBlitz, actionToBeLogged = board.processAction(AIAction)
                            
                            sourcePos = AIAction["activePiece"]["pos"]
                            targetPos = AIAction["targetPiece"]["pos"]
                            AIAction["new_boardstate"] = new_boardstate
                            
                            if isValidAction:
                                action_history = await self.log_action(actionToBeLogged)
                                AIAction["action_history"] = action_history
                                black_actions.append(AIAction)
                                black_moves.append(sourcePos + "-" + targetPos)
                                await self.update(new_boardstate, corpList, whiteMove, readyToBlitz)
                            else:
                                print(AIAction)
                                print(f"{self.channel_name}\t-\tInvalid AI Movement")
                                
                        case "ATTACK_ATTEMPT":
                            isValidAction, isSuccessfulAttack, new_boardstate, roll_val, corpList, whiteMove, isBlitz, readyToBlitz, isEndGame, kingDead, white_captured, black_captured, actionToBeLogged = board.processAction(AIAction)
                            
                            sourcePos = AIAction["activePiece"]["pos"]
                            targetPos = AIAction["targetPiece"]["pos"]
                            
                            AIAction["roll_val"] = roll_val
                            AIAction["isSuccessfulAttack"] = isSuccessfulAttack
                            AIAction["isBlitz"] = isBlitz
                            AIAction["readyToBlitz"] = readyToBlitz
                            AIAction["new_boardstate"] = new_boardstate
                            AIAction["corpList"] = corpList
                            AIAction["whiteMove"] = whiteMove
                            AIAction["white_captured"] = white_captured
                            AIAction["black_captured"] = black_captured
                            
                            if isValidAction:
                                if isSuccessfulAttack:
                                    if isEndGame:
                                        game_ended_flag = True
                                        action_history = await self.log_action(actionToBeLogged)
                                        AIAction["action_history"] = action_history
                                        AIAction["kingDead"] = kingDead
                                        black_actions.append(AIAction)
                                        black_moves.append(sourcePos + "-" + targetPos)
                                        await self.updateEOG(new_boardstate, corpList, whiteMove, readyToBlitz, kingDead, white_captured, black_captured)
                                    else:
                                        action_history = await self.log_action(actionToBeLogged)
                                        AIAction["action_history"] = action_history
                                        black_actions.append(AIAction)
                                        black_moves.append(sourcePos + "-" + targetPos)
                                        await self.updateSuccessAttack(new_boardstate, corpList, whiteMove, readyToBlitz, white_captured, black_captured)
                                else:
                                    action_history = await self.log_action(actionToBeLogged)
                                    AIAction["action_history"] = action_history
                                    black_actions.append(AIAction)
                                    black_moves.append("")
                                    await self.update(new_boardstate, corpList, whiteMove, readyToBlitz)
                            else:
                                print(AIAction)
                                print(f"{self.channel_name}\t-\tInvalid AI Attack")
                
                if game_ended_flag:
                    await self.channel_layer.group_send(
                        str(self.game_id), 
                        {
                            "type": "ai.turn.res",
                            "actionType": "AI_TURN_RES",
                            "black_actions": black_actions,
                            "black_moves": black_moves,
                            "kingDead": kingDead,
                            "new_boardstate": new_boardstate,
                            "whiteMove": whiteMove,
                            "corpList": corpList,
                            "readyToBlitz": readyToBlitz,
                            'white_captured': white_captured,
                            'black_captured': black_captured,
                            "action_history": action_history,
                            'sender_channel_name': self.channel_name
                        }
                    )
                    print(f"{self.channel_name}\t-\tValidated & Processed AI_TURN_REQ [END_OF_GAME]")
                else:
                    await self.channel_layer.group_send(
                        str(self.game_id), 
                        {
                            "type": "ai.turn.res",
                            "actionType": "AI_TURN_RES",
                            "black_actions": black_actions,
                            "black_moves": black_moves,
                            "new_boardstate": new_boardstate,
                            "whiteMove": whiteMove,
                            "corpList": corpList,
                            "readyToBlitz": readyToBlitz,
                            'white_captured': white_captured,
                            'black_captured': black_captured,
                            "action_history": action_history,
                            'sender_channel_name': self.channel_name
                        }
                    )
                    print(f"{self.channel_name}\t-\tValidated & Processed AI_TURN_REQ")
            else:
                print(f"{self.channel_name}\t-\tFailed to Validate And/Or Process AI_TURN_REQ")
        except BaseException:
            tb = traceback.format_exc()
            print(tb)
    
    async def ai_turn_res(self, event):
        if "kingDead" in event:
            await self.send_json({
                "actionType": event['actionType'],
                "black_actions": event['black_actions'],
                "black_moves": event["black_moves"],
                "kingDead": event["kingDead"],
                "new_boardstate": event["new_boardstate"],
                "whiteMove": event["whiteMove"],
                "corpList": event["corpList"],
                "readyToBlitz": event["readyToBlitz"],
                'white_captured': event["white_captured"],
                'black_captured': event["black_captured"],
                "action_history": event["action_history"],
            })
            print(f"{event['sender_channel_name']}\t-\tSending AI_TURN_REQ [END_OF_GAME]")
        else:
            await self.send_json({
                "actionType": event['actionType'],
                "black_actions": event['black_actions'],
                "black_moves": event["black_moves"],
                "new_boardstate": event["new_boardstate"],
                "whiteMove": event["whiteMove"],
                "corpList": event["corpList"],
                "readyToBlitz": event["readyToBlitz"],
                'white_captured': event["white_captured"],
                'black_captured': event["black_captured"],
                "action_history": event["action_history"],
            })
            print(f"{event['sender_channel_name']}\t-\tSending AI_TURN_REQ")
    
    async def resign(self):
        await self.channel_layer.group_send(
            str(self.game_id),
            {
                "type": "resign.game",
                'sender_channel_name': self.channel_name
            }
        )
    
    async def resign_game(self, event):
        if self.channel_name != event['sender_channel_name']:
            await self.send_json({
                "actionType":"OPPONENT_RESIGNED",
            })
    
    async def chat_message(self, payload):
        try:
            print(payload)
            message = payload['message']
            username = payload['username']
            game_id = payload['game_id']
            
            await self.save_message(username, game_id, message)
        
            # Send message to room group
            await self.channel_layer.group_send(
                str(self.game_id),
                {
                    'type': 'message_chat',
                    'message': message,
                    'username': username
                }
            )
        except BaseException:
            tb = traceback.format_exc()
            print(tb)
        
    # Receive message from room group
    async def message_chat(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send_json({
            'actionType': "CHAT_MESSAGE",
            'message': message,
            'username': username
        })
        
    # Add a new method to the class
    @database_sync_to_async
    def save_message(self, username, game_id, message):
        user = User.objects.get(username=username)
        game = Game.objects.get(pk=game_id)

        Message.objects.create(user=user, lobby=game, content=message)
    
    @database_sync_to_async
    def log_action(self, actionToBeLogged):
        game = Game.objects.get(pk=self.game_id)
        Action.objects.create(game=game, content=actionToBeLogged)
        
        action_history = []
        action_list = list(Action.objects.all().filter(game=game))
        for action in action_list:
            action_history.append(action.content)
        
        return action_history
    
    # Called after every move_new & attempt_action JSON is sent to persist gamestate to DB
    @database_sync_to_async
    def update(self, new_boardstate, corplist, whiteMove, readyToBlitz): # , pgn):
        # Find current game, toss update if doesn't exist for some reason
        game = Game.objects.all().filter(id=self.game_id)[0]
        if not game:
            print("DB update failed, game not found")
            return
        
        # Replace existing boardstate & PGN with updated version
        game.boardstate = new_boardstate
        game.corplist = corplist
        game.whitemove = whiteMove
        game.readytoblitz = readyToBlitz
        # game.pgn = pgn
        
        # Persist transaction
        print("Saving game details")
        game.save()
        print("Successfully saved")
        
    # Called after every move_new & attempt_action JSON is sent to persist gamestate to DB
    @database_sync_to_async
    def updateSuccessAttack(self, new_boardstate, corplist, whiteMove, readyToBlitz, white_captured, black_captured): # , pgn):
        # Find current game, toss update if doesn't exist for some reason
        game = Game.objects.all().filter(id=self.game_id)[0]
        if not game:
            print("DB update failed, game not found")
            return
        
        # Replace existing boardstate & PGN with updated version
        game.boardstate = new_boardstate
        game.corplist = corplist
        game.whitemove = whiteMove
        game.readytoblitz = readyToBlitz
        game.white_captured = white_captured
        game.black_captured = black_captured
        # game.pgn = pgn
        
        # Persist transaction
        print("Saving game details")
        game.save()
        print("Successfully saved")
        
    # Called after every move_new & attempt_action JSON is sent to persist gamestate to DB
    @database_sync_to_async
    def updateEOG(self, new_boardstate, corplist, whiteMove, readyToBlitz, kingDead, white_captured, black_captured): # , pgn):
        # Find current game, toss update if doesn't exist for some reason
        game = Game.objects.all().filter(id=self.game_id)[0]
        if not game or game.status == 3:
            return
        
        # Replace existing boardstate & PGN with updated version
        game.boardstate = new_boardstate
        game.corplist = corplist
        game.whitemove = whiteMove
        game.readytoblitz = readyToBlitz
        game.white_captured = white_captured
        game.black_captured = black_captured
        # game.pgn = pgn
        
        # End game
        game.status = 3
        if kingDead == 'w':
            game.winner = 'White wins'
        if kingDead == 'b':
            game.winner = 'Black wins'

        # Persist transaction
        print("Saving game details")
        game.save()
        print("Successfully saved")
    
    @database_sync_to_async
    def game_over(self, result):
        game = Game.objects.all().filter(id=self.game_id)[0]
        if game.status == 3:
            return
        game.winner = result
        game.status = 3
        
        # Persist transaction
        print("Saving game details")
        game.save()
        print("Successfully saved")
        
    async def game_over_msg(self, event):
        if self.channel_name != event['sender_channel_name']:
            await self.send_json({
                "actionType": event["actionType"],
                "result": event["result"]
            })

    # Helper function to grab the current boardstate from the DB
    @database_sync_to_async
    def get_boardstate(self):
        game = Game.objects.all().filter(id=self.game_id)[0]
        return game.boardstate, game.whitemove, game.corplist, game.readytoblitz, game.white_captured, game.black_captured
    
    @database_sync_to_async
    def disconn(self):
        user = self.scope["user"]
        game = Game.objects.all().filter(id=self.game_id)[0]
        if game.opponent == user:
            game.opponent_online = False
            print(f"{self.channel_name}\t-\tSetting OPPONENT-OFFLINE")
        elif game.owner == user:
            game.owner_online = False
            print(f"{self.channel_name}\t-\tSending OWNER-OFFLINE")
        game.save()
        print(f"Successfully Disconnected")