from collections import defaultdict
from pytz import utc

from musicleague import app
from musicleague.persistence import get_postgres_conn
from musicleague.persistence.models import Bot
from musicleague.persistence.models import InvitedUser
from musicleague.persistence.models import League
from musicleague.persistence.models import LeaguePreferences
from musicleague.persistence.models import RankingEntry
from musicleague.persistence.models import Round
from musicleague.persistence.models import RoundStatus
from musicleague.persistence.models import ScoreboardEntry
from musicleague.persistence.models import Submission
from musicleague.persistence.models import User
from musicleague.persistence.models import Vote
from musicleague.persistence.statements import SELECT_BOT
from musicleague.persistence.statements import SELECT_INVITED_USERS_COUNT
from musicleague.persistence.statements import SELECT_INVITED_USERS_IN_LEAGUE
from musicleague.persistence.statements import SELECT_LEAGUE
from musicleague.persistence.statements import SELECT_LEAGUE_ID_FOR_ROUND
from musicleague.persistence.statements import SELECT_LEAGUE_PREFERENCES
from musicleague.persistence.statements import SELECT_LEAGUES_COUNT
from musicleague.persistence.statements import SELECT_MEMBERSHIPS_COUNT
from musicleague.persistence.statements import SELECT_MEMBERSHIPS_FOR_USER
from musicleague.persistence.statements import SELECT_MEMBERSHIPS_PLACED_FOR_USER
from musicleague.persistence.statements import SELECT_ROUND
from musicleague.persistence.statements import SELECT_ROUNDS_COUNT
from musicleague.persistence.statements import SELECT_ROUNDS_IN_LEAGUE
from musicleague.persistence.statements import SELECT_ROUNDS_IN_LEAGUE_WITH_STATUS
from musicleague.persistence.statements import SELECT_SCOREBOARD
from musicleague.persistence.statements import SELECT_SUBMISSIONS
from musicleague.persistence.statements import SELECT_SUBMISSIONS_COUNT
from musicleague.persistence.statements import SELECT_USER
from musicleague.persistence.statements import SELECT_USER_BY_EMAIL
from musicleague.persistence.statements import SELECT_USER_PREFERENCES
from musicleague.persistence.statements import SELECT_USERS_COUNT
from musicleague.persistence.statements import SELECT_USERS_IN_LEAGUE
from musicleague.persistence.statements import SELECT_VOTES
from musicleague.persistence.statements import SELECT_VOTES_COUNT


def select_bot(bot_id):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_BOT, (str(bot_id),))
                if cur.rowcount < 1:
                    return None

                access_token, refresh_token, expires_at = cur.fetchone()
                bot = Bot(id=bot_id, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at)
                return bot
    except Exception as e:
        app.logger.error('Failed SELECT_BOT', exc_info=e)


def select_user(user_id):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_USER, (str(user_id),))
                if cur.rowcount < 1:
                    return None

                email, image_url, is_admin, joined, name, profile_bg = cur.fetchone()
                u = User(user_id, email, image_url, is_admin, joined, name, profile_bg)

                # TODO This could be done in one fetch with a join
                cur.execute(SELECT_USER_PREFERENCES, (str(user_id),))
                if cur.rowcount > 0:
                    (u.preferences.owner_all_users_submitted_notifications,
                     u.preferences.owner_all_users_voted_notifications,
                     u.preferences.owner_user_left_notifications,
                     u.preferences.owner_user_submitted_notifications,
                     u.preferences.owner_user_voted_notifications,
                     u.preferences.user_added_to_league_notifications,
                     u.preferences.user_playlist_created_notifications,
                     u.preferences.user_removed_from_league_notifications,
                     u.preferences.user_submit_reminder_notifications,
                     u.preferences.user_vote_reminder_notifications) = cur.fetchone()

                return u
    except Exception as e:
        app.logger.error('Failed SELECT_USER', exc_info=e)


