import requests

from bot.misc import Keys


def get_user_name(user_id: int):
    """Получить имя пользователя по from_id"""
    url = f"https://api.vk.com/method/users.get?user_ids={user_id}" \
          f"&access_token={Keys.VK_TOKEN}" \
          f"&v={Keys.VK_TOKEN_VERSION}"
    response = requests.get(url).json()
    user_data = response['response'][0]

    first_name = user_data['first_name']
    last_name = user_data['last_name']
    user_name = f"{first_name} {last_name}"
    return first_name, last_name, user_name
