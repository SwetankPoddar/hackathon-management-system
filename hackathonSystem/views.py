from django.shortcuts import render, reverse, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout,authenticate,login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse

from .forms import createChallengeForm, createRequestForm, createTeamForm, closeRequestForm, customAuthenticationForm, editTeamInformation, createCategoryForm,AttachmentsUpload
from .models import Challenge, RequestsMade, Team, Judge, Category, Attachments

##### HELPER FUNCTIONS #####

def getTeam(request):
    try:
        return Team.objects.get(user = request.user)
    except Team.DoesNotExist:
        return None

def getJudge(request):
    try:
        return Judge.objects.get(user = request.user)
    except Judge.DoesNotExist:
        return None

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

def checkIfJudge(user):
    return not user.is_anonymous and Judge.objects.filter(user = user).exists()

def sortTeamByPoints(teamWithInformation):
    return teamWithInformation.information.points


#### VIEWS ####

def index(request):
    if request.user.is_authenticated:
        if(request.user.is_staff):
            request.session['user_type'] = 'judge'
            judge = getJudge(request)
            allowed_categories = Category.objects.filter(allowed_to_edit__in=[judge]) 
            context = {'judge': judge, 'allowed_categories': allowed_categories}
        else:
            request.session['user_type'] = 'team'
            context={'team': getTeam(request)}

        return render(request, 'index.html', context=context)
    else:
        form = customAuthenticationForm()
        return render(request, 'index.html', context={'form': form} )


@login_required
def category_list(request):
    categories = Category.objects.all()
    for category in categories:
        category.num_challenge = Challenge.objects.filter(category = category).count()
    context_dict = {'category_array': categories}
    if(request.session['user_type'] == 'team'):
        context_dict['details'] = calculateInformation(getTeam(request))

    return render(request, 'category_list.html', context=context_dict)

@login_required
def challenge_list(request, category_id):
    challenges = Challenge.objects.filter(category = category_id)
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


@user_passes_test(checkIfJudge)
def request_list(request):
    openRequests = RequestsMade.objects.filter(
        status = "request_made",
        challenge__in = Challenge.objects.filter(
            category__in = Category.objects.filter(allowed_to_edit__in=[getJudge(request)]) 
        )
    )
    context_dict = {'request_array': openRequests }
    if request.is_ajax():
        data = {'rendered_table': render_to_string('table_content.html', context=context_dict)}
        return JsonResponse(data)
    return render(request, 'request_list.html', context=context_dict)

@user_passes_test(checkIfJudge)
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
    if(checkIfJudge(request.user)):
        requestInfo = RequestsMade.objects.get(id = request_id)
    else:
        team = getTeam(request)
        requestInfo = RequestsMade.objects.get(team = team, id = request_id)
    context_dict = {'requestInfo': requestInfo}
    return render(request, 'request.html', context=context_dict)

@user_passes_test(checkIfJudge)
def delete_request(request, request_id):
    RequestsMade.objects.filter(id = request_id).delete()
    return redirect(reverse('closed_requests'))

@user_passes_test(checkIfJudge)
def closed_requests(request):
    closedRequests = RequestsMade.objects.filter(status = 'judged').order_by('-made_at')
    paginator = Paginator(closedRequests, 30)
    page = request.GET.get('page')
    closedRequests = paginator.get_page(page)
    return render(request, 'closed_requests.html',{'requests': closedRequests})

@user_passes_test(checkIfJudge)
def team_information(request, user_id):
    team = Team.objects.get(user = User.objects.get(id = user_id))
    teamScore = calculateInformation(team)
    return render(request, 'team_information.html',{'team':team, 'details':teamScore})

##### FORM VIEWS  #####
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
    return render(request, 'form_template.html', context={'form': teamInformation,'col_size':'8'})


@login_required
def create_request(request):
    newRequest = createRequestForm(request.POST or None, request = request)
    attachments = AttachmentsUpload(request.POST or None, request.FILES or None)
    if newRequest.is_valid():
        newRequest = newRequest.save(commit = False)
        newRequest.team = getTeam(request)
        newRequest.save()
        return redirect(reverse("judged_list"))

    newRequest.action = str(reverse('create_request'))
    newRequest.formFor = 'Create Request'
    return render(request, 'form_template.html', context={'form': newRequest})


@login_required
def create_category(request):
    newCategory = createCategoryForm(request.POST or None)
    if (request.method == 'POST'):
        if newCategory.is_valid():
            cat = newCategory.save()
            messages.success(request, 'Category successfully created')

    newCategory.action = str(reverse('create_category'))
    newCategory.formFor = 'Create Category'
    return render(request, 'form_template.html', context={'form': newCategory})

@user_passes_test(checkIfJudge)
def create_challenge(request):
    newChallenge = createChallengeForm(request.POST or None, request.FILES or None, judge=getJudge(request))
    if request.method == "POST" and newChallenge.is_valid():
        newChallenge = newChallenge.save()
        print(request.FILES.getlist('attachments'))
        files = request.FILES.getlist('attachments')
        for f in files:
            file_instance = Attachments(attachment=f)
            file_instance.save()
            newChallenge.attachments.add(file_instance)
        return redirect(reverse("challenge_details",kwargs={'challenge_id': newChallenge.id}))

    newChallenge.action = str(reverse('create_challenge'))
    newChallenge.formFor = 'Create Challenge'
    return render(request, 'form_template_challenge.html', context={'form': newChallenge})

@user_passes_test(checkIfJudge)
def create_team(request):
    createTeamRequest = createTeamForm(request.POST or None)

    if(request.method == "POST"):
        if createTeamRequest.is_valid():
            username = createTeamRequest.cleaned_data["username"]
            password = createTeamRequest.cleaned_data["password"]
            team_name = createTeamRequest.cleaned_data["name"]
            # Create new user account
            user = User.objects.create_user(username=username, password=password)
            team = Team.objects.create(user = user, name = team_name)

            messages.success(request, 'Team successfully created')
            return redirect(reverse('create_team'))

    form = createTeamRequest
    form.action = str(reverse('create_team'))
    form.formFor = 'Create Team'
    return render(request, 'form_template.html', context={'form': form,'col_size':'4'})

@user_passes_test(checkIfJudge)
def close_request(request, requestID):
    try:
        requestInstance = RequestsMade.objects.get(
            id = requestID,
            status = 'request_made',
            challenge__in = Challenge.objects.filter(
                category__in = Category.objects.filter(allowed_to_edit__in=[getJudge(request)]) 
            )
        )
    except RequestsMade.DoesNotExist:
        return redirect(reverse('index'))

    if(request.method == "POST"):

        closeRequest = closeRequestForm(request.POST, instance = requestInstance)

        if(closeRequest.is_valid()):
            closeRequest = closeRequest.save(commit = False)
            closeRequest.status = "judged"
            closeRequest.closed_by = Judge.objects.get(user = request.user)
            closeRequest.save()

            return redirect(reverse('request_list'))
        else:
            return redirect(reverse('close_request',kwargs={'requestID': requestID}))

    else:
        form = closeRequestForm(instance=requestInstance)

        return render(request, 'close_request.html', context={'form': form, 'requestDetails': requestInstance})
