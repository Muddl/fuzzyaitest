from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Game
from .engine import Boardstate
from .testAI import produceMove

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
                "actionCount": data[4],
                "white_captured": data[5],
                "black_captured": data[6]
            })
            print(f"Sending JOIN for AI Game")
    
    @database_sync_to_async
    def verify(self, game_id):
        # Find current game, game isn't valid if it doesn't exist (wrong gameId route?)
        game = Game.objects.all().filter(id=game_id)[0]
        if not game:
            return False
        
        # If opponent doesn't exist, it's an AI game
        if game.opponent == None:
            user = self.scope["user"]
            
            if game.owner == user:
                game.owner_online = True
                print(f"Game_Id:{game_id}\t-\tSetting Owner_Online In DB")
            else:
                return False
        
            game.save()
            
            return [True, game.boardstate, game.level, game.whitemove, game.actioncount, game.white_captured, game.black_captured]
    
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
            elif actionType == "AI_ACTION_REQ":
                await self.ai_action_req(content);
        except:
            pass
    
     # Helper function called when a new-move command is recieved, broadcasts move.new event to group, handled in move_new
    async def new_move(self, payload):
        boardstate, whiteMove, actionCounter = await self.get_boardstate()
        
        board = Boardstate(boardstate=boardstate, whiteMove=whiteMove, actionCounter=actionCounter)
        
        isValidAction, new_boardstate, actionCount, whiteMove = board.processAction(payload)
        
        if isValidAction:
            await self.channel_layer.group_send(
                str(self.game_id),
                {
                    "type": "move.new",
                    "actionType": payload["actionType"],
                    "activePiece": payload["activePiece"],
                    "targetPiece": payload["targetPiece"],
                    "new_boardstate": new_boardstate,
                    "whiteMove": whiteMove,
                    "actionCount": actionCount,
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
            "whiteMove": event["whiteMove"],
            "actionCount": event["actionCount"],
            # "pgn": event["pgn"],
        })
        print(f"{event['sender_channel_name']}\t-\tSending New-Move")
        
        # Call update(baordstate, pgn) handler to manage DB persistence
        await self.update(event["new_boardstate"], event["actionCount"], event["whiteMove"]) #,event["pgn"])
    
    # Helper function called when a new-move command is recieved, broadcasts move.new event to group, handled in move_new
    async def attack_attempt(self, payload):
        boardstate, whiteMove, actionCounter = await self.get_boardstate()
        
        board = Boardstate(boardstate=boardstate, whiteMove=whiteMove, actionCounter=actionCounter)
        
        if (payload["activePiece"]["rank"] == "N" and payload["blitz"]):
            isValidAction, isSuccessfulAttack, new_boardstate, roll_val, actionCount, whiteMove, blitz = board.processAction(payload)
        else:
            isValidAction, isSuccessfulAttack, new_boardstate, roll_val, actionCount, whiteMove = board.processAction(payload)
            
        if isValidAction:
            if isSuccessfulAttack:
                print(f"{self.channel_name}\t-\tValidated Attack-Attempt as Successful")
                if (payload["activePiece"]["rank"] == "N" and payload["blitz"]):
                    await self.channel_layer.group_send(
                        str(self.game_id),
                        {
                            "type": "attempt.attack",
                            "actionType": "ATTACK_ATTEMPT",
                            "isSuccessfulAttack": isSuccessfulAttack,
                            "new_boardstate": new_boardstate,
                            "roll_val": roll_val,
                            "blitz": blitz,
                            "actionCount": actionCount,
                            "whiteMove": whiteMove,
                            "activePiece": payload["activePiece"]["color"] + payload["activePiece"]["rank"],
                            "targetPiece": payload["targetPiece"]["color"] + payload["targetPiece"]["rank"],
                            'sender_channel_name': self.channel_name
                        }
                    )
                else:
                    await self.channel_layer.group_send(
                        str(self.game_id),
                        {
                            "type": "attempt.attack",
                            "actionType": "ATTACK_ATTEMPT",
                            "isSuccessfulAttack": isSuccessfulAttack,
                            "new_boardstate": new_boardstate,
                            "roll_val": roll_val,
                            "actionCount": actionCount,
                            "whiteMove": whiteMove,
                            "activePiece": payload["activePiece"]["color"] + payload["activePiece"]["rank"],
                            "targetPiece": payload["targetPiece"]["color"] + payload["targetPiece"]["rank"],
                            'sender_channel_name': self.channel_name
                        }
                    )
            else:
                print(f"{self.channel_name}\t-\tValidated Attack-Attempt as Failed")
                if (payload["activePiece"]["rank"] == "N" and payload["blitz"]):
                    await self.channel_layer.group_send(
                        str(self.game_id),
                        {
                            "type": "attempt.attack",
                            "actionType": "ATTACK_ATTEMPT",
                            "isSuccessfulAttack": isSuccessfulAttack,
                            "new_boardstate": new_boardstate,
                            "roll_val": roll_val,
                            "blitz": blitz,
                            "actionCount": actionCount,
                            "whiteMove": whiteMove,
                            "activePiece": payload["activePiece"]["color"] + payload["activePiece"]["rank"],
                            "targetPiece": payload["targetPiece"]["color"] + payload["targetPiece"]["rank"],
                            'sender_channel_name': self.channel_name
                        }
                    )
                else:
                    await self.channel_layer.group_send(
                        str(self.game_id),
                        {
                            "type": "attempt.attack",
                            "actionType": "ATTACK_ATTEMPT",
                            "isSuccessfulAttack": isSuccessfulAttack,
                            "new_boardstate": new_boardstate,
                            "roll_val": roll_val,
                            "actionCount": actionCount,
                            "whiteMove": whiteMove,
                            "activePiece": payload["activePiece"]["color"] + payload["activePiece"]["rank"],
                            "targetPiece": payload["targetPiece"]["color"] + payload["targetPiece"]["rank"],
                            'sender_channel_name': self.channel_name
                        }
                    )
        else:
            print(f"{self.channel_name}\t-\tFailed to validate Attack-Attempt")
    
    # Pair handler of new_move(), recieves the event broadcast request & sends relevent message
    async def attempt_attack(self, event):
        if event['isSuccessfulAttack']:
            if "blitz" in event:
                print(f"{event['sender_channel_name']}\t-\tSending Attempt-Attack as Successful")
                await self.send_json({
                    "actionType": event["actionType"],
                    "isSuccessfulAttack": event["isSuccessfulAttack"],
                    "new_boardstate": event["new_boardstate"],
                    "roll_val": event["roll_val"],
                    "blitz": event["blitz"],
                    "actionCount": event["actionCount"],
                    "whiteMove": event["whiteMove"],
                    "activePiece": event["activePiece"],
                    "targetPiece": event["targetPiece"],
                    # "pgn": event["pgn"],
                })
            else:
                print(f"{event['sender_channel_name']}\t-\tSending Attempt-Attack as Successful")
                await self.send_json({
                    "actionType": event["actionType"],
                    "isSuccessfulAttack": event["isSuccessfulAttack"],
                    "new_boardstate": event["new_boardstate"],
                    "roll_val": event["roll_val"],
                    "actionCount": event["actionCount"],
                    "whiteMove": event["whiteMove"],
                    "activePiece": event["activePiece"],
                    "targetPiece": event["targetPiece"],
                    # "pgn": event["pgn"],
                })
        else:
            if "blitz" in event:
                print(f"{event['sender_channel_name']}\t-\tSending Attempt-Attack as Failed")
                await self.send_json({
                    "actionType": event["actionType"],
                    "isSuccessfulAttack": event["isSuccessfulAttack"],
                    "roll_val": event["roll_val"],
                    "blitz": event["blitz"],
                    "actionCount": event["actionCount"],
                    "whiteMove": event["whiteMove"],
                    "activePiece": event["activePiece"],
                    "targetPiece": event["targetPiece"],
                    # "pgn": event["pgn"],
                })
            else:
                print(f"{event['sender_channel_name']}\t-\tSending Attempt-Attack as Failed")
                await self.send_json({
                    "actionType": event["actionType"],
                    "isSuccessfulAttack": event["isSuccessfulAttack"],
                    "roll_val": event["roll_val"],
                    "actionCount": event["actionCount"],
                    "whiteMove": event["whiteMove"],
                    "activePiece": event["activePiece"],
                    "targetPiece": event["targetPiece"],
                    # "pgn": event["pgn"],
                })
        
        await self.update(event["new_boardstate"], event["actionCount"], event["whiteMove"]) #,event["pgn"])
        
    async def highlight(self, payload):
        boardstate, whiteMove, actionCounter = await self.get_boardstate()
        
        board = Boardstate(boardstate=boardstate, whiteMove=whiteMove, actionCounter=actionCounter)
        
        isValidAction, highlight_pos = board.processAction(payload)
        
        if isValidAction:
            await self.channel_layer.group_send(
                str(self.game_id),
                {
                    "type": "move.highlight",
                    "actionType": "HIGHLIGHT",
                    "highlight_pos": highlight_pos,
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
                "highlight_pos": event['highlight_pos']
            })
            print(f"{event['sender_channel_name']}\t-\tSending Highlight-Move")
    
    # Called on recieved request from front-end for an AI turn
    async def ai_action_req(self, payload):
        boardstate, whiteMove, actionCounter = await self.get_boardstate()
        if (not whiteMove and actionCounter < 3 and payload["isAIGame"]):
            moveString = produceMove(boardstate)
            print(moveString)
            board = Boardstate(boardstate=boardstate, whiteMove=whiteMove, actionCounter=actionCounter)
            isValidAction, actionString = board.parseMoveString(moveString)

            if isValidAction:
                await self.channel_layer.group_send(
                    str(self.game_id), 
                    {
                        "type": "ai.request",
                        "actionType": "AI_ACTION_REQ",
                        "actionString": actionString,
                        'sender_channel_name': self.channel_name
                    }
                )
                print(f"{self.channel_name}\t-\tValidated AI_ACTION_REQ")
            else:
                print(f"{self.channel_name}\t-\tFailed to validate AI_ACTION_REQ")
    
    async def ai_request(self, event):
        await self.send_json({
                "actionType": event['actionType'],
                "actionString": event['actionString']
            })
        print(f"{event['sender_channel_name']}\t-\tSending AI_ACTION_REQ")
            
    
    # Called after every move_new & attempt_action JSON is sent to persist gamestate to DB
    @database_sync_to_async
    def update(self, new_boardstate, actionCount, whiteMove): # , pgn):
        # Find current game, toss update if doesn't exist for some reason
        game = Game.objects.all().filter(id=self.game_id)[0]
        if not game:
            print("DB update failed, game not found")
            return
        
        # Replace existing boardstate & PGN with updated version
        game.boardstate = new_boardstate
        game.actioncount = actionCount
        game.whitemove = whiteMove
        # game.pgn = pgn
        
        # Persist transaction
        print("Saving game details")
        game.save()
        print("Successfully saved")

    # Helper function to grab the current boardstate from the DB
    @database_sync_to_async
    def get_boardstate(self):
        game = Game.objects.all().filter(id=self.game_id)[0]
        return game.boardstate, game.whitemove, game.actioncount