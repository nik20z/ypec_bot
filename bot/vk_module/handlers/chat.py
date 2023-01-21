from vkbottle.bot import BotLabeler, Message, rules
# from vkbottle_types.objects import MessagesConversation


class ChatInfoRule(rules.ABCRule[Message]):
    async def check(self, message: Message) -> dict:
        chats_info = await message.ctx_api.messages.get_conversations_by_id(message.peer_id)
        return {"chat": chats_info.items[0]}


chat_labeler = BotLabeler()
chat_labeler.vbml_ignore_case = True
chat_labeler.auto_rules = [rules.PeerRule(from_chat=True), ChatInfoRule()]


'''
@chat_labeler.message(command="самобан")
async def kick(message: Message, chat: MessagesConversation) -> None:
    await message.ctx_api.messages.remove_chat_user(message.chat_id, message.from_id)
    await message.answer(f"Участник самоустранился из {chat.chat_settings.title} по собственному желанию")


@chat_labeler.message(text="где я")
async def where_am_i(message: Message, chat: MessagesConversation) -> None:
    await message.answer(f"Вы в <<{chat.chat_settings.title}>>")
'''
