# musician_site_static

Статическая версия сайта для GitHub Pages.

## Локальный запуск

```powershell
py -m http.server 8000
```

Открыть: `http://127.0.0.1:8000/`

## Обложки

Если в архиве нет оригинальных обложек, скопируйте их из Django-проекта:

```powershell
Copy-Item C:\Users\egorm\PycharmProjects\musician_site\media\covers\* .\images\covers\
```

До копирования вместо отсутствующей обложки показывается аккуратный placeholder, поэтому страница не ломается.
