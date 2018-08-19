def compare_scores_to_lines(lines, scores, statuses):
    """Wrapper which analyzes score deltas and attributes them to
    the appropriate line. Returns a list of tuples, like fetch_lines, but
    adds a tuple each for each score delta.
    """
    results = lines[:]
    for index, matchup in enumerate(lines):
        # remove the home team asterisk for analysis, if necessary
        favored_team = matchup[0].replace('*', '')
        unfavored_team = matchup[1].replace('*', '')
        delta = int(scores[favored_team]) - int(scores[unfavored_team])
        results[index].append(unicode(delta))
        results[index].append('game is over' if statuses[favored_team].startswith('F') else '')

    return results


def compare_results_to_picks():
    """Logic to determine how many points to write to the Picks table.
    Null = not over
    0    = Incorrect
    0.5  = Exact Line
    1    = Correct
    """
