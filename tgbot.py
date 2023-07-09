import os
from threading import Thread
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from nn_style_transfer import get_vgg19, style_transfer as nn_process
import bot_answers as ans

load_dotenv()
TG_TOKEN = os.getenv("TG_BOT_TOKEN")

TG_API_URL = ans.TG_API_URL
CHATS_ORIG_IMAGES = ans.CHATS_ORIG_IMAGES
IN_PROCESS_CHATS = ans.IN_PROCESS_CHATS
TRAINING_INFO_LAST_ID = ans.TRAINING_INFO_LAST_ID

ANSWERS = {
    'start': lambda x: ans.start(x, token=TG_TOKEN),
    'transfer_style': lambda chat_id:
        ans.pending_first_img(chat_id, token=TG_TOKEN),
    ('busy', ): lambda chat_id:
        ans.busy(chat_id, token=TG_TOKEN),
    ('pending_1st_img', ): lambda chat_id:
        ans.pending_first_img(chat_id, token=TG_TOKEN),
    ('pending_2nd_img', ): lambda chat_id:
        ans.pending_second_img(chat_id, token=TG_TOKEN),
    ('docs_not_allowed', ): lambda chat_id:
        ans.docs_not_allowed(chat_id, token=TG_TOKEN),
    ('send_image', ): lambda chat_id, file_path:
        ans.send_image(chat_id, file_path, token=TG_TOKEN),
    ('send_training_info', ): lambda chat_id, info:
        ans.send_training_info(chat_id, info, token=TG_TOKEN),
    None: lambda x: ans.command_not_exist(x, token=TG_TOKEN),
}


def process_command(message):
    command = message['text'].split()[0][1:]
    chat_id = message['chat']['id']
    if chat_id in CHATS_ORIG_IMAGES:
        del CHATS_ORIG_IMAGES[chat_id]
    if command in ANSWERS:
        ANSWERS[command](chat_id)
    else:
        ANSWERS[None](chat_id)


def process_message(message):
    chat_id = message['chat']['id']
    if chat_id in CHATS_ORIG_IMAGES:
        if 'photo' in message:
            CHATS_ORIG_IMAGES[chat_id].append(message['photo'][-1])
        elif 'document' in message:
            ANSWERS[('docs_not_allowed', )](chat_id)
        if len(CHATS_ORIG_IMAGES[chat_id]) == 0:
            ANSWERS[('pending_1st_img', )](chat_id)
        elif len(CHATS_ORIG_IMAGES[chat_id]) == 1:
            ANSWERS[('pending_2nd_img',)](chat_id)
        else:
            transfer_style(chat_id)
    else:
        ANSWERS[None](chat_id)


def process_update(update):
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        if chat_id in IN_PROCESS_CHATS:
            ANSWERS[('busy', )](chat_id)
        elif 'entities' in update['message'] \
                and update['message']['entities'][0]['type'] == 'bot_command':
            process_command(update['message'])
        else:
            process_message(update['message'])


def __mkdir(path):
    """Создает директорию, если не существует."""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_image(image_info):
    file_id = image_info['file_id']
    r = requests.get(
        f"{TG_API_URL}/bot{TG_TOKEN}/getFile",
        data={'file_id': file_id}
    ).json()
    file_path = r['result']['file_path']
    r_file = requests.get(f"{TG_API_URL}/file/bot{TG_TOKEN}/{file_path}")
    __mkdir("tmp")
    filename = f"tmp/{time.time()}.jpg"
    with open(filename, "wb") as f:
        for chunk in r_file.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return filename


def transfer_style(chat_id):
    IN_PROCESS_CHATS.append(chat_id)
    ANSWERS[('busy', )](chat_id)
    while IN_PROCESS_CHATS[0] != chat_id:
        time.sleep(1)
    style_img_path = get_image(CHATS_ORIG_IMAGES[chat_id][0])
    content_img_path = get_image(CHATS_ORIG_IMAGES[chat_id][1])
    output_file_path = f"./tmp/{time.time()}.jpg"
    log_func = lambda info: ANSWERS[('send_training_info', )](chat_id, info)
    nn_process(
        content_img_path=content_img_path,
        style_img_path=style_img_path,
        output_file_path=output_file_path,
        log_func=log_func
    )
    ANSWERS[('send_image', )](chat_id, output_file_path)
    # for path in [style_img_path, content_img_path, output_file_path]:
    #     os.remove(path)
    del CHATS_ORIG_IMAGES[chat_id]
    TRAINING_INFO_LAST_ID[0] = None
    IN_PROCESS_CHATS.popleft()


def main():
    offset = 0
    while True:
        updates = requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/getUpdates',
            data={'offset': offset + 1}
        ).json().get('result')
        if updates is not None:
            offset = updates[-1]['update_id'] if len(updates) > 0 else 0
            for update in updates:
                Thread(target=process_update, args=(update,),
                       daemon=True).start()
        else:
            print("Can not get updates!")
            time.sleep(1)


if __name__ == '__main__':
    get_vgg19()  # Скачает веса, если не скачаны
    main()
