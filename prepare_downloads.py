from pathlib import Path
import re
import zipfile


AUDIO = Path("audio")
DOWNLOADS = Path("downloads")


TRACKS = {
    "piterskij-albom": [
        "палмер",
        "реп",
        "факбой 2",
        "выходной",
        "на пати",
        "капитал",
        "однажды",
        "фрагменты",
        "факбой 2 2",
    ],

    "nishtyak-muzyka": [
        "дуралеи",
        "ништяк музыка",
        "хонибургер 2",
        "детка 0_0",
    ],

    "nishtyak-muzik": [
        "шмоук",
        "ништяк music",
        "хонибургер",
        "бейби ^_^",
    ],

    "neo-emo": [
        "пережить",
        "бездарность",
        "boyfriend XD",
        "сколько?",
        "вера",
    ],

    "slabyy-personazh": [
        "опенинг",
        "драться!",
        "бояться",
        "слабый персонаж",
        "бич пакет",
        "молодым и злым",
        "о свободе",
        "пазла",
        "трудности",
        "воронка",
        "я не знаю",
        "искры",
        "гербарий 2",
        "прощай",
    ],

    "sad-boys-club": [
        "интро",
        "додик",
        "sad boys club",
        "я хочу",
        "5 минут",
        "лин лин лин",
        "солевая стейси",
    ],
}


def safe_filename(name):
    # Символы, которые Windows не разрешает в именах файлов.
    return re.sub(r'[<>:"/\\\\|?*]', "", name).strip()


def make_album_zip(album_slug, titles):
    album_dir = AUDIO / album_slug

    if not album_dir.exists():
        print(f"нет папки: {album_dir}")
        return False

    zip_path = DOWNLOADS / f"{album_slug}.zip"

    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED
    ) as archive:

        for number, title in enumerate(titles, start=1):
            source = album_dir / f"{number:02d}.mp3"

            if not source.exists():
                print(f"нет файла: {source}")
                continue

            clean_title = safe_filename(title)

            archive_name = (
                f"{number:02d} - {clean_title}.mp3"
            )

            archive.write(
                source,
                arcname=archive_name
            )

    print(f"готово: {zip_path}")
    return True


def main():
    if not AUDIO.exists():
        print("Папка audio не найдена.")
        return

    DOWNLOADS.mkdir(exist_ok=True)

    created = 0

    for album_slug, titles in TRACKS.items():
        if make_album_zip(album_slug, titles):
            created += 1

    print(f"\nСоздано архивов: {created}")


if __name__ == "__main__":
    main()
