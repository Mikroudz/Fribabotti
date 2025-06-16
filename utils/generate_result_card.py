from typing import List, Tuple
import pandas as pd
import matplotlib.pyplot as plt

from models.course.model import Course
from models.score.model import Score
from models.track.model import Track


from models.game_session.model import GameSession
from io import BytesIO

from utils.formatting import par_score_format, datetime_to_pretty

CURRENT_TIMEZONE = "Europe/Helsinki"


def create_result_card_image(
    course: Course, scores: List[Tuple[str, Score]], game_session: GameSession
) -> BytesIO:
    """course = Course(
        tracks=[Track(track_number=i, par=2) for i in range(1, 18)], name="asd"
    )
    scores = []
    for i in range(0, 2):
        for j in range(1, 18):
            scores.append((f"user{i}", Score(track_number=j, score=3)))"""

    data_to_df = {
        "Track": {
            track.track_number: str(track.track_number) for track in course.tracks
        }
        | {9999: "Total", 10000: "+/-"}
    }

    tracks = {track.track_number: track.par for track in course.tracks}

    data_to_df["Par"] = tracks | {9999: sum([track.par for track in course.tracks])}

    totals = {}

    for username, score in scores:
        if username not in data_to_df:
            data_to_df[username] = {}
        if username not in totals:
            totals[username] = (0, 0)
        totals[username] = (
            totals[username][0] + score.score,
            totals[username][1] + tracks.get(score.track_number, 0) + score.score,
        )
        data_to_df[username][score.track_number] = score.score_formatted

    for user, total in totals.items():
        data_to_df[user][9999] = total[1]
        data_to_df[user][10000] = par_score_format(total[0])

    df = pd.DataFrame.from_dict(data_to_df, orient="index")
    df.iloc[0].apply(str)

    df = df.reindex(sorted(df.columns), axis=1)

    df = df.fillna("")

    df_with_index_as_col = df.reset_index()

    widest_row = max(df.index.astype(str).str.len()) * 0.7
    # width in letters
    column_widths = [widest_row] + [3] * (df.shape[1] - 1) + [5] + [3]

    table_size = sum(column_widths) * 0.2, (df.shape[1] + 1) * 0.35

    plt.figure(figsize=table_size, dpi=150)
    fig, ax = plt.subplots()

    fig.set_size_inches(table_size[0], table_size[1])

    plt.title(
        f"{course.name} {datetime_to_pretty(game_session.started_at, CURRENT_TIMEZONE)} - {datetime_to_pretty(game_session.ended_at, CURRENT_TIMEZONE)}"
    )
    ax.axis("off")
    ax.axis("tight")
    table = ax.table(
        cellText=df_with_index_as_col.to_numpy().tolist(),
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
