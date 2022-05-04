from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Game, Message, Action

@login_required
def game(request, game_id):
    game = get_object_or_404(Game,pk=game_id)
    chat_messages = Message.objects.filter(lobby=game)[0:25]
    actions = Action.objects.filter(game=game)[0:5]
    
    player_username = request.user
    opp_username = game.opponent if game.opponent != None else "AI"
    if game.status == 3:
        messages.add_message(request, messages.ERROR, "This game has already been completed! Start another")
        return HttpResponseRedirect(reverse("homepage"))
    if request.user != game.owner:
        opp_username = game.owner
        if game.status == 1 and game.opponent == None:
            game.opponent = request.user
            game.status = 2
            game.save()
            opp_username = game.owner
            messages.add_message(request, messages.SUCCESS, "You have joined this game successfully!")
        elif game.status == 2 and (game.opponent == None or game.opponent != request.user):
            messages.add_message(request, messages.ERROR, "This game already has enough participants. Try joining another")
            return HttpResponseRedirect(reverse("homepage"))
    return render(request, "game/game.html", {"game_id": game_id, "player_username": player_username, "opp_username": opp_username, "chat_messages": chat_messages, "actions": actions })
