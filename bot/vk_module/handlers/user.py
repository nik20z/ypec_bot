import asyncio
from datetime import datetime
from io import BytesIO
from typing import Union, Any

from vkbottle import BaseStateGroup
from vkbottle import GroupEventType
from vkbottle import CtxStorage
from vkbottle import DocMessagesUploader
from vkbottle.bot import BotLabeler, Message, MessageEvent
from vkbottle.dispatch.rules.base import CommandRule

# My Modules
from bot.vk_module import answers
from bot.vk_module.functions import get_user_name
from bot.vk_module.handlers.config import api
from bot.vk_module.handlers.config import state_dispenser
from bot.vk_module.handlers.functions import get_callback_values
from bot.vk_module.handlers.functions import get_event_last_callback_data
from bot.vk_module.handlers.functions import answer_callback
from bot.vk_module.keyboards import Inline
from bot.vk_module.keyboards import Reply
from bot.vk_module.rules import CheckNewUser
from bot.vk_module.rules import CheckPayload
from bot.vk_module.rules import CheckState

from bot.database import Insert
from bot.database import Update
from bot.database import Select

from bot.functions import column_name_by_callback
from bot.functions import get_week_day_name_by_id
from bot.functions import month_translate

from bot.message_timetable import MessageTimetable

from bot.vk_module.config import ADMINS_VK
from bot.vk_module.config import DEFAULT_LIMIT_SUBSCRIPTIONS

# from bot.misc import Keys


user_labeler = BotLabeler()
user_labeler.vbml_ignore_case = True
# chat_labeler.auto_rules = [rules.PeerRule(f=True), ChatInfoRule()]

ctx_user_storage = CtxStorage()

AnswerText = answers.Text
AnswerCallback = answers.Callback


class UserStates(BaseStateGroup):
    """Класс состояний пользователя"""
    choice_type_name = "choice_type_name"
    choice_name = "choice_name"


@user_labeler.message(CheckNewUser())
async def new_user(message: Message) -> None:
    """Обработчик для нового пользователя"""
    user_id = message.peer_id
    joined = datetime.utcfromtimestamp(message.date)

    [first_name, last_name, user_name] = get_user_name(user_id)

    if user_id > 0:
        text = AnswerText.welcome_message_private(first_name)
    else:
        text = AnswerText.welcome_message_group(first_name)

    new_user_data = (user_id, user_name, joined)
    Insert.new_user("vkontakte", new_user_data)

    # logger.info(f"message {user_id} {user_name}")

    ctx_user_storage.set(user_id, 'new_user')
    await choice_type_name(message, text=text)


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["g_list"]),
                        CheckState('choice_type_name'))
async def choice_group__name(event: MessageEvent) -> None:
    """Выбор группы из списка для нового пользователя"""
    user_id = event.object.user_id

    Update.user_settings(user_id, "type_name", "True", table_name="vkontakte")
    group__names_array = Select.group_(grouping=False)

    text = AnswerText.choice_name("group_")
    keyboard = Inline.names_list(group__names_array,
                                 offset=7,
                                 short_type_name='g',
                                 row_width=3)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    await state_dispenser.set(user_id, UserStates.choice_name)
    # logger.info(f"callback {user_id}")'''


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["g_list"], ind=-2),
                        CheckState('choice_name'))
async def paging_group__list_state(event: MessageEvent) -> None:
    """Обработчик листания списка групп для новых пользователей"""
    await paging_group__list(event)


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["g_list"], ind=-2))
async def paging_group__list(event: MessageEvent, last_ind: int = -2) -> None:
    """Обработчик листания списка групп"""
    user_id = event.object.peer_id
    last_callback_data = get_callback_values(event, last_ind)[-1]
    start_ = int(event.payload['cmd'].split()[-1])

    group__names_array = Select.group_(grouping=False)
    add_back_button = ctx_user_storage.get(user_id) != 'new_user'

    text = AnswerText.choice_name("group_")
    keyboard = Inline.names_list(group__names_array,
                                 offset=7,
                                 start_=start_,
                                 short_type_name='g',
                                 row_width=3,
                                 add_back_button=add_back_button,
                                 last_callback_data=last_callback_data)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id} {start_}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["t_list"]),
                        CheckState('choice_type_name'))
