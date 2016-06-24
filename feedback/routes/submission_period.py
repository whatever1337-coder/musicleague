from datetime import datetime
from pytz import utc

from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from feedback import app
from feedback.league import get_league
from feedback.routes.decorators import league_required
from feedback.routes.decorators import login_required
from feedback.submission_period import create_submission_period
from feedback.submission_period import get_submission_period
from feedback.submission_period import remove_submission_period
from feedback.submission_period import update_submission_period


CREATE_SUBMISSION_PERIOD_URL = '/l/<league_id>/submission_period/create/'
MODIFY_SUBMISSION_PERIOD_URL = '/l/<league_id>/<submission_period_id>/modify/'  # noqa
REMOVE_SUBMISSION_PERIOD_URL = '/l/<league_id>/<submission_period_id>/remove/'  # noqa
SETTINGS_URL = '/l/<league_id>/<submission_period_id>/settings/'
VIEW_SUBMISSION_PERIOD_URL = '/l/<league_id>/<submission_period_id>/'


@app.route(CREATE_SUBMISSION_PERIOD_URL)
@login_required
@league_required
def post_create_submission_period(league_id, **kwargs):
    league = kwargs.get('league')
    if league.has_owner(g.user):
        create_submission_period(league)
    return redirect(url_for('view_league', league_id=league_id))


@app.route(REMOVE_SUBMISSION_PERIOD_URL)
@login_required
@league_required
def r_remove_submission_period(league_id, submission_period_id, **kwargs):
    league = kwargs.get('league')
    if league.has_owner(g.user):
        remove_submission_period(submission_period_id)
    return redirect(url_for('view_league', league_id=league_id))


@app.route(SETTINGS_URL, methods=['POST'])
@login_required
@league_required
def save_submission_period_settings(league_id, submission_period_id,
                                    **kwargs):
    name = request.form.get('name')

    submission_due_date_str = request.form.get('submission_due_date_utc')
    submission_due_date = utc.localize(
        datetime.strptime(submission_due_date_str, '%m/%d/%y %I%p'))

    vote_due_date_str = request.form.get('voting_due_date_utc')
    vote_due_date = utc.localize(
        datetime.strptime(vote_due_date_str, '%m/%d/%y %I%p'))

    update_submission_period(submission_period_id, name, submission_due_date,
                             vote_due_date)

    return redirect(request.referrer)


@app.route(VIEW_SUBMISSION_PERIOD_URL)
@login_required
def view_submission_period(league_id, submission_period_id):
    if submission_period_id is None:
        raise Exception(request.referrer)
        return redirect(request.referrer)
    league = get_league(league_id)
    submission_period = get_submission_period(submission_period_id)
    tracks = submission_period.all_tracks
    if tracks:
        tracks = g.spotify.tracks(submission_period.all_tracks).get('tracks')

    return render_template(
        'submission_period.html',
        user=g.user, league=league, submission_period=submission_period,
        tracks=tracks)
