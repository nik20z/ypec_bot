
<h1 align="center">YPEC Bot</h1>

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&width=435&lines=Telegram-Vk+bot+%D0%BA%D0%BE%D0%BB%D0%BB%D0%B5%D0%B4%D0%B6%D0%B0+%D0%AF%D0%9F%D0%AD%D0%9A" alt="Typing SVG" /></a>

<p align="center">
  <img src="https://img.shields.io/github/stars/nik20z/ypec_bot">
  <img src="https://img.shields.io/github/issues/nik20z/ypec_bot">
  <img src="https://img.shields.io/github/license/nik20z/ypec_bot">
</p>

[![https://telegram.me/ypec_bot](https://img.shields.io/badge/💬%20Telegram-Channel-blue.svg?style=flat-square)](https://telegram.me/ypec_bot)
[![https://vk.com/ypec_bot](https://img.shields.io/badge/💬%20Вконтакте-Группа-blue.svg?style=flat-square)](https://vk.com/ypec_bot)

![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)

## Описание
Ежедневная рассылка готового расписания (соединение основного расписания с заменами, которые появляются каждый день), а также отслеживание изменений в заменах в течение дня с последующим оповещением пользователей

![image](https://user-images.githubusercontent.com/62090150/209471806-4aa5afb0-5cb7-4db8-b83a-c276114f0d6d.png)
![image](https://user-images.githubusercontent.com/62090150/209471733-0c0b6709-ee87-4381-91e0-d18f7cc39e96.png)


## Будущие апдейты

Телеграм:
- [ ] Ограничить количество подписок до 10 на каждый профиль
- [ ] Добавить возможность принудительного обновления расписания
- [ ] Добавить возможность остановки и запуска процедуры обновления расписания

Вконтакте:
- [ ] Увеличить количество подписок и добавить персональную настройку по карточкам групп/преподавателей, как в тг
- [ ] Реализовать возможность работы бота в беседе (+ добавить настройку закрепа для бесед)
- [ ] Придумать, как можно упростить листание списка групп/преподавателей 
- [ ] Добавить возможность просмотра расписания за конкретный день (как в тг)

Общее:
- [ ] Автоматическое создание бэкапов
- [ ] Улучшение алгоритма обработки названий предметов (поиск похожих названий и их объединение)
- [ ] Написание парсера логов и добавление функции, собирающей статистику (отдельно для каждой соц сети)
- [ ] Создание анти-спам системы, которая будет блокировать спамеров

На перспективу (наброски):
- [ ] Создать систему ведомостей в облаке для старост, бот будет автоматически создавать веломости для групп
- [ ] Сделать возможность оплаты ботом своего же хостинга, при этом, он должен выпрашивать донаты у юзеров


## Порядок установки на VPS (Ubuntu 20.04.3 LTS)

```
sudo adduser ypec

sudo apt update
sudo apt upgrade
sudo apt install python3.8
sudo apt install python3-pip

sudo apt update
sudo apt install postgresql postgresql-contrib
```

Настраиваем локаль через пакет, выбирая ru_RU.utf8:
```
dpkg-reconfigure locales
apt-get install language-pack-ru
```

Изменяем локаль кластера базы данных (12 заменяем на вашу версию postgres)
```
pg_lsclusters
pg_dropcluster --stop 12 main
pg_createcluster --locale ru_RU.utf8 --start 12 main
```

Создаём пользователя, создаём базу данных и добавляем расширение pg_trgm
```
sudo -i -u postgres
  psql
    CREATE USER ypec WITH PASSWORD '123456789';
    CREATE DATABASE ypec_bot;
    \c ypec_bot
    CREATE EXTENSION pg_trgm;
    \q
  exit
```

Клонируем репозиторий
```
cd /home/ypec
git clone https://github.com/nik20z/ypec_bot.git
cd ypec_bot
```

Устанавливаем необходимые библиотеки
```
pip3 install aiohttp
pip3 install aiogram
pip3 install beautifulsoup4
pip3 install loguru
pip3 install lxml
pip3 install nest-asyncio
pip3 install psycopg2-binary
pip3 install requests
pip3 install transliterate
pip3 install vkbottle
```

Альтернативный способ установки всех библиотек
```
pip3 install -r requirements.txt
```

Вносим правки в файл /bot/misc/env.py
1. TG_TOKEN - получаем через Bot Father
2. VK_TOKEN - получаем в настройках группы (ставим все галочки при получении токена)
3. VK_TOKEN_VERSION
4. VK_BOT_ID
5. SETTINGS - настройки доступа к БД

Добавляем свой id в vkontakte в файл /bot/vk_module/config.py (если, не знаете, где найти: [тык](https://vk.com/faq18062) и [тык](https://regvk.com/id))
1. GOD_ID_VK - главный админ
2. ADMINS_VK - список всех админов

Добавляем свой id в telegram в файл /bot/tg_module/config.py (можно узнать через [бота](https://t.me/getmyid_bot))
1. GOD_ID_TG - главный админ
2. ADMINS_TG - список всех админов


Перед созданием службы, перезапускающей скрипт, необходимо в папку /etc/systemd/system поместить файл ypec_bot.service
```
apt-get install systemd
systemctl daemon-reload
systemctl enable ypec_bot
systemctl start ypec_bot
systemctl status ypec_bot
```

При необходимости меняем часовой пояс
```
timedatectl
timedatectl list-timezones
sudo timedatectl set-timezone Europe/Moscow
```

Если возникают проблемы с установкой python
```
sudo apt-get install libpq-dev
sudo apt-get install python-dev
```

## Для администрирования
Для установки бота на сервер и настройки советую использовать [PuTTY](https://www.putty.org). А также [WinSCP](https://winscp.net/eng/download.php) для удобного взаиможействия с файлами проекта


## После полной настройки и запуска бота

1. Парсим основное расписание по команде /get_main_timetable ALL
2. При необходимости редачим файл dpo.csv и заносим данные о ДПО в БД по команде /update_dpo

<p align="center">
  <img src="https://user-images.githubusercontent.com/62090150/193757014-4e816ff4-e524-4d3d-a0f9-5d64701e9ec0.png">
</p>