async def choice_teacher_name(event: MessageEvent) -> None:
    """Выбор преподавателя из списка для нового пользователя"""
    user_id = event.object.user_id

    Update.user_settings(user_id, "type_name", "False", table_name="vkontakte")
    teacher_names_array = Select.teacher()

    text = AnswerText.choice_name("teacher")
    keyboard = Inline.names_list(teacher_names_array,
                                 offset=5,
                                 short_type_name='t',
                                 row_width=1)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    await state_dispenser.set(user_id, UserStates.choice_name)
    # logger.info(f"callback {user_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["t_list"], ind=-2),
                        CheckState('choice_name'))
async def paging_teacher_list_state(event: MessageEvent) -> None:
    """Обработчик листания списка преподавателей для новых пользователей"""
    await paging_teacher_list(event)


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["t_list"], ind=-2))
async def paging_teacher_list(event: MessageEvent, last_ind: int = -2) -> None:
    """Обработчик листания списка преподавателей"""
    user_id = event.object.peer_id
    last_callback_data = get_callback_values(event, last_ind)[-1]
    start_ = int(event.payload['cmd'].split()[-1])

    teacher_names_array = Select.teacher()
    add_back_button = ctx_user_storage.get(user_id) != 'new_user'

    text = AnswerText.choice_name("teacher")
    keyboard = Inline.names_list(teacher_names_array,
                                 offset=3,
                                 start_=start_,
                                 short_type_name='t',
                                 row_width=1,
                                 add_back_button=add_back_button,
                                 last_callback_data=last_callback_data)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id} {start_}")


@user_labeler.message(state=UserStates.choice_type_name)
async def error_choice_type_name_message(message: Message) -> None:
    """Обработчик левых сообщений при выборе профиля"""
    user_id = message.peer_id
    await message.answer(AnswerText.errors("choice_type_name"))
    # logger.info(f"message {user_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["gc"], ind=-2),
                        CheckState('choice_name'))
async def choice_group_(event: MessageEvent) -> None:
    """Обработчик выбора группы для нового пользователя"""
    user_id = event.object.peer_id
    type_name = "group_"
    group__id = str(event.payload['cmd'].split()[-1])
    group__name = Select.name_by_id(type_name, group__id)

    Update.user_settings(user_id, "name_id", group__id, table_name="vkontakte")
    # Update.user_settings_array(user_id, table_name="vkontakte", name_=type_name, value=group__id, remove_=None)
    # Update.user_settings_array(user_id, table_name="vkontakte", name_="spam_group_", value=group__id, remove_=None)

    date_ = Select.fresh_ready_timetable_date(type_name=type_name, name_id=int(group__id))
    date_str = date_.strftime("%d.%m.%Y")
    data_ready_timetable = Select.ready_timetable(type_name, date_, group__name)

    text = MessageTimetable(group__name,
                            date_str,
                            data_ready_timetable,
                            format_=False).get()

    keyboard = Reply.default()

    # await event.show_snackbar(AnswerCallback.new_user("choice_group__name_finish", group__name))

    '''
    message_id = event.conversation_message_id
    group_id = Keys.VK_BOT_ID
    await api.messages.delete(peer_id=user_id,
                              message_ids=message_id,
                              delete_for_all=True,
                              group_id=group_id)
    '''

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    user_state_data = ctx_user_storage.get(user_id)
    await state_dispenser.delete(user_id)
    ctx_user_storage.delete(user_id)

    # logger.info(f"callback {user_id} {group__name} {group__id}")

    if "new_user" in user_state_data:
        await asyncio.sleep(2)
        await help_message(event.object)


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["tc"], ind=-2),
                        CheckState('choice_name'))
async def choice_teacher(event: MessageEvent) -> None:
    """Выбор преподавателя для нового пользователя"""
    user_id = event.object.peer_id
    type_name = "teacher"
    teacher_id = event.payload['cmd'].split()[-1]
    teacher_name = Select.name_by_id(type_name, teacher_id)

    Update.user_settings(user_id, "name_id", teacher_id, table_name="vkontakte")
    # Update.user_settings_array(user_id, table_name="vkontakte", name_=type_name, value=teacher_id, remove_=None)
    # Update.user_settings_array(user_id, table_name="vkontakte", name_="spam_teacher", value=teacher_id, remove_=None)

    date_ = Select.fresh_ready_timetable_date(type_name=type_name, name_id=int(teacher_id))
    date_str = date_.strftime("%d.%m.%Y")
    data_ready_timetable = Select.ready_timetable(type_name, date_, teacher_name)

    text = MessageTimetable(teacher_name,
                            date_str,
                            data_ready_timetable,
                            format_=False).get()
    keyboard = Reply.default()

    # await event.show_snackbar(AnswerCallback.new_user("choice_teacher_name_finish", teacher_name))

    # await callback.message.delete()
    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    user_state_data = ctx_user_storage.get(user_id)
    await state_dispenser.delete(user_id)
    ctx_user_storage.delete(user_id)

    # logger.info(f"callback {user_id} {teacher_name} {teacher_id}")

    if "new_user" in user_state_data:
        await asyncio.sleep(2)
        await help_message(event.object)


