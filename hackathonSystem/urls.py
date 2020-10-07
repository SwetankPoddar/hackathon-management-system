from django.urls import path
from . import views

urlpatterns = [
    # Index Page
    path('', views.index, name='index'),

    # Login
    path('login/', views.login_request, name="login_request"),

    # Logout
    path('logout/', views.logout_request, name="logout_request"),

    # Show all categories Page
    path('category-list/', views.category_list, name='category_list'),

    # Show all challenge Page
    path('challenge-list/<int:category_id>/', views.challenge_list, name='challenge_list'),

    # More information on challenge Page
    path('challenge/<int:challenge_id>/', views.challenge_details, name='challenge_details'),

    # Open Requests List (Admin Page)
    path('request-list/', views.request_list, name='request_list'),

    # Create Request (User Page)
    path('create-request/', views.create_request, name="create_request"),

    # All Requests Made with marks and status (User Page)
    path('judged-list/', views.judged_list, name='judged_list'),

    # Detailed information about a request
    path('request-details/<int:request_id>/', views.request_details, name='request_details'),

    # Score card and team information (Admin Only)
    path('teams/', views.teams, name='teams'),

    # Get HackerRank usernames for all teams (Admin Only)
    path('hr-usernames/', views.hr_usernames, name='hr_usernames'),

    # Create Team (Admin Only)
    path('create-team/', views.create_team, name="create_team"),

    # Create Challenge (Admin Only)
    path('create-challenge/', views.create_challenge, name="create_challenge"),

    # Create Challenge (Admin Only)
    path('create-category/', views.create_category, name="create_category"),


    # Close Request with marks (Admin Only)
    path('close-request/<int:requestID>/', views.close_request, name="close_request"),

    # Closed Requests List (Admin Only)
    path('closed-requests/', views.closed_requests, name='closed_requests'),

    # Delete Request (Admin Only)
    path('delete-request/<int:request_id>/', views.delete_request, name="delete_request"),

    # Edit Team Information (User Only)
    path('edit-information/', views.edit_information, name="edit_information"),

    # See Team Information (Admin Only)
    path('team-information/<int:user_id>/', views.team_information, name="team_information"),

    # Input HR scrape results (Admin Only)
    path('hr-input/', views.hr_input, name="hr-input"),
]
