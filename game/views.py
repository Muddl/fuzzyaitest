from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Game

@login_required
def game(request, game_id):
    game = get_object_or_404(Game,pk=game_id)
    if game.status == 3:
        messages.add_message(request, messages.ERROR, "This game has already been completed! Start another")
        return HttpResponseRedirect(reverse("homepage"))
    if request.user != game.owner:
        messages.add_message(request, messages.ERROR, "This game already has enough participants. Try joining another")
        return HttpResponseRedirect(reverse("homepage"))
    return render(request, "game/game.html", {"game_id":game_id})
