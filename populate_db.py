import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','GUTS.settings')

import django
django.setup()

from hackathonSystem.models import Challenge,RequestsMade,Team,User,Category,Judge,Organisation

import random

def print_bar():
    print('---------------')

def create_team(user_acc, team_name, member_details, hackerrank_accounts ):
    print('Creating a team account with the name ' + team_name)
    return Team.objects.create(
            user = user_acc,
            name = team_name,
            member_details = member_details,
            hackerrank_accounts = hackerrank_accounts
        )
    print_bar()

def create_organisation(name):
    print('Creating a organisation with the name' + name)
    
    print_bar()

    return Organisation.objects.create(
        name = name
    )

def create_judge(user_acc, organisation):
    print('Creating a judge account for the organisation ' + organisation.name)
    
    return Judge.objects.create(
        user = user_acc,
        organisation = organisation
    )

    print_bar()



def create_user(user_name, password, type_of_user = 'team'):
    print('Creating a user account with the following credentials:')
    print('username: ' + user_name)
    print('password: ' + password)

    user_object = User.objects.create_user(user_name, password=password)

    if(type_of_user == 'judge'):
        user_object.is_staff = True

    user_object.save()
    return user_object


def create_challenge(name, points, description, category):
    print('Creating challenge with the following infomration:')
    print('name: ' + name)
    print('points: ' + str(points))
    print('description: ' + description)
    print('category: ' + str(category))

    print_bar()

    return Challenge.objects.create(
        name = name,
        points_avaliable = points,
        description = description,
        category = category,
    )



def create_category(name):
    print('Creating category with the following infomration:')
    print('name: ' + name)

    print_bar()

    return Category.objects.create(
        name = name
    )


def create_request(team, challenge):
    pass


if __name__ == "__main__":
    org = create_organisation('GUTS')

    for i in range(2):
        user = create_user(f'admin_acc{i+1}', 'password', 'judge')
        judge = create_judge(user, org)


    cat = create_category("GUTS")

    for i in range(5):
        create_challenge(f'challenge-{i+1}', random.randint(1,11)*10, f'description-{i+1}',cat)

    for i in range(5):
        team_user = create_user(f'team_acc{i+1}', 'password')
        team = create_team (
            team_user,
            f'team-{i+1}',
            f'memberdetails-{i+1}',
            f'hackerrank-{i+1}'
        )
