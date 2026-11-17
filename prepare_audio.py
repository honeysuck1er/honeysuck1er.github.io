from pathlib import Path
import shutil
import subprocess
import sys


SOURCE = Path(r"D:\хонисаклер архив")
DEST = Path("audio")


ALBUMS = {
    "sad-boys-club": {
        "folder": "1) sad boys club",
        "tracks": [
            "интро.mp3",
            "додик.mp3",
            "sad boys club.mp3",
            "я хочу.mp3",
            None,  # 05 - "5 минут": файла в архиве пока нет
            "лин лин лин.mp3",
            "солевая стейси.mp3",
        ],
    },

    "slabyy-personazh": {
        "folder": "2) слабый персонаж",
        "tracks": [
            "опенинг.mp3",
            "драться!.mp3",
            "бояться.mp3",
            "слабый персонаж.mp3",
            "бич пакет.mp3",
            "молодым и злым.mp3",
            "о свободе.mp3",
            "пазла.mp3",
            "трудности.mp3",
            "воронка.mp3",
            "я не знаю.mp3",
            "искры.mp3",
            "гербарий 2.mp3",
            "прощай.mp3",
        ],
    },

    "neo-emo": {
        "folder": "3) neo emo",
        "tracks": [
            "пережить.mp3",
            "бездарность.mp3",
            "boyfriend XD.mp3",
            "сколько_.mp3",
            "вера.mp3",
        ],
    },

    "nishtyak-muzik": {
        "folder": "4) ништяк музик",
        "tracks": [
            "шмоук.mp3",
            "ништяк music.mp3",
            "хонибургер.mp3",
            "бейби ^_^.mp3",
        ],
    },

    "nishtyak-muzyka": {
        "folder": "5) ништяк музыка",
        "tracks": [
            "дуралеи.mp3",
            "ништяк музыка.mp3",
            "хонибургер 2.mp3",
            "детка 0_0.mp3",
        ],
    },

    "piterskij-albom": {
        "folder": "6) питерский альбом",
        "tracks": [
            "1) палмер.wav",
            "2) реп.wav",
            "3) факбой 2.wav",
            "4) выходной.wav",
            "5) на пати.wav",
            "6) капитал.wav",
            "7) однажды.wav",
            "8) фрагменты.wav",
            "9) факбой 2 2.wav",
        ],
    },
}


def ffmpeg_available():
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def make_mp3(source: Path, destination: Path):
    destination.parent.mkdir(parents=True, exist_ok=True)

    if source.suffix.lower() == ".mp3":
        shutil.copy2(source, destination)
        print(f"COPY    {source} -> {destination}")
        return

    print(f"CONVERT {source} -> {destination}")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-vn",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "320k",
            str(destination),
        ],
        check=True,
    )


def main():
    if not SOURCE.exists():
        print(f"ОШИБКА: не найдена папка архива: {SOURCE}")
        sys.exit(1)

    needs_ffmpeg = any(
        filename is not None and Path(filename).suffix.lower() != ".mp3"
        for album in ALBUMS.values()
        for filename in album["tracks"]
    )

    if needs_ffmpeg and not ffmpeg_available():
        print("ОШИБКА: FFmpeg не найден.")
        print("Установи его командой:")
        print("winget install Gyan.FFmpeg")
        sys.exit(1)

    copied = 0
    missing = 0

    for slug, album in ALBUMS.items():
        source_folder = SOURCE / album["folder"]

        print(f"\n=== {slug} ===")

        for number, filename in enumerate(album["tracks"], start=1):
            if filename is None:
                print(f"SKIP    {number:02d} - исходник пока отсутствует")
                missing += 1
                continue

            source = source_folder / filename
            destination = DEST / slug / f"{number:02d}.mp3"

            if not source.exists():
                print(f"MISSING {source}")
                missing += 1
                continue

            make_mp3(source, destination)
            copied += 1

    total_bytes = sum(
        path.stat().st_size
        for path in DEST.rglob("*")
        if path.is_file()
    )

    print("\n==============================")
    print(f"Готово файлов: {copied}")
    print(f"Пропущено/не найдено: {missing}")
    print(f"Размер папки audio: {total_bytes / 1024 / 1024:.2f} MB")
    print(f"Папка: {DEST.resolve()}")


if __name__ == "__main__":
    main()