@user_labeler.message(state=UserStates.choice_name)
async def error_choice_name_message(message: Message) -> None:
    """Обработчик левых сообщений при выборе группы/преподавателя"""
    user_id = message.peer_id
    await message.answer(AnswerText.errors("choice_name"))
    # logger.info(f"message {user_id}")


@user_labeler.message(CommandRule("start", ["!", "/"], 0))
async def choice_type_name(message: Message, text: str = None) -> None:
    """Выбор типа профиля"""
    user_id = message.peer_id

    if text is None:
        text = AnswerText.choice_type_name()
    keyboard = Inline.type_names()

    await message.answer(text, keyboard=keyboard)
    await state_dispenser.set(user_id, UserStates.choice_type_name)
    # logger.info(f"message {user_id}")


@user_labeler.message(CommandRule("Расписание", [""], 0))
async def timetable(message: Message,
                    event: MessageEvent = None,
                    last_callback_data: str = "",
                    paging: bool = False,
                    type_name: str = None,
                    name_id: int = None,
                    date_: str = None,
                    add_back_button: bool = False
                    ) -> Union[None, Any]:
    """Обработчик запроса на получение Расписания"""
    user_id = message.peer_id

    user_info = Select.user_info_by_column_names(user_id, table_name="vkontakte")

    if not paging:
        """Выводим обычное расписание расписание"""
        type_name = user_info[0]
        name_id = user_info[1]

    view_name = user_info[2]
    # view_week_day = user_info[3]
    view_add = user_info[4]
    view_time = user_info[5]
    # view_dpo_info = user_info[6]

    if type_name is None or name_id is None:
        """У пользователя нет основной подписки"""
        # logger.info(f"message {user_id} {None} {name_id}")
        return await message.answer(AnswerText.no_main_subscription())

    name_ = Select.name_by_id(type_name, str(name_id))

    dates_array = Select.dates_ready_timetable(type_name=type_name,
                                               name_id=name_id,
                                               type_date='string',
                                               type_sort='ASC')

    if date_ == 'empty':
        """Если при листании упёрлись в конец списка, то выводим сообщение об отсутсвии расписания"""
        return await event.show_snackbar(AnswerCallback.not_timetable_paging())

    elif date_ is None:
        """Если не указана дата, то берём самую актуальную"""
        date_ = Select.fresh_ready_timetable_date(type_name=type_name,
                                                  name_id=name_id,
                                                  type_date='string')

    if date_ is None:
        """Если в БД нет данных о расписании"""
        text = AnswerText.not_exist_timetable(name_)
        keyboard = Reply.default()
        return await message.answer(text, reply_markup=keyboard)

    data_ready_timetable = Select.ready_timetable(type_name, date_, name_)

    text = MessageTimetable(name_,
                            date_,
                            data_ready_timetable,
                            view_name=view_name,
                            view_add=view_add,
                            view_time=view_time,
                            format_=False).get()

    keyboard = Inline.timetable_paging(type_name,
                                       name_id,
                                       dates_array,
                                       date_,
                                       last_callback_data,
                                       add_back_button=add_back_button)

    if paging:
        await event.edit_message(text, keyboard=keyboard)
    else:
        await message.answer(text, keyboard=keyboard)


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["t_p"], ind=-4))
async def timetable_paging(event: MessageEvent, last_ind: int = -4) -> None:
    """Листание расписания"""
    add_back_button = False
    [callback_data_split, last_callback_data] = get_callback_values(event, last_ind)
    if last_callback_data != "":
        """Если есть данные о прошлых шагах - добавляем кнопку  Назад"""
        add_back_button = True

    [type_name, name_id, date_] = callback_data_split[-3:]
    await timetable(event,
                    event=event,
                    last_callback_data=last_callback_data,
                    paging=True,
                    type_name=type_name,
                    name_id=name_id,
                    date_=date_,
                    add_back_button=add_back_button)


