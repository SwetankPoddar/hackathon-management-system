from django.shortcuts import render, reverse, redirect
from .models import Challenge, RequestsMade, Team, CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout,authenticate,login
from django.contrib.auth.decorators import user_passes_test
from .forms import createChallengeForm, createRequestForm, createTeamForm, closeRequestForm, customAuthenticationForm, editTeamInformation
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse

##### HELPER FUNCTIONS #####

def getTeam(request):

    userModel = CustomUser.objects.get(user = request.user)

    if(userModel.isAdmin()):
        return None

    team = Team.objects.get(user = userModel)
    return team

def calculateInformation(team):
    challenges = Challenge.objects.all()

    fully_completed = 0
    partially_completed = 0
    total_points = 0

    # Get request with max point for each question
    for challenge in challenges:
        try:
            request = RequestsMade.objects.filter(team = team, status = 'judged', challenge = challenge).order_by('-points_gained')[:1].get()
            if challenge.points_avaliable == request.points_gained:
                fully_completed +=1
            else:
                partially_completed += 1

            total_points += request.points_gained
        except RequestsMade.DoesNotExist:
            pass

    details = {'points': total_points, 'challenges_completed': fully_completed, 'partially_completed': partially_completed }

    return details


def checkIfAdmin(user):
    userModel = CustomUser.objects.get(user = user)
    return userModel.isAdmin()

def sortTeamByPoints(teamWithInformation):
    return teamWithInformation.information.points


#### VIEWS ####

def index(request):
    if request.user.is_authenticated:
        userModel = CustomUser.objects.get(user = request.user)
        if(userModel.isAdmin()):
            request.session['user_type'] = 'admin'
            context = {}
        else:
            request.session['user_type'] = 'team'
            team = Team.objects.get(user = userModel)
            context={'team': team}

        return render(request, 'index.html', context=context)

    else:
        form = customAuthenticationForm()
        return render(request, 'index.html', context={'form': form} )

@login_required
def challenge_list(request):
    challenges = Challenge.objects.all()
    team = getTeam(request)
    details = calculateInformation(team)
    if team:
        for challenge in challenges:
            try:
                requestMade = RequestsMade.objects.filter(team = team, challenge = challenge).order_by('-made_at')[:1].get()
                challenge.status = requestMade.get_status_display()
            except RequestsMade.DoesNotExist:
                challenge.status = "Not attempted yet"

    context_dict={'challenge_array': challenges, 'details': details}

    return render(request, 'challenge_list.html', context=context_dict)

@login_required
def challenge_details(request,challenge_id):
    challenge = Challenge.objects.get(id = challenge_id)
    team = getTeam(request)

    request_with_most_points = RequestsMade.objects.filter(team = team, challenge = challenge).order_by('-points_gained').values()

    if(len(request_with_most_points) == 0):
        points_gained = 0
        status = "No attempt found"
        request_id = None

    if(len(request_with_most_points) >= 1):
        request_with_most_points = request_with_most_points[0]
        openRequests = RequestsMade.objects.filter(team = team, challenge = challenge, status = "request_made").values()

        if(len(openRequests) == 1):
            status = "Request Made"
            request_id = openRequests[0]['id']
        else:
            status = "Judged"
            request_id = request_with_most_points['id']
        points_gained = request_with_most_points['points_gained']


    if(len(request_with_most_points) == 0):
        status = "Not attempted yet"

    return render(request, 'challenge.html', context={'challenge': challenge, 'points_gained':points_gained, 'status':status, 'request_id': request_id })

@login_required
def judged_list(request):
    team = getTeam(request)
    judgments = RequestsMade.objects.filter(team = team).order_by('-status')
    context_dict = {'judgement_array': judgments}
    return render(request, 'judged_list.html', context=context_dict)


@user_passes_test(checkIfAdmin)
def request_list(request):
    openRequests = RequestsMade.objects.filter(status = "request_made")
    context_dict = {'request_array': openRequests }
    if request.is_ajax():
        data = {'rendered_table': render_to_string('hackathonSystem/table_content.html', context=context_dict)}
        return JsonResponse(data)
    return render(request, 'request_list.html', context=context_dict)

@user_passes_test(checkIfAdmin)
def teams(request):
    allTeams = Team.objects.all()

    for team in allTeams:
        team.information = calculateInformation(team)

    #allTeams.sort(key = sortTeamByPoints)

    context_dict={'team_array':allTeams}
    return render(request, 'teams.html', context=context_dict)


def logout_request(request):
    logout(request)
    return redirect(reverse('index'))

