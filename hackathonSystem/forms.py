from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Challenge, RequestsMade, Team, CustomUser, Category
from django.contrib.auth.models import User

### HELPER FUNCTIONS ##

def addFormControlClass(fields):
    for visible in fields:
        visible.field.widget.attrs['class'] = 'form-control'

### OVER ####

class createTeamForm(forms.ModelForm):
    # Username, password
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Team
        fields = ('name',)

    def clean(self):
        data = self.cleaned_data
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            self.add_error('username', 'Username already exists')

        p1 = data.get('password')
        p2 = data.get('confirm_password')

        if(p1 != p2):
            self.add_error('confirm_password', 'Passwords do not match.')

    def __init__(self, *args, **kwargs):
        super(createTeamForm, self).__init__(*args, **kwargs)
        addFormControlClass(self.visible_fields())

class createChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ('name','points_avaliable','category','description')

    def __init__(self, *args, **kwargs):
        super(createChallengeForm, self).__init__(*args, **kwargs)
        addFormControlClass(self.visible_fields())



class createCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(createCategoryForm, self).__init__(*args, **kwargs)
        addFormControlClass(self.visible_fields())


class createRequestForm(forms.ModelForm):

    class Meta:
        model = RequestsMade
        fields = ('challenge','notes')

    def clean(self):
        data = self.cleaned_data
        questionID = data.get('challenge')
        user = self.request.user
        userObject = CustomUser.objects.get(user = user)
        team = Team.objects.get(user = userObject)

        if RequestsMade.objects.filter(team=team, challenge = questionID, status = "request_made").exists():
            self.add_error('challenge', 'You already have an open request for this question.  Please wait.')

        self.add_error('challenge', 'We are no longer accepting any requests!')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(createRequestForm, self).__init__(*args, **kwargs)

        addFormControlClass(self.visible_fields())

class closeRequestForm(forms.ModelForm):
    class Meta:
        model = RequestsMade
        fields = ('points_gained',)

    def clean(self):
        data = self.cleaned_data
        points = data.get('points_gained')
        if(points < 0):
            self.add_error('points_gained', 'Points can\'t be negetive.')

    def __init__(self, *args, **kwargs):

        super(closeRequestForm, self).__init__(*args, **kwargs)

        challenge = kwargs.pop('instance').challenge
        self.fields['points_gained'] = forms.IntegerField(max_value=challenge.points_avaliable)

        addFormControlClass(self.visible_fields())


class customAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(customAuthenticationForm, self).__init__(*args, **kwargs)
        addFormControlClass(self.visible_fields())

class editTeamInformation(forms.ModelForm):

    class Meta:
        model = Team
        fields = ('member_details','hackerrank_accounts',)

    def __init__(self, *args, **kwargs):
        super(editTeamInformation, self).__init__(*args, **kwargs)
        addFormControlClass(self.visible_fields())
