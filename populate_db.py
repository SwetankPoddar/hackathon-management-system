import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','GUTS.settings')

import django
django.setup()

from hackathonSystem.models import Challenge,CustomUser,RequestsMade,Team,User,Category

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

def create_user(user_name, password, type_of_user):
    print('Creating an account of "' + CustomUser.USER_TYPE_CHOICES[type_of_user-1][1] + '" type... with the following credentials:')
    print('username: ' + user_name)
    print('password: ' + password)

    user_object = User.objects.create_user(user_name, password=password)
    if(type_of_user == 2):
        user_object.is_superuser = True
        user_object.is_staff = True

    user_object.save()

    customUser = CustomUser.objects.create(
        user=user_object,
        user_type=type_of_user
    )
    print_bar()
    return customUser


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

    admin_user = create_user('admin_acc2', 'password', 2)
    cat = create_category("GUTS")

    for i in range(5):
        create_challenge(f'challenge-{i+1}', random.randint(1,11)*10, f'description-{i+1}',cat)

    for i in range(5):
        team_user = create_user(f'team_acc{i+1}', 'password', 1)
        team = create_team (
            team_user,
            f'team-{i+1}',
            f'memberdetails-{i+1}',
            f'hackerrank-{i+1}'
        )