def select_user_by_email(user_email):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_USER_BY_EMAIL, (user_email,))
                if cur.rowcount < 1:
                    return None

                user_id, image_url, is_admin, joined, name, profile_bg = cur.fetchone()
                u = User(user_id, user_email, image_url, is_admin, joined, name, profile_bg)

                # TODO This could be done in one fetch with a join
                cur.execute(SELECT_USER_PREFERENCES, (str(user_id),))
                if cur.rowcount > 0:
                    (u.preferences.owner_all_users_submitted_notifications,
                     u.preferences.owner_all_users_voted_notifications,
                     u.preferences.owner_user_left_notifications,
                     u.preferences.owner_user_submitted_notifications,
                     u.preferences.owner_user_voted_notifications,
                     u.preferences.user_added_to_league_notifications,
                     u.preferences.user_playlist_created_notifications,
                     u.preferences.user_removed_from_league_notifications,
                     u.preferences.user_submit_reminder_notifications,
                     u.preferences.user_vote_reminder_notifications) = cur.fetchone()

                return u
    except Exception as e:
        app.logger.error('Failed SELECT_USER_BY_EMAIL', exc_info=e)


def select_users_count():
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_USERS_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.error('Failed SELECT_USERS_COUNT', exc_info=e)


def select_invited_users_count():
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_INVITED_USERS_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.error('Failed SELECT_INVITED_USERS_COUNT', exc_info=e)


def select_league(league_id, exclude_properties=None):
    if exclude_properties is None:
        exclude_properties = []

    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_LEAGUE, (str(league_id),))
                league_tup = cur.fetchone()
                l = League(
                    id=str(league_id),
                    created=league_tup[0],
                    name=league_tup[1],
                    owner_id=league_tup[2],
                    status=league_tup[3],
                )
                l.preferences = select_league_preferences(league_id)

                if 'rounds' not in exclude_properties:
                    cur.execute(SELECT_ROUNDS_IN_LEAGUE, (str(league_id),))
                    for round_tup in cur.fetchall():
                        round_id = round_tup[0]
                        r = select_round(round_id)
                        r.league = l
                        l.submission_periods.append(r)

                if 'invited_users' not in exclude_properties:
                    cur.execute(SELECT_INVITED_USERS_IN_LEAGUE, (str(league_id),))
                    for user_tup in cur.fetchall():
                        invite_id, email = user_tup
                        l.invited_users.append(InvitedUser(invite_id, email, league_id))

                cur.execute(SELECT_USERS_IN_LEAGUE, (str(league_id),))
                user_idx = {}
                round_uri_entry_idx = defaultdict(dict)
                for user_tup in cur.fetchall():
                    user_id = user_tup[0]
                    u = select_user(user_id)
                    l.users.append(u)
                    user_idx[user_id] = u
                    if user_id == l.owner_id:
                        l.owner = u

                for round in l.submission_periods:
                    if 'submissions' not in exclude_properties:
                        cur.execute(SELECT_SUBMISSIONS, (str(round.id),))
                        for submission_tup in cur.fetchall():
                            created, user_id, tracks = submission_tup
                            submitter = user_idx.get(user_id, None)
                            if submitter is None:
                                continue

                            s = Submission(user=submitter, tracks=tracks.keys(), created=created)
                            s.league = l
                            s.submission_period = round
                            round.submissions.append(s)
                            for uri, ranking in tracks.iteritems():
                                entry = ScoreboardEntry(uri=uri, submission=s, place=ranking)
                                round_uri_entry_idx[round.id][uri] = entry

                    if 'votes' not in exclude_properties:
                        cur.execute(SELECT_VOTES, (str(round.id),))
                        for vote_tup in cur.fetchall():
                            created, user_id, votes = vote_tup
                            voter = user_idx.get(user_id, None)
                            if voter is None:
                                continue

                            v = Vote(user=voter, votes=votes, created=created)
                            v.league = l
                            v.submission_period = round
                            round.votes.append(v)
                            for uri, weight in votes.iteritems():
                                # TODO Deal with case where submitter was removed from league
                                if round.id not in round_uri_entry_idx:
                                    continue

                                if uri not in round_uri_entry_idx[round.id]:
                                    continue

                                round_uri_entry_idx[round.id][uri].votes.append(v)

                if 'scoreboard' not in exclude_properties:

                    user_entry_idx = defaultdict(list)
                    for round in l.submission_periods:
                        entries_by_uri = round_uri_entry_idx[round.id]
                        for entry in entries_by_uri.values():
                            round.scoreboard.add_entry(entry, entry.place)
                            if round.is_complete:
                                user_entry_idx[entry.submission.user.id].append(entry)

                    if len(user_entry_idx):
                        cur.execute(SELECT_SCOREBOARD, (str(league_id),))
                        for scoreboard_tup in cur.fetchall():
                            user_id, rank = scoreboard_tup
                            u = user_idx.get(user_id, None)
                            le = RankingEntry(league=l, user=u, place=rank)
                            le.entries = user_entry_idx[user_id]
                            l.scoreboard.add_entry(le, rank)

                return l
    except Exception as e:
        app.logger.error('Failed SELECT_LEAGUE', exc_info=e)