def login_request(request):
    if(request.method == "POST"):
        form = customAuthenticationForm(request, data = request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request,user)
    return redirect(reverse("index"))

@login_required
def request_details(request, request_id):
    if(checkIfAdmin(request.user)):
        requestInfo = RequestsMade.objects.get(id = request_id)
    else:
        team = getTeam(request)
        requestInfo = RequestsMade.objects.get(team = team, id = request_id)
    context_dict = {'requestInfo': requestInfo}
    return render(request, 'request.html', context=context_dict)

@user_passes_test(checkIfAdmin)
def delete_request(request, request_id):
    RequestsMade.objects.filter(id = request_id).delete()
    return redirect(reverse('closed_requests'))

@user_passes_test(checkIfAdmin)
def closed_requests(request):
    closedRequests = RequestsMade.objects.filter(status = 'judged').order_by('-made_at')
    paginator = Paginator(closedRequests, 30)
    page = request.GET.get('page')
    closedRequests = paginator.get_page(page)
    return render(request, 'closed_requests.html',{'requests': closedRequests})

@user_passes_test(checkIfAdmin)
def team_information(request, user_id):
    customUser = CustomUser.objects.get(id = user_id)
    team = Team.objects.get(user = customUser)
    teamScore = calculateInformation(team)
    return render(request, 'team_information.html',{'team':team, 'details':teamScore})

##### FORMS  #####
@login_required
def edit_information(request):
    team = getTeam(request)

    teamInformation = editTeamInformation(request.POST or None, instance=team)
    if(request.method == "POST"):
        if teamInformation.is_valid():
            teamInformation.save()
            return redirect(reverse('edit_information'))

    teamInformation.action = str(reverse('edit_information'))

    teamInformation.formFor = "Edit Team Information"

    return render(request, 'form_template_slim.html', context={'form': teamInformation})


@login_required
def create_request(request):

    newRequest = createRequestForm(request.POST or None, request = request)

    if(request.method == "POST"):
        if newRequest.is_valid():
            newRequest = newRequest.save(commit = False)
            newRequest.team = getTeam(request)
            newRequest.save()
            return redirect(reverse("judged_list"))

    newRequest.action = str(reverse('create_request'))
    newRequest.formFor = 'Create Request'
    return render(request, 'form_template.html', context={'form': newRequest})

@user_passes_test(checkIfAdmin)
def create_challenge(request):

    newChallenge = createChallengeForm(request.POST or None)

    if(request.method == "POST"):
        if newChallenge.is_valid():
            newChallenge = newChallenge.save()
            return redirect(reverse("challenge_details",kwargs={'challenge_id': newChallenge.id}))

    newChallenge.action = str(reverse('create_challenge'))
    newChallenge.formFor = 'Create Challenge'
    return render(request, 'form_template.html', context={'form': newChallenge})

@user_passes_test(checkIfAdmin)
def create_team(request):
    createTeamRequest = createTeamForm(request.POST or None)

    if(request.method == "POST"):
        if createTeamRequest.is_valid():
            username = createTeamRequest.cleaned_data["username"]
            password = createTeamRequest.cleaned_data["password"]
            # Create new user account

            user = User.objects.create_user(username, 'notRequired@lol.com', password)
            user = CustomUser.objects.create(user = user, user_type = 1)

            createTeamRequest = createTeamRequest.save(commit = False)
            createTeamRequest.user = user
            createTeamRequest.save()
            messages.success(request, 'Team sucesfully created')
            return redirect(reverse('create_team'))

    form = createTeamRequest
    form.action = str(reverse('create_team'))
    form.formFor = 'Create Team'
    return render(request, 'form_template_slim.html', context={'form': form})

@user_passes_test(checkIfAdmin)
def close_request(request, requestID):
    try:
        requestInstance = RequestsMade.objects.get(id = requestID, status = 'request_made')

    except RequestsMade.DoesNotExist:
        print('Invalid ID ' + str(requestID))
        return redirect(reverse('index'))

    if(request.method == "POST"):

        closeRequest = closeRequestForm(request.POST, instance = requestInstance)

        if(closeRequest.is_valid()):
            closeRequest = closeRequest.save(commit = False)
            closeRequest.status = "judged"
            closeRequest.closed_by = CustomUser.objects.get(user = request.user)
            closeRequest.save()

            return redirect(reverse('request_list'))
        else:
            return redirect(reverse('close_request',kwargs={'requestID': requestID}))

    else:
        form = closeRequestForm(instance=requestInstance)

        return render(request, 'close_request.html', context={'form': form, 'requestDetails': requestInstance})
