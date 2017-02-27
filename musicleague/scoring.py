from itertools import groupby

from musicleague.models import Scoreboard
from musicleague.models import ScoreboardEntry


def calculate_round_scoreboard(round):
    """ Calculate and store scoreboard on round. The scoreboard consists of
    a dict where keys are the rankings for each entry. The values for the
    scoreboard are lists of entries. In most cases, the list will have a
    length of 1; however, if two or more songs are tied, the list will grow
    in length for a particular ranking.
    """
    round.scoreboard = Scoreboard()

    # Create a ScoreboardEntry for each song with corresponding Submission
    entries = {uri: ScoreboardEntry(uri=uri, submission=submission)
               for submission in round.submissions
               for uri in submission.tracks}

    # Get Votes for each entry
    for vote in round.votes:
        for uri, points in vote.votes.iteritems():
            if points > 0:
                entries[uri].votes.append(vote)

    # Sort votes on each entry by number of points awarded
    for entry in entries.values():
        entry.votes = sorted(entry.votes,
                             key=lambda x: x.votes[entry.uri],
                             reverse=True)

    # Rank entries and assign to round scoreboard with string keys
    rankings = rank_entries(entries.values())
    for rank, entries in rankings.iteritems():
        round.scoreboard._rankings[str(rank)] = entries

    round.save()
    return round


def rank_entries(entries):
    entries = rank_by_points(entries)
    entries = rank_by_num_voters(entries)

    # Index entries by ranking
    rankings = {}
    for i, entries in enumerate(entries):
        rankings[i + 1] = entries

    return rankings


def rank_by_points(entries):
    # Rank entries by number of points
    ranked = []
    key_func = lambda x: x.points
    entries = sorted(entries, key=key_func, reverse=True)
    entries = groupby(entries, key=key_func)
    for _, group in entries:
        ranked.append(list(group))

    return ranked


def rank_by_num_voters(entries):
    # Rank entries by number of voters
    ranked = []
    for entries_for_rank in entries:
        if len(entries_for_rank) == 1:
            ranked.append(entries_for_rank)
            continue

        key_func = lambda x: len(x.votes)
        entries_for_rank = sorted(entries_for_rank, key=key_func, reverse=True)
        entries_for_rank = groupby(entries_for_rank, key=key_func)
        for _, group in entries_for_rank:
            ranked.append(list(group))

    return ranked


def calculate_league_scoreboard(league):
    pass
