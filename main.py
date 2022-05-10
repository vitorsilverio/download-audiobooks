from datetime import timedelta
from dataclasses import dataclass
import re
import subprocess

from ostrich.utils.text import get_safe_path
from pytube import YouTube

@dataclass
class Chapter:
    timestamp: str
    title: str

def extract_segment(start: str, end: str | None = None, title: str = "") -> None:
    command = [
        "ffmpeg",
        "-i",
        "video.mp4",
        "-ss",
        start,
        "-to",
        end,
        "-q:a",
        "0",
        "-map",
        "a",
        f"{get_safe_path(title)}.mp3",
    ]
    if not end:
        command.pop(5)
        command.pop(5)
    subprocess.run(command)


def detect_chapters(yt: YouTube) -> list[Chapter]:
    chapters = []
    # Try to get the chapters from the video description
    for line in yt.description.split("\n"):
        if re.match(r".*\d{1,2}:\d{2}.*", line):
            timestamp = re.search(r"(\d{1,2}:\d{2}(:\d{2})?)", line).group(0)
            title = line.replace(timestamp, "").strip()
            chapters.append(Chapter(timestamp, title))
    return chapters


def main() -> None:
    yt = YouTube("https://www.youtube.com/watch?v=plwbd_Jk5sI")
    yt.streams.filter(progressive=True, file_extension="mp4").order_by(
        "resolution"
    ).desc().first().download(filename="video.mp4")
    chapters = detect_chapters(yt)
    for index, chapter in enumerate(chapters):
        print(f"Processing chapter: {chapter}")

        if index < len(chapters) - 1:
            next_chapter = chapters[index + 1]
            extract_segment(chapter.timestamp, next_chapter.timestamp, chapter.title)
        else:
            extract_segment(chapter.timestamp, None, chapter.title)

if __name__ == "__main__":
    main()
