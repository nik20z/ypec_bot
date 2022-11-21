from vkbottle.bot import MessageEvent

from bot.vk_module.handlers.config import api


def get_callback_values(event: MessageEvent, last_ind: int):
    """Получить callback_data_split и last_callback_data с ограничением по индексу"""
    callback_data_split = event.payload['cmd'].split()
    last_callback_data = ' '.join(callback_data_split[:last_ind])
    return callback_data_split, last_callback_data


def get_event_last_callback_data(event: MessageEvent, last_ind: int) -> dict:
    """"""
    callback_data_split = event.payload['cmd'].split()
    last_callback_data = ' '.join(callback_data_split[:last_ind])
    return {"cmd": last_callback_data}


async def answer_callback(event):
    """Отправить ответ на нажатие кнопки"""
    await api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id
    )