@user_labeler.message(CommandRule("Настройки", [""], 0))
async def settings(message: Message, event: MessageEvent = None, edit_text: bool = False) -> None:
    """Обработчик запроса на получение Настроек пользователя"""
    user_id = message.peer_id
    user_settings_data = list(Select.user_info(user_id, table_name="vkontakte"))
    table_name = user_settings_data[0]
    name_id = user_settings_data[2]

    if name_id is not None:
        name_ = Select.name_by_id(table_name, name_id)
        user_settings_data[1] = name_

    text = AnswerText.settings()
    keyboard = Inline.user_settings(user_settings_data)

    if edit_text:
        if event is not None:
            await event.edit_message(text, keyboard=keyboard)
            await answer_callback(event)
    else:
        await message.answer(text, keyboard=keyboard)

    # logger.info(f"message {user_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["s"]))
async def settings_callback(event: MessageEvent) -> None:
    """Обработчик CallbackQuery на возвращение к меню Настроек"""
    await settings(event.object, event=event, edit_text=True)


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["ms"]))
async def main_settings(event: MessageEvent) -> None:
    """Обработчик CallbackQuery на переход к окну основных настроек"""
    user_id = event.object.peer_id
    user_settings_data = list(Select.user_info(user_id, table_name="vkontakte"))

    text = AnswerText.main_settings()
    keyboard = Inline.main_settings(user_settings_data)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["settings_info"], ind=-2))
async def settings_info(event: MessageEvent) -> None:
    """Обработчик CallbackQuery для получения информации при нажатии кнопки"""
    user_id = event.object.peer_id
    settings_name = event.payload['cmd'].split()[-1]
    await event.show_snackbar(AnswerCallback.settings_info(settings_name))
    # logger.info(f"callback {user_id} {settings_name}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["update_main_settings_bool"], ind=-2))
async def update_main_settings_bool(event: MessageEvent) -> None:
    """Обновление настроек True/False"""
    user_id = event.object.peer_id
    settings_name = event.payload['cmd'].split()[-1]

    result = Update.user_settings_bool(user_id, table_name="vkontakte", name_=settings_name)

    await main_settings(event)
    # logger.info(f"callback {user_id} {settings_name} {result}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["support"]))
async def support(event: MessageEvent, last_ind: int = -1) -> None:
    """Обработка нажатия кнопки support"""
    user_id = event.object.peer_id
    last_callback_data = get_callback_values(event, last_ind)[-1]

    text = AnswerText.support()
    keyboard = Inline.support(event.payload['cmd'], last_callback_data)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["donate"]))
async def donate(event: MessageEvent, last_ind: int = -1) -> None:
    """Вывести меню с вариантами донейшинов"""
    user_id = event.object.peer_id
    last_callback_data = get_callback_values(event, last_ind)[-1]

    text = AnswerText.donate()
    keyboard = Inline.donate(last_callback_data)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(["future_updates"]))
async def future_updates(event: MessageEvent, last_ind: int = -1) -> None:
    """Вывести сообщение о будущих апдейтах"""
    user_id = event.object.peer_id
    last_callback_data = get_callback_values(event, last_ind)[-1]

    text = Select.config("future_updates")

    '''    
    if text in (None, ''):
        return await callback.bot.answer_callback_query(callback_query_id=callback.id,
                                                        text=AnswerCallback.error["default"])
    '''

    keyboard = Inline.get_back_button(last_callback_data, return_keyboard=True)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['sp_gr', 'sub_gr', 'sp_tch', 'sub_tch']))
