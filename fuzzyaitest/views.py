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
    ai = Game.objects.all().filter(owner=request.user).filter(status=2).filter(opponent__isnull=True).exclude(status=3).order_by('-updated_at')
    ai_list = []
    for game in ai:
        metadata = {}
        metadata["id"] = game.pk
        metadata["link"] = f"/game/{game.pk}"
        metadata["level"] = game.level
        metadata["created_at"] = game.created_at
        metadata["updated_at"] = game.updated_at
        ai_list.append(metadata)
    
    my_multi = Game.objects.all().filter(Q(owner=request.user) | Q(opponent=request.user)).exclude(status=3).exclude(opponent__isnull=True).order_by('-updated_at')
    my_multi_list = []
    for game in my_multi:
        metadata = {}
        metadata["id"] = game.pk
        metadata["link"] = f"/game/{game.pk}"
        metadata["white"] = game.owner
        metadata["black"] = game.opponent
        metadata["created_at"] = game.created_at
        metadata["updated_at"] = game.updated_at
        my_multi_list.append(metadata)
        
    open_multi = Game.objects.all().exclude(Q(owner=request.user) | Q(opponent=request.user)).filter(status=1).filter(opponent__isnull=True).exclude(status=3).order_by('-updated_at')
    open_multi_list = []
    for game in open_multi:
        metadata = {}
        metadata["id"] = game.pk
        metadata["link"] = f"/game/{game.pk}"
        metadata["white"] = game.owner
        metadata["black"] = game.opponent
        metadata["created_at"] = game.created_at
        metadata["updated_at"] = game.updated_at
        open_multi_list.append(metadata)
    
    return render(request, 'webapp/homepage.html', { "ai": ai_list, "my_multi": my_multi_list, "open_multi": open_multi_list })

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
        isAIGame = eval(request.POST["isAIGame"])
        username = request.POST["username"]
        level = request.POST["level"]
        
        if isAIGame:
            if level == "undef":
                messages.add_message(request, messages.ERROR, "Please choose a level if you are creating an AI game!")
                return HttpResponseRedirect(reverse("create"))
            l = Game(owner=request.user, level=level, status=2)
            l.save()
            messages.add_message(request, messages.SUCCESS, "AI Game created and displayed in Homepage.")
            return HttpResponseRedirect(reverse("homepage"))
        else:
            if username:
                try:
                    u = User.objects.get(username=username)
                    if u == request.user:
                        messages.add_message(request, messages.ERROR, "You can't play a multiplayer game with yourself!")
                        return HttpResponseRedirect(reverse("create"))
                    g = Game(owner=request.user, opponent=u, status=2)
                    g.save()
                    return HttpResponseRedirect(f'/game/{str(g.pk)}')
                except Exception as e:
                    print(e)
                    messages.add_message(request, messages.ERROR, "The username entered does not exist.")
                    return HttpResponseRedirect(reverse("create"))
            else:
                g = Game(owner=request.user, status=1)
                g.save()
                return HttpResponseRedirect(reverse("homepage"))

@login_required
def completed(request):
    games=[]
    g = Game.objects.all().filter(Q(owner=request.user) | Q(opponent=request.user)).filter(status=3).order_by('-updated_at')
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
    return render(request, "game/completed.html", {"completed": games})

@login_required
def rules(request):
    return render(request, "webapp/rules.html")

