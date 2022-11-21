from .admin import admin_labeler
from .user import user_labeler
from .chat import chat_labeler
# Если использовать глобальный лейблер, то все хендлеры будут зарегистрированы в том же порядке, в котором они были импортированы

__all__ = ("admin_labeler", "user_labeler", "chat_labeler")