async def spam_or_subscribe_name_id(event: MessageEvent, last_ind: int = -1) -> None:
    """Обновление настроек spamming и subscribe для карточек группы/преподавателя"""
    user_id = event.object.peer_id
    callback_data_split = get_callback_values(event, last_ind)[0]
    event.object.payload = get_event_last_callback_data(event, last_ind)

    type_column_name = callback_data_split[-1]
    action_type = type_column_name.split('_')[0]
    short_type_name = type_column_name.split('_')[-1]
    name_id = callback_data_split[-2]

    result = Update.user_settings_array(user_id,
                                        table_name="vkontakte",
                                        name_=column_name_by_callback.get(type_column_name),
                                        value=name_id,
                                        limit_array=DEFAULT_LIMIT_SUBSCRIPTIONS)
    # if number_sub == DEFAULT_LIMIT_SUBSCRIPTIONS:
    # text = AnswerCallback.limit_number_subscriptions()
    # return await event.show_snackbar(text)

    # удалили подписку
    if type_column_name in ('sub_gr', 'sub_tch') and not result:

        # если это карточка с активной основной подпиской, то удаляем её
        if Update.user_settings_value(user_id,
                                      "name_id",
                                      name_id,
                                      table_name="vkontakte",
                                      remove_=True):
            Update.user_settings(user_id,
                                 "type_name",
                                 "NULL",
                                 table_name="vkontakte",
                                 convert_val_text=False)

        Update.user_settings_array(user_id,
                                   table_name="vkontakte",
                                   name_=column_name_by_callback.get(f"sp_{short_type_name}"),
                                   value=name_id,
                                   remove_=True)

    elif type_column_name in ("sp_gr", "sp_tch") and result:

        Update.user_settings_array(user_id,
                                   table_name="vkontakte",
                                   name_=column_name_by_callback.get(f"sub_{short_type_name}"),
                                   value=name_id,
                                   remove_=None)

    # await event.show_snackbar(AnswerCallback.spam_or_subscribe_name_id(action_type, result))

    # logger.info(f"callback {user_id} {short_type_name} {action_type} {name_id} {result}")

    if short_type_name == "gr":
        await group__card(event)

    elif short_type_name == "tch":
        await teacher_card(event)


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['m_sub_gr', 'm_sub_tch']))
async def main_subscribe_name_id(event: MessageEvent, last_ind: int = -1) -> None:
    """Обновление настроек main_subscribe для карточек группы/преподавателя"""
    user_id = event.object.peer_id
    callback_data_split = get_callback_values(event, last_ind)[0]
    event.object.payload = get_event_last_callback_data(event, last_ind)
    type_column_name = callback_data_split[-1]
    name_id = callback_data_split[-2]

    result = Update.user_settings_value(user_id, "name_id", name_id, table_name="vkontakte")

    # если основная подписка добавлена
    if result:
        Update.user_settings(user_id,
                             "type_name",
                             type_column_name == "m_sub_gr",
                             table_name="vkontakte",
                             convert_val_text=True)
        '''
        Update.user_settings_array(user_id,
                                   table_name="vkontakte",
                                   name_=column_name_by_callback.get(type_column_name),
                                   value=name_id,
                                   remove_=None)
        '''
    else:
        Update.user_settings(user_id,
                             "type_name",
                             "NULL",
                             table_name="vkontakte",
                             convert_val_text=False)
        Update.user_settings(user_id,
                             "name_id",
                             "NULL",
                             table_name="vkontakte",
                             convert_val_text=False)

    # await event.show_snackbar(AnswerCallback.main_subscribe_name_id(result))

    # logger.info(f"callback {user_id} {type_column_name} {name_id} {result}")

    if type_column_name == 'm_sub_gr':
        await group__card(event)

    elif type_column_name == 'm_sub_tch':
        await teacher_card(event)


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['gc'], ind=-2))
async def group__card(event: MessageEvent, last_ind: int = -2) -> None:
    """Показать карточку группы"""
    user_id = event.object.peer_id
    [callback_data_split, last_callback_data] = get_callback_values(event, last_ind)
    group__id = callback_data_split[-1]

    group__user_info = Select.user_info_name_card("group_", user_id, group__id, table_name="vkontakte")
    group__name = group__user_info[1]

    text = AnswerText.group__card()
    keyboard = Inline.group__card(group__user_info,
                                  callback_data=event.payload['cmd'],
                                  last_callback_data=last_callback_data)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id} {group__name} {group__id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['tc'], ind=-2))
async def teacher_card(event: MessageEvent, last_ind: int = -2) -> None:
    """Показать карточку преподавателя"""
    user_id = event.object.peer_id
    [callback_data_split, last_callback_data] = get_callback_values(event, last_ind)
    teacher_id = callback_data_split[-1]

    teacher_user_info = Select.user_info_name_card("teacher", user_id, teacher_id, table_name="vkontakte")
    teacher_name = teacher_user_info[1]

    text = AnswerText.teacher_card()
    keyboard = Inline.teacher_card(teacher_user_info,
                                   callback_data=event.payload['cmd'],
                                   last_callback_data=last_callback_data)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id} {teacher_name} {teacher_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['lessons_list'], ind=-2))
async def lessons_list_by_teacher(event: MessageEvent, last_ind: int = -2) -> Union[None, Any]:
    """Вывести список дисциплин, которые ведёт преподаватель"""
    user_id = event.object.peer_id
    [callback_data_split, last_callback_data] = get_callback_values(event, last_ind)
    teacher_id = callback_data_split[-1]
    teacher_name = Select.name_by_id("teacher", teacher_id)

    lessons_list = Select.lessons_list_by_teacher(teacher_name)

    if not lessons_list:
        return await event.show_snackbar(AnswerCallback.not_lessons_list())

    text = AnswerText.lessons_list_by_teacher(teacher_name, lessons_list)
    keyboard = Inline.get_back_button(last_callback_data, return_keyboard=True)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id} {teacher_name} {teacher_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['wdmt']))
