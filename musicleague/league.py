from datetime import datetime

from haikunator import Haikunator

from musicleague.models import InvitedUser
from musicleague.models import League
from musicleague.models import LeaguePreferences
from musicleague.notify import user_added_to_league_notification
from musicleague.notify import user_invited_to_league_notification
from musicleague.notify import user_removed_from_league_notification
from musicleague.user import get_user_by_email


def add_user(league, user_email, notify=True):
    user = get_user_by_email(user_email)
    if user and user not in league.users:
        league.users.append(user)
        league.save()

        if notify:
            user_added_to_league_notification(user, league)

    elif user is None:
        invited_user = InvitedUser(email=user_email)
        invited_user.save()
        league.invited_users.append(invited_user)
        league.save()

        if notify:
            user_invited_to_league_notification(invited_user, league)


def remove_user(league, user_id):
    remaining_users = []
    removed_user = None
    for user in league.users:
        if str(user.id) == user_id:
            removed_user = user
        else:
            remaining_users.append(user)
    league.users = remaining_users
    league.save()

    if removed_user:
        user_removed_from_league_notification(removed_user, league)


def create_league(user):
    haikunator = Haikunator()

    name = haikunator.haikunate(token_length=0)

    new_league = League(owner=user, users=[user], created=datetime.utcnow())
    new_league.preferences = LeaguePreferences(name=name)
    new_league.save()
    return new_league


def get_league(league_id):
    try:
        league = League.objects.get(id=league_id)
        return league
    except League.DoesNotExist:
        return None


def get_leagues_for_owner(user):
    try:
        leagues = League.objects(owner=user).all().order_by('-created')
        return leagues
    except League.DoesNotExist:
        return []


def get_leagues_for_user(user):
    try:
        leagues = League.objects(users=user).all().order_by('-created')
        return leagues
    except League.DoesNotExist:
        return []