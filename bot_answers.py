import requests
from collections import deque

TG_API_URL = "https://api.telegram.org"
CHATS_ORIG_IMAGES = {}
IN_PROCESS_CHATS = deque()


def __send_message(chat_id, text, token):
    return requests.post(
        f"{TG_API_URL}/bot{token}/sendmessage?chat_id={chat_id}&text={text}")


def start(chat_id, token):
    text = "Это бот для переноса стиля с одного изображения на другое. " +\
           "Для начала работы отправьте команду /transfer_style."
    __send_message(chat_id, text, token)


def pending_first_img(chat_id, token):
    text = "Прикрепите первое изображение — с которого переносим стиль."
    CHATS_ORIG_IMAGES[chat_id] = []
    __send_message(chat_id, text, token)


def pending_second_img(chat_id, token):
    text = "Прикрепите второе изображение — на которое переносим стиль."
    __send_message(chat_id, text, token)


def command_not_exist(chat_id, token):
    text = "Такой команды нет. Воспользуйтесь командой /transfer_style."
    __send_message(chat_id, text, token)


def get_dq_pos(x, dq):
    for i in range(len(dq)):
        if x == dq[i]:
            return i
    return -1


def busy(chat_id, token):
    pos = get_dq_pos(chat_id, IN_PROCESS_CHATS)
    if pos == 0:
        text = "Ваши изображения обрабатываются. Дождитесь завершения процесса."
    else:
        text = f"Ваш запрос в очереди; число запросов перед ним: {pos}. " \
               f"Результат будет отправлен в этот чат после завершения процесса."
    __send_message(chat_id, text, token)


def docs_not_allowed(chat_id, token):
    text = "Изображение необходимо прикрепить как фото, а не файл/документ."
    __send_message(chat_id, text, token)


def send_image(chat_id, file_path, token):
    files = {'photo': open(file_path, 'rb')}
    __send_message(chat_id, "Готово!", token)
    while True:
        r = requests.post(
            f"{TG_API_URL}/bot{token}/sendPhoto?chat_id={chat_id}",
            files=files
        )
        if r.json().get('ok') is True:
            break