async def week_days_main_timetable(event: MessageEvent, last_ind: int = -1) -> Union[None, Any]:
    """Показать список дней недели дня получения основного расписания"""
    user_id = event.object.peer_id
    [callback_data_split, last_callback_data] = get_callback_values(event, last_ind)

    type_name = column_name_by_callback.get(callback_data_split[-3])
    name_id = int(callback_data_split[-2])
    week_days_id_main_timetable_array = Select.week_days_timetable(type_name, name_id, "main_timetable")

    if not week_days_id_main_timetable_array:
        return await event.show_snackbar(text=AnswerCallback.not_week_days_main_timetable())

    text = AnswerText.week_days_main_timetable()
    keyboard = Inline.week_days_main_timetable(week_days_id_main_timetable_array,
                                               current_week_day_id=datetime.now().weekday(),
                                               callback_data=event.payload['cmd'],
                                               last_callback_data=last_callback_data)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['download_main_timetable']))
async def download_main_timetable(event: MessageEvent) -> None:
    """Скачать Основное расписание на неделю"""
    user_id = event.object.peer_id
    callback_data_split = event.payload['cmd'].split()

    type_name = column_name_by_callback.get(callback_data_split[-4])
    name_id = callback_data_split[-3]
    name_ = Select.name_by_id(type_name, name_id)

    text = f"{name_}\n\n"

    for week_day_id in range(6):
        week_day_name = get_week_day_name_by_id(week_day_id, bold=False)
        data_main_timetable = Select.view_main_timetable(type_name,
                                                         name_,
                                                         week_day_id=week_day_id,
                                                         lesson_type=None)
        main_timetable_message = MessageTimetable(name_,
                                                  week_day_name,
                                                  data_main_timetable,
                                                  start_text="",
                                                  view_name=False,
                                                  type_format="txt",
                                                  format_timetable="only_date").get()
        text += f"{main_timetable_message}\n\n"

    file_source = BytesIO(str.encode(text))  # StringIO(text)
    title = f"{name_} На неделю {event.event_id[-4:]}.txt"

    # await callback.bot.send_chat_action(user_id, 'upload_document')
    await asyncio.sleep(2)
    doc = await DocMessagesUploader(api).upload(title, file_source, peer_id=user_id)
    await event.send_message(attachment=doc)
    await answer_callback(event)
    # logger.info(f"callback {user_id} {type_name} {name_} {name_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['wdmt'], ind=-2))
async def get_main_timetable_by_week_day_id(event: MessageEvent, last_ind: int = -1) -> Union[None, Any]:
    """Получить основное расписание для дня недели"""
    user_id = event.object.peer_id
    [callback_data_split, last_callback_data] = get_callback_values(event, last_ind)

    week_day_id = callback_data_split[-1]

    type_name = column_name_by_callback.get(callback_data_split[-4])
    name_id = callback_data_split[-3]
    name_ = Select.name_by_id(type_name, name_id)

    data_main_timetable = Select.view_main_timetable(type_name, name_, week_day_id=week_day_id, lesson_type=None)

    if not data_main_timetable:
        week_day = get_week_day_name_by_id(week_day_id, type_case="prepositional", bold=False)
        text = AnswerCallback.not_timetable_by_week_day(week_day)
        return await event.show_snackbar(text)

    date_week_day = get_week_day_name_by_id(week_day_id,
                                            type_case='prepositional',
                                            bold=False)
    text = MessageTimetable(name_,
                            date_week_day,
                            data_main_timetable,
                            start_text="Основное расписание на ",
                            mode="vkontakte",
                            format_=True).get()
    keyboard = Inline.get_back_button(last_callback_data, return_keyboard=True)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id} {type_name} {name_} {week_day_id} {bool(data_main_timetable)}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['mhrt']))
async def months_history_ready_timetable(event: MessageEvent, last_ind: int = -1) -> None:
    """Вывести список с месяцами"""
    max_number_months = 3
    user_id = event.object.peer_id
    last_callback_data = get_callback_values(event, last_ind)[-1]

    months_array = Select.months_ready_timetable()
    if len(months_array) > max_number_months:
        months_array = months_array[-max_number_months:]

    text = AnswerText.months_history_ready_timetable()
    keyboard = Inline.months_ready_timetable(months_array, event.payload['cmd'], last_callback_data)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['mhrt'], ind=-2))
