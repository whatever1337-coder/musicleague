import httplib
import json

from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for

from musicleague import app
from musicleague.notify import owner_user_voted_notification
from musicleague.notify import user_last_to_vote_notification
from musicleague.routes.decorators import login_required
from musicleague.routes.decorators import templated
from musicleague.submission import get_my_submission
from musicleague.submission_period import get_submission_period
from musicleague.submission_period.tasks import complete_submission_period
from musicleague.submission_period.tasks.cancelers import cancel_round_completion  # noqa
from musicleague.submission_period.tasks.cancelers import cancel_vote_reminders
from musicleague.vote import create_or_update_vote, get_my_vote

VOTE_URL = '/l/<league_id>/<submission_period_id>/vote/'


@app.route(VOTE_URL, methods=['GET'])
@templated('vote/page.html')
@login_required
def view_vote(league_id, submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    league = submission_period.league
    if not league.has_user(g.user):
        return redirect(url_for('view_league', league_id=league.id))

    if not submission_period.accepting_votes:
        return redirect(url_for('view_league', league_id=league.id))

    my_submission = get_my_submission(g.user, submission_period)

    # If this user didn't submit for this round, don't allow them to vote
    if not my_submission:
        return redirect(url_for('view_league', league_id=league.id))

    my_vote = get_my_vote(g.user, submission_period)

    tracks = []
    if submission_period.all_tracks:
        tracks = g.spotify.tracks(submission_period.all_tracks).get('tracks')
    tracks_by_uri = {track.get('uri'): track for track in tracks if track}

    # Remove user's own submitted songs from tracks shown on page
    if my_submission:
        for uri in my_submission.tracks:
            tracks_by_uri.pop(uri, None)

    return {
        'user': g.user,
        'league': league,
        'round': submission_period,
        'tracks_by_uri': tracks_by_uri,
        'my_vote': my_vote,
        'access_token': session['access_token'],
    }


@app.route(VOTE_URL, methods=['POST'])
@login_required
def vote(league_id, submission_period_id):
    submission_period = get_submission_period(submission_period_id)
    if not submission_period or not submission_period.league:
        return "No submission period or league", httplib.INTERNAL_SERVER_ERROR

    if not submission_period.league.has_user(g.user):
        return "Not a member of this league", httplib.UNAUTHORIZED

    # If this user didn't submit for this round, don't allow them to vote
    if g.user not in submission_period.have_submitted:
        return redirect(url_for('view_league', league_id=submission_period.league.id))

    try:
        votes = json.loads(request.form.get('votes'))
    except Exception:
        app.logger.exception("Failed to load JSON from form with votes: %s",
                             request.form)
        return 'There was an error processing your votes', 500

    # Remove all unnecessary zero-values
    votes = {k: v for k, v in votes.iteritems() if v}

    if not submission_period.accepting_votes:
        return redirect(request.referrer)

    # Process votes
    league = submission_period.league
    vote = create_or_update_vote(votes, submission_period, league, g.user)

    # If someone besides owner is submitting, notify the owner
    if g.user.id != league.owner.id:
        owner_user_voted_notification(vote)

    remaining = submission_period.have_not_voted
    if not remaining:
        complete_submission_period(submission_period.id)
        cancel_round_completion(submission_period)
        cancel_vote_reminders(submission_period)
        submission_period.save()

    elif vote.count < 2 and len(remaining) == 1:
        last_user = remaining[0]
        user_last_to_vote_notification(last_user, submission_period)

    return redirect(url_for('view_league', league_id=league_id))
