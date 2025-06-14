from typing import List, Tuple
from PIL import Image
import matplotlib.pyplot as plt

from models.course.model import Course
from models.score.model import Score
from io import BytesIO

from utils.formatting import par_score_format


def create_result_card_image(
    course: Course, scores: List[Tuple[str, Score]]
) -> BytesIO:

    datarows = [["Track"] + [track.track_number for track in course.tracks] + ["Total"]]
    datarows += [
        ["Par"]
        + [track.par for track in course.tracks]
        + [sum([track.par for track in course.tracks])]
    ]
    track_count = len(course.tracks)

    user_scores = {}
    for username, score in scores:
        if username not in user_scores:
            user_scores[username] = []
        user_scores[username].append(score.score_formatted)

    for user, v in user_scores.items():
        row = [user] + v + [par_score_format(sum([int(sco) for sco in v]))]
        missing = track_count - len(row)
        datarows += [row + [0] * missing]

    widest_row = max([len(row[0]) for row in datarows])
    # width in letters
    column_widths = [widest_row] + [4] * track_count + [6]

    table_size = sum(column_widths) * 0.2, (len(datarows) + 1) * 0.4

    fig, ax = plt.subplots(figsize=table_size)
    ax.axis("off")
    ax.axis("tight")
    table = ax.table(
        cellText=datarows,
        loc="center",
        cellLoc="center",
        colWidths=[w / sum(column_widths) for w in column_widths],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    # table.scale(1.2, 1.2)
    fig.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="JPEG", bbox_inches="tight")
    buf.seek(0)

    plt.close()
    return buf
