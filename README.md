# Get Contact Info

Скрипт, позволяющий получить информацию по всем чатам пользователей в bot_maker в течении двуз недель

## Что надо установить

- python>3.8
- aiohttp
- pandas

## Как использовать

1. Получаем access_token в bot_maker
2. ```export BOTMAKER_ACCESS_TOKEN=<ваш токен>```
3. pytnon3.8 get_all_dialogs.py

## Результат

- Выводит все сообщения пользователей в формате csv в all_messages.csv
- Выводит всю инфу про пользователей в формате csv в all_info.csv