def select_league_preferences(league_id):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_LEAGUE_PREFERENCES, (str(league_id),))
                if cur.rowcount < 1:
                    return None

                lp = LeaguePreferences()
                (lp.track_count, lp.point_bank_size, lp.max_points_per_song,
                 lp.downvote_bank_size, lp.max_downvotes_per_song,
                 lp.submission_reminder_time, lp.vote_reminder_time) = cur.fetchone()
                return lp
    except Exception as e:
        app.logger.error('Failed SELECT_LEAGUE_PREFERENCES', exc_info=e)


def select_leagues_for_user(user_id, exclude_properties=None):
    if exclude_properties is None:
        exclude_properties = []

    leagues = []
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_MEMBERSHIPS_FOR_USER, (str(user_id),))
                for membership_tup in cur.fetchall():
                    league_id = membership_tup[0]
                    league = select_league(league_id, exclude_properties=exclude_properties)
                    leagues.append(league)
    except Exception as e:
        app.logger.error('Failed SELECT_MEMBERSHIPS_FOR_USER', exc_info=e)

    return leagues


def select_leagues_count():
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_LEAGUES_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.error('Failed SELECT_LEAGUES_COUNT', exc_info=e)


def select_memberships_count(user_id):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_MEMBERSHIPS_COUNT, (str(user_id),))
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.error('Failed SELECT_MEMBERSHIPS_COUNT', exc_info=e)


def select_memberships_placed(user_id):
    placed = defaultdict(int)
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_MEMBERSHIPS_PLACED_FOR_USER, (str(user_id),))
                for placed_tup in cur.fetchall():
                    rank, count = placed_tup
                    placed[rank] = count
    except Exception as e:
        app.logger.error('Failed SELECT_MEMBERSHIPS_PLACED_FOR_USER', exc_info=e)

    return placed


def select_round(round_id):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_ROUND, (str(round_id),))
                round_tup = cur.fetchone()
                r = Round(
                    id=str(round_id),
                    league_id=round_tup[0],
                    created=round_tup[1],
                    description=round_tup[2],
                    name=round_tup[3],
                    playlist_url=round_tup[4],
                    submissions_due=utc.localize(round_tup[5]),
                    votes_due=utc.localize(round_tup[6]),
                )
                return r
    except Exception as e:
        app.logger.error('Failed SELECT_ROUND', exc_info=e)


def select_league_id_for_round(round_id):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_LEAGUE_ID_FOR_ROUND, (str(round_id),))
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.error('Failed SELECT_LEAGUE_ID_FOR_ROUND', exc_info=e)


def select_rounds_count():
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_ROUNDS_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.error('Failed SELECT_ROUNDS_COUNT', exc_info=e)


def select_rounds_incomplete_count(league_id):
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_ROUNDS_IN_LEAGUE_WITH_STATUS, (league_id, RoundStatus.CREATED))
                return cur.rowcount
    except Exception as e:
        app.logger.error('Failed SELECT_ROUNDS_IN_LEAGUE_WITH_STATUS', exc_info=e)

    return -1


def select_submissions_count():
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_SUBMISSIONS_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.error('Failed SELECT_SUBMISSIONS_COUNT', exc_info=e)


def select_votes_count():
    try:
        postgres_conn = get_postgres_conn()
        with postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(SELECT_VOTES_COUNT)
                return cur.fetchone()[0]
    except Exception as e:
        app.logger.error('Failed SELECT_VOTES_COUNT', exc_info=e)