async def dates_ready_timetable(event: MessageEvent, last_ind: int = -1) -> Union[None, Any]:
    """Вывести список дат"""
    user_id = event.object.peer_id
    [callback_data_split, last_callback_data] = get_callback_values(event, last_ind)
    type_name = column_name_by_callback.get(callback_data_split[-4])
    name_id = callback_data_split[-3]
    month = callback_data_split[-1]

    name_ = Select.name_by_id(type_name, name_id)

    dates_array = Select.dates_ready_timetable(month=month,
                                               type_name=type_name,
                                               name_id=name_id)
    if not dates_array:
        """Если нет расписания ни на одну дату"""
        text = AnswerCallback.not_ready_timetable_by_month(month_translate(month))
        return await event.show_snackbar(text)

    text = AnswerText.dates_ready_timetable(name_, month_translate(month))
    keyboard = Inline.dates_ready_timetable(dates_array, event.payload['cmd'], last_callback_data)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id} {type_name} {name_} {name_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['download_ready_timetable_by_month']))
async def download_ready_timetable_by_month(event: MessageEvent) -> None:
    """Скачать всё расписание на определённый месяц"""
    user_id = event.object.peer_id
    callback_data_split = event.payload['cmd'].split()

    type_name = column_name_by_callback.get(callback_data_split[-5])
    name_id = callback_data_split[-4]
    month = callback_data_split[-2]
    month_translate_text = month_translate(month)

    name_ = Select.name_by_id(type_name, name_id)

    text = f"{name_} {month_translate_text}\n\n"

    user_info = Select.user_info_by_column_names(user_id,
                                                 column_names=['view_add', 'view_time'],
                                                 table_name='vkontakte')
    view_add = user_info[0]
    view_time = user_info[1]

    dates_array = Select.dates_ready_timetable(month=month,
                                               type_name=type_name,
                                               name_id=int(name_id),
                                               type_sort='ASC')

    for date_ in dates_array:
        data_ready_timetable = Select.ready_timetable(type_name, date_, name_)
        date_text = date_.strftime('%d.%m.%Y')

        if data_ready_timetable:
            ready_timetable_message = MessageTimetable(name_,
                                                       date_text,
                                                       data_ready_timetable,
                                                       view_name=False,
                                                       view_add=view_add,
                                                       view_time=view_time,
                                                       format_=False).get()
            text += f"{ready_timetable_message}\n\n"

    file_source = BytesIO(str.encode(text))
    title = f"{name_} {month_translate(month)} {event.event_id[-4:]}.txt"

    # await callback.bot.send_chat_action(user_id, 'upload_document')
    await asyncio.sleep(2)
    doc = await DocMessagesUploader(api).upload(title, file_source, peer_id=user_id)
    await event.send_message(attachment=doc)
    await answer_callback(event)
    # logger.info(f"callback {user_id} {month} {type_name} {name_} {name_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['mhrt'], -3))
async def ready_timetable_by_date(event: MessageEvent) -> None:
    """Вывести расписание для определённой даты"""
    user_id = event.object.peer_id
    callback_data_split = event.payload['cmd'].split()
    type_name = column_name_by_callback.get(callback_data_split[-5])
    name_id = callback_data_split[-4]
    date_ = callback_data_split[-1]

    await view_ready_timetable(event,
                               type_name=type_name,
                               name_id=name_id,
                               date_=date_)
    # logger.info(f"callback {user_id} {date_} {type_name} {name_id} name_id")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['dpo'], -1))
async def view_dpo_information(event: MessageEvent, last_ind: int = -1) -> None:
    """Получить информацию о ДПО"""
    user_id = event.object.peer_id
    [callback_data_split, last_callback_data] = get_callback_values(event, last_ind)

    type_name = column_name_by_callback.get(callback_data_split[-3])
    name_id = callback_data_split[-2]
    name_ = Select.name_by_id(type_name, name_id)

    week_days_id_dpo_array = Select.week_days_timetable(type_name, name_id, "dpo")

    text = f"{name_}\n"
    for week_day_id in week_days_id_dpo_array:
        """Перебираем дни недели с ДПО"""
        data_dpo = Select.dpo(type_name, name_, week_day_id)
        week_day_name = get_week_day_name_by_id(week_day_id, type_case='default', bold=False)
        text += MessageTimetable(name_,
                                 week_day_name,
                                 data_dpo,
                                 start_text="",
                                 view_name=False,
                                 mode='vkontakte',
                                 format_=True).get()
        text += '\n'

    keyboard = Inline.get_back_button(last_callback_data, return_keyboard=True)

    await event.edit_message(text, keyboard=keyboard)
    #await callback.bot.answer_callback_query(callback.id)
    await answer_callback(event)
    # logger.info(f"callback {user_id} {type_name} {name_} {name_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['g_rt', 't_rt']))
