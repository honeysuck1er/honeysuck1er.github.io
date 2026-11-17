from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

SOURCE_ROOT = Path(r"D:\хонисаклер архив")
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = PROJECT_ROOT / "audio" / "singles"
MANIFEST_PATH = PROJECT_ROOT / "singles_audio.json"

# Для нового релиза в будущем достаточно добавить сюда его название.
RELEASES = [
    "циклы",
    "интересно",
    "fomo",
    "hangover (x__x)",
    "2023 ^_^",
    "расскажи ^_^",
    "баллада об оппчике",
    "mlg moment",
    "егор привет",
    "не умею...",
    "ты ты ты",
    "паранойя!",
    "качели",
    "3",
]


TRACK_ORDER = {
    "баллада об оппчике": [
        "баллада об оппчике",
        "19",
        "фиолетовая фанта ^_^",
    ],
    "mlg moment": [
        "плавит",
        "nyan cat",
    ],
    "егор привет": [
        "егор привет",
        "бит егор привет чет завайбил меня ЖОСКА",
    ],
    "3": [
        "из китая",
        "gang!",
    ],
}

DISPLAY_TITLES = {
    "nyan cat (_ω_)": "nyan cat",
}

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"}

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d",
    "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
    "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
    "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "ch",
    "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
}


def slugify(text: str) -> str:
    text = text.lower().strip()
    result = []

    for char in text:
        if char in TRANSLIT:
            result.append(TRANSLIT[char])
        elif char.isascii() and char.isalnum():
            result.append(char)
        else:
            result.append("-")

    slug = "".join(result)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "track"


def normalize_name(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"^\s*\d+\s*[\)\.\-_]+\s*", "", text)
    text = re.sub(r"[^\wа-яё]+", " ", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def clean_track_title(filename: str) -> str:
    title = Path(filename).stem.strip()
    title = re.sub(r"^\s*\d+\s*[\.\)\-_ ]+\s*", "", title).strip()
    return title or Path(filename).stem


def find_release_source(title: str) -> Path | None:
    wanted = normalize_name(title)
    folder_matches = []
    file_matches = []

    for path in SOURCE_ROOT.rglob("*"):
        if path.is_dir():
            if normalize_name(path.name) == wanted:
                folder_matches.append(path)
        elif path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS:
            if normalize_name(path.stem) == wanted:
                file_matches.append(path)

    if folder_matches:
        return sorted(folder_matches, key=lambda p: len(p.parts))[0]

    if file_matches:
        return sorted(file_matches, key=lambda p: len(p.parts))[0]

    return None


def get_audio_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source]

    files = [
        path for path in source.rglob("*")
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    ]
    return sorted(files, key=lambda p: p.name.lower())


def convert_to_mp3(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    if source.suffix.lower() == ".mp3":
        shutil.copy2(source, destination)
        return

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(source),
            "-vn", "-codec:a", "libmp3lame", "-b:a", "320k",
            str(destination),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def unique_track_slug(title: str, used: set[str]) -> str:
    base = slugify(title)
    candidate = base
    counter = 2

    while candidate in used:
        candidate = f"{base}-{counter}"
        counter += 1

    used.add(candidate)
    return candidate


def prepare_release(title: str) -> dict | None:
    source = find_release_source(title)

    if source is None:
        print(f"НЕ НАЙДЕНО: {title}")
        return None

    release_slug = slugify(title)
    destination_dir = OUTPUT_ROOT / release_slug

    if destination_dir.exists():
        shutil.rmtree(destination_dir)

    destination_dir.mkdir(parents=True, exist_ok=True)
    source_files = get_audio_files(source)

    if not source_files:
        print(f"НЕТ АУДИО: {title} -> {source}")
        return None

    used_slugs = set()
    prepared_tracks = []

    for source_file in source_files:
        raw_title = clean_track_title(source_file.name)
        display_title = DISPLAY_TITLES.get(
            raw_title,
            raw_title
        )

        prepared_tracks.append({
            "source": source_file,
            "raw_title": raw_title,
            "title": display_title,
        })

    # Если в релизе один трек, его отображаемое название
    # всегда равно названию самого релиза.
    # Так "трек - хонисаклер", странные имена файлов и потерянные
    # символы не попадают на сайт.
    if len(prepared_tracks) == 1:
        prepared_tracks[0]["title"] = title

    wanted_order = TRACK_ORDER.get(title)

    if wanted_order:
        order_map = {
            normalize_name(track_title): index
            for index, track_title in enumerate(wanted_order)
        }

        prepared_tracks.sort(
            key=lambda item: order_map.get(
                normalize_name(item["title"]),
                999
            )
        )

    tracks = []

    for item in prepared_tracks:
        source_file = item["source"]
        track_title = item["title"]

        track_slug = unique_track_slug(
            track_title,
            used_slugs
        )

        destination_file = (
            destination_dir /
            f"{track_slug}.mp3"
        )

        try:
            convert_to_mp3(
                source_file,
                destination_file
            )
        except subprocess.CalledProcessError:
            print(f"ОШИБКА FFMPEG: {source_file}")
            continue

        relative_path = (
            destination_file
            .relative_to(PROJECT_ROOT)
        )

        tracks.append({
            "title": track_title,
            "file": relative_path.as_posix(),
        })

        print(
            f"  {track_title} -> "
            f"{relative_path.as_posix()}"
        )

    if not tracks:
        return None

    print(f"ГОТОВО: {title} ({len(tracks)} треков)")

    return {
        "title": title,
        "slug": release_slug,
        "tracks": tracks,
    }


def main() -> None:
    if not SOURCE_ROOT.exists():
        print(f"Не найдена исходная папка:\n{SOURCE_ROOT}")
        return

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    manifest = []

    for title in RELEASES:
        print(f"\n--- {title} ---")
        release = prepare_release(title)
        if release is not None:
            manifest.append(release)

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    total_tracks = sum(len(release["tracks"]) for release in manifest)

    print("\n==========================")
    print(f"Релизов: {len(manifest)}")
    print(f"Треков: {total_tracks}")
    print(f"Manifest: {MANIFEST_PATH}")
    print("==========================")


if __name__ == "__main__":
    main()
