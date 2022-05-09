from datetime import timedelta
import re

from ostrich.utils.text import get_safe_path
from pydub import AudioSegment
from pytube import YouTube


def detect_chapters(yt: YouTube) -> list[tuple[str, str]]:
    chapters = []
    # Try to get the chapters from the video description
    for line in yt.description.split("\n"):
        if re.match(r".*\d{1,2}:\d{2}.*", line):
            timestamp = re.search(r"(\d{1,2}:\d{2}(:\d{2})?)", line).group(0)
            title = line.replace(timestamp, "").strip()
            chapters.append((timestamp, title))
    return chapters


def main() -> None:
    yt = YouTube("https://www.youtube.com/watch?v=plwbd_Jk5sI")
    yt.streams.filter(progressive=True, file_extension="mp4").order_by(
        "resolution"
    ).desc().first().download(filename="video.mp4")
    chapters = detect_chapters(yt)
    audio_segment = AudioSegment.from_file("video.mp4", "mp4")
    for chapter, index in enumerate(chapters):
        timestamp = chapter[0].split(":")[::-1]
        title = chapter[1]
        start_time = timedelta(
            hours=int(timestamp[2]) if len(timestamp) == 3 else 0,
            minutes=int(timestamp[1]),
            seconds=int(timestamp[0]),
        )

        if index < len(chapters) - 1:
            next_timestamp = chapters[index + 1][0].split(":")[::-1]
            next_start_time = timedelta(
                hours=int(next_timestamp[2]) if len(next_timestamp) == 3 else 0,
                minutes=int(next_timestamp[1]),
                seconds=int(next_timestamp[0]),
            )
            chapter_segment = audio_segment[start_time.total_seconds() * 1000 :next_start_time.total_seconds() * 1000]
        else:
            chapter_segment = audio_segment[start_time.total_seconds() * 1000 :]
        chapter_segment.export(get_safe_path(f"{title}.mp3"), format="mp3")


if __name__ == "__main__":
    main()
