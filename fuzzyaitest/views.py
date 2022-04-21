from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.db.models import Q

from game.models import Game

@login_required
def index(request):
    ai = Game.objects.all().filter(opponent__isnull=True).exclude(status=3)
    ai_list = []
    for game in ai:
        metadata = {}
        metadata["link"] = f"/game/{game.pk}"
        metadata["level"] = game.level
        metadata["created_at"] = game.created_at
        metadata["updated_at"] = game.updated_at
        ai_list.append(metadata)
    return render(request, 'webapp/homepage.html', { "ai": ai_list })

class register(View):
    def get(self, request):
        return render(request, "registration/signup.html")
    def post(self, request):
        first_name=request.POST["fname"]
        last_name=request.POST["lname"]
        username=request.POST["username"]
        email=request.POST["email"]
        password=request.POST["password"]
        passwordconf=request.POST["passwordconf"]
        if password != passwordconf:
            messages.add_message(request, messages.ERROR, "Passwords do not match")
            return HttpResponseRedirect(reverse("register"))
        try:
            User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        except:
            messages.add_message(request, messages.ERROR, "This username already exists!")
            return HttpResponseRedirect(reverse("register"))
        messages.add_message(request, messages.SUCCESS, "User successfully registered! Login now...")
        return HttpResponseRedirect("/accounts/login/")
    
class createGame(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,"game/create.html")
    def post(self, request):
        level = request.POST["level"]
        
        if level == "undef":
            messages.add_message(request, messages.ERROR, "Please choose a level if you are creating a public room!")
            return HttpResponseRedirect(reverse("create"))
        l = Game(owner=request.user, level=level)
        l.save()
        messages.add_message(request, messages.SUCCESS, "AI Game created and displayed in Homepage.")
        return HttpResponseRedirect(reverse("homepage"))

@login_required
def ongoing(request):
    games = []
    l = Game.objects.all().filter(owner=request.user).filter(status=1)
    g = Game.objects.all().filter(Q(owner=request.user) | Q(opponent=request.user)).filter(status=2)
    for i in g:
        x = {}
        if i.owner == request.user:
            x["opponent"] = i.opponent
            x["side"] = i.owner_side
        else:
            x["opponent"] = i.owner
            if i.owner_side == "white":
                x["side"] = "black"
            else:
                x["side"] = "white"
        x["link"] = f"/game/{i.pk}"
        games.append(x) 
    return render(request, "game/ongoing.html", {"public":l, "ongoing": games})

@login_required
def completed(request):
    games=[]
    g = Game.objects.all().filter(Q(owner=request.user) | Q(opponent=request.user)).filter(status=3)
    for i in g:
        x = {}
        x["id"] = i.pk
        x["result"] = ""
        x["ended"] = i.updated_at
        if i.owner == request.user:
            x["opponent"] = i.opponent
            x["side"] = i.owner_side
            if i.winner == "White wins":
                if i.owner_side == "white":
                    x["result"] = "You won this match"
                else:
                    x["result"] = "You lost this match"
            elif i.winner == "Black wins":
                if i.owner_side == "black":
                    x["result"] = "You won this match"
                else:
                    x["result"] = "You lost this match"
            else:
                x["result"] = i.winner
        else:
            x["opponent"] = i.owner
            if i.owner_side == "white":
                x["side"] = "black"
            else:
                x["side"] = "white"
            if i.winner == "Black wins":
                if i.owner_side == "white":
                    x["result"] = "You won this match"
                else:
                    x["result"] = "You lost this match"
            elif i.winner == "White wins":
                if i.owner_side == "black":
                    x["result"] = "You won this match"
                else:
                    x["result"] = "You lost this match"
            else:
                x["result"] = i.winner
        games.append(x)
        print(games)
    return render(request, "game/completed.html", {"completed": games})

@login_required
def rules(request):
    return render(request, "webapp/rules.html")

