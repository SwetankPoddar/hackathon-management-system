from django.urls import path
from . import views

urlpatterns = [
    # Index Page
    path('', views.index, name='index'),

    # Login
    path('login/', views.login_request, name="login_request"),

    # Logout
    path('logout/', views.logout_request, name="logout_request"),

    # Show all challenge Page
    path('challenge_list/', views.challenge_list, name='challenge_list'),

    # More information on challenge Page
    path('challenge/<int:challenge_id>/', views.challenge_details, name='challenge_details'),

    # Open Requests List (Admin Page)
    path('request_list/', views.request_list, name='request_list'),
    
    # Create Request (User Page)
    path('create_request/', views.create_request, name="create_request"),
    
    # All Requests Made with marks and status (User Page)
    path('judged_list/', views.judged_list, name='judged_list'),

    # Detailed information about a request
    path('request/<int:request_id>/', views.request_details, name='request_details'),
    
    # Score card and team information (Admin Only)
    path('teams/', views.teams, name='teams'),

    # Create Team (Admin Only)
    path('create_team/', views.create_team, name="create_team"),

    # Create Challenge (Admin Only)
    path('create_challenge/', views.create_challenge, name="create_challenge"),

    # Close Request with marks (Admin Only)
    path('close_request/<int:requestID>/', views.close_request, name="close_request"),
    
    # Closed Requests List (Admin Only)
    path('closed_requests/', views.closed_requests, name='closed_requests'),

    # Delete Request (Admin Only)
    path('delete_request/<int:request_id>/', views.delete_request, name="delete_request"),

    # Edit Team Information (User Only)
    path('edit_information/', views.edit_information, name="edit_information"),

    # See Team Information (Admin Only)
    path('team_information/<int:user_id>/', views.team_information, name="team_information")
]
