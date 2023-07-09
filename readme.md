# Style Transfer TG Bot

Итоговый проект Deep Learning School — Телеграм-бот, который переносит стиль одного
изображения на другое.

Код для переноса стиля взят из туториала на сайте PyTorch ([ссылка](https://pytorch.org/tutorials/advanced/neural_style_tutorial.html)), в основе — модель VGG19
(веса скачиваются из репозитория PyTorch).

## Установка

1. Склонировать репозиторий.

2. Задать значение переменной окружения `TG_BOT_TOKEN` (API-ключ бота);
например, через файл .env (должен быть в директории проекта).

3. Выполнить команду `python app.py`. Бот будет запущен.

### Docker

Чтобы создать Docker-образ, необходимо выполнить (из директории проекта):

```docker build -t tg_bot .```

Чтобы создать контейнер из образа, необходимо выполнить:

```docker run --rm -d --name tg_bot tg_bot```

(образ весит более 7 GB).

В контейнере необходимо задать значение переменной окружения `TG_BOT_TOKEN`.

## Скриншоты работы TG-бота

1. Начало работы (команда `/start`):

![Начало работы](screenshots/1.png)

