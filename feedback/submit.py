from feedback.models import Submission


def create_submission(tracks, user):
    new_submission = Submission(tracks, user)
    return new_submission