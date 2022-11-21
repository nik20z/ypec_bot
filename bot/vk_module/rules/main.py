from typing import Union
from vkbottle.bot import Message, MessageEvent
from vkbottle.dispatch.rules import ABCRule
from bot.vk_module.handlers.config import state_dispenser

from bot.database import Select


class CheckNewUser(ABCRule[Message]):
    """Проверка на нового пользователя"""
    async def check(self, message: Message) -> Union[dict, bool]:
        return Select.user_info(user_id=message.peer_id, table_name="vkontakte") is None


class CheckPayload(ABCRule[Message]):
    """Проверка вхождения команды в callback по индексу"""
    def __init__(self, commands: list, ind: int = -1):
        self.commands = commands
        self.ind = ind

    async def check(self, event_or_message) -> Union[dict, bool]:
        #if isinstance(event, MessageEvent):
        callback_data_split = event_or_message.payload['cmd'].split()
        try:
            return callback_data_split[self.ind] in self.commands
        except IndexError:
            return False


class CheckState(ABCRule[Message]):
    """"""
    def __init__(self, state):
        self.state = state
        # UserStates.choice_type_name
        #self.user_id = user_id
        #self.state = state

    async def check(self, event: MessageEvent) -> Union[dict, bool]:
        #print("isinstance(event, MessageEvent)", isinstance(event, MessageEvent))
        user_id = event.object.peer_id
        user_data = await state_dispenser.get(user_id)
        if user_data is not None:
            current_state = str(user_data.state).split(':')[-1]
            return current_state == self.state
        return False