async def view_ready_timetable(event: MessageEvent,
                               last_ind: int = -1,
                               type_name: str = None,
                               name_id: int = None,
                               date_: str = None) -> Union[None, Any]:
    """Показать текущее расписание"""
    user_id = event.object.peer_id
    [callback_data_split, last_callback_data] = get_callback_values(event, last_ind)

    if type_name is None:
        type_name = column_name_by_callback.get(callback_data_split[-1])

    if name_id is None:
        name_id = callback_data_split[-2]

    if date_ is None:
        date_ = Select.fresh_ready_timetable_date(type_name=type_name,
                                                  name_id=name_id,
                                                  type_date='string')

        if date_ is None:
            """Расписание полностью отсутствует"""
            text = AnswerCallback.not_ready_timetable()
            return await event.show_snackbar(text)

    user_info = Select.user_info_by_column_names(user_id,
                                                 column_names=['view_add', 'view_time'],
                                                 table_name="vkontakte")
    view_add = user_info[0]
    view_time = user_info[1]

    name_ = Select.name_by_id(type_name, name_id)

    data_ready_timetable = Select.ready_timetable(type_name, date_, name_)

    text = MessageTimetable(name_,
                            date_,
                            data_ready_timetable,
                            view_add=view_add,
                            view_time=view_time,
                            format_=False).get()

    dates_array = Select.dates_ready_timetable(type_name=type_name,
                                               name_id=name_id,
                                               type_date='string',
                                               type_sort='ASC')

    # keyboard = Inline.get_back_button(last_callback_data, return_keyboard=True)

    keyboard = Inline.timetable_paging(type_name,
                                       name_id,
                                       dates_array,
                                       date_,
                                       last_callback_data,
                                       add_back_button=True)

    await event.edit_message(text, keyboard=keyboard)
    await answer_callback(event)
    # logger.info(f"callback {user_id} {type_name} {name_} {name_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['*'], ind=0))
async def view_callback(event: MessageEvent) -> None:
    """Обработчик нажатий на пустые кнопки"""
    user_id = event.object.peer_id
    text = ' '.join(event.payload['cmd'].split()[1:])
    # await event.show_snackbar(text)
    await answer_callback(event)
    # logger.info(f"callback {user_id}")


@user_labeler.raw_event(GroupEventType.MESSAGE_EVENT,
                        MessageEvent,
                        CheckPayload(['close']))
async def close(event: MessageEvent) -> None:
    """Обработать запрос на удаление (закрытие) окна сообщения"""
    user_id = event.object.peer_id
    '''
    await api.messages.delete(
        peer_id=event.object.peer_id,
        message_ids=event.object.conversation_message_id,
        delete_for_all=True,
        group_id=Keys.VK_BOT_ID
    )
    '''
    await event.edit_message("Сообщение 'удалено'!")
    # logger.info(f"callback {user_id}")


@user_labeler.message(CommandRule("call_schedule", ["!", "/"], 0))
async def call_schedule(message: Message) -> None:
    """Расписание звонков"""
    user_id = message.peer_id
    await message.answer(AnswerText.call_schedule())
    # logger.info(f"callback {user_id}")


@user_labeler.message(CommandRule("help", ["!", "/"], 0))
async def help_message(message: Union[Message, Any]) -> None:
    """Вывести help-сообщение"""
    user_id = message.peer_id
    await api.messages.send(user_id=user_id,
                            message=AnswerText.help_message(),
                            random_id=datetime.now().timestamp())
    # logger.info(f"message {user_id}")


@user_labeler.message(CommandRule("keyboard", ["!", "/"], 0))
async def show_keyboard(message: Message) -> None:
    """Показать клавиатуру"""
    user_id = message.peer_id

    text = AnswerText.show_keyboard()
    keyboard = Reply.default()
    if user_id in ADMINS_VK:
        keyboard = Reply.default_admin()

    await message.answer(text, keyboard=keyboard)
    # logger.info(f"message {user_id}")


@user_labeler.message()
async def other_messages(message: Message) -> None:
    """Обработчик сторонних сообщений"""
    user_id = message.peer_id
    text = AnswerText.other_messages()
    await message.answer(text)
    # logger.info(f"message {user_id}")
