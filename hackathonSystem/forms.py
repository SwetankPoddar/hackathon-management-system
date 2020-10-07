from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ClearableFileInput
from .models import Challenge, RequestsMade, Team, Judge, Category, Attachments
from django.contrib.auth.models import User

MAX_UPLOAD_FILE_SIZE = 2 * 1024 * 1024

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
    attachments = forms.FileField(widget=ClearableFileInput(attrs={'multiple': True}), required=False, label="Attachment (supports multiple)")
    class Meta:
        model = Challenge
        fields = ('name','points_avaliable','category','description')
    def __init__(self, *args, **kwargs):
        self.judge = kwargs.pop('judge',None)
        super(createChallengeForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(allowed_to_edit__in=[self.judge]) 
        addFormControlClass(self.visible_fields())
    
class createCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name','description','allowed_to_edit')

    def __init__(self, *args, **kwargs):
        super(createCategoryForm, self).__init__(*args, **kwargs)
        addFormControlClass(self.visible_fields())


class createRequestForm(forms.ModelForm):
    attachments = forms.FileField(widget=ClearableFileInput(attrs={'multiple': True}), required=False, label="Attachment (supports multiple)")
    class Meta:
        model = RequestsMade
        fields = ('challenge','notes')

    def clean(self):
        data = self.cleaned_data
        challenge = data.get('challenge')
        team = Team.objects.get(user = self.request.user)

        for f in self.request.FILES.getlist('attachments'):
            if f.size > MAX_UPLOAD_FILE_SIZE:
                self.add_error('attachments', f._get_name() + ' too large. EachSize should not exceed 2 MB.')

        if RequestsMade.objects.filter(team=team, challenge = challenge, status = "request_made").exists():
            self.add_error('challenge', 'You already have an open request for this challenge.  Please wait.')
       
        try:
            request_made = RequestsMade.objects.filter(team = team, status = 'judged', challenge = challenge).order_by('-points_gained')[:1].get()
            if challenge.points_avaliable == request_made.points_gained:
                self.add_error('challenge', 'You have already been awarded the maximum amount of points for this challenge')
        except RequestsMade.DoesNotExist:
            pass

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.selected_challenge = self.request.GET.get('challenge_id', None)
        super(createRequestForm, self).__init__(*args, **kwargs)
        self.initial['challenge'] = self.selected_challenge
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
        fields = ('name','member_details','hackerrank_accounts',)

    def __init__(self, *args, **kwargs):
        super(editTeamInformation, self).__init__(*args, **kwargs)
        addFormControlClass(self.visible_fields())


class submitHrParse(forms.Form):
    text = forms.CharField(widget=forms.Textarea, label='HR script output')
    purge = forms.BooleanField(label='Purge existing HR attempts and recreate', required=False)

