from telethon.sync import TelegramClient
import database as db
import config
import asyncio

""" data['alarm_level'] - Рівень тривоги | 0:нема, 1:схід, 2:вся Україна """
data = db.get_data()
client = TelegramClient('session', config.CLIENT_API_ID, config.CLIENT_API_HASH)

async def update_last(value:dict):
    db.update_data(value)

async def get_updates():
    await client.connect()
    # print('get_updates start')
    # Check @war_monitor | monitor
    async for msg in client.iter_messages('war_monitor', limit=1): break
    if msg.id != data['war_monitor']:
        if 'Зліт МіГ' in msg.text:
            data['war_monitor'] = msg.id
            data['alarm_level'] = 2
            asyncio.create_task(update_last(data))
            return '🚨 <b>Тривога по всій Україні!</b>\n → Зліт МіГ-31К ВПС рф - @war_monitor', True
        elif 'Загроза застосування наземних пускових' in msg.text or 'Запуск ракет ЗРК С-300' in msg.text:
            data['war_monitor'] = msg.id
            data['alarm_level'] = 1
            asyncio.create_task(update_last(data))
            return '🚨 <b>Тривога на східних областях!</b>\n Загроза застосування наземних пускових комплексів ОТРК/ЗРК - @war_monitor', False
        elif 'Відбій по областях' in msg.text:
            for_all = data['alarm_level'] == 2
            data['war_monitor'] = msg.id
            data['alarm_level'] = 0
            asyncio.create_task(update_last(data))
            return '❕ <b>Відбій тривоги по областях</b> - @war_monitor', for_all

    # Check @Hajun_BY | Беларускі Гаюн
    async for msg in client.iter_messages('Hajun_BY', limit=1): break
    if msg.id != data['Hajun_BY']:
        if 'Взлёт МиГ' in msg.text:
            data['Hajun_BY'] = msg.id
            asyncio.create_task(update_last(data))
            return '❗️ <b>Скоро буде тривога по всій Україні!</b>\n → Зліт МіГ-31К ВПС рф над територією білорусі - @Hajun_BY', True
        elif 'Посадка ДРЛО' in msg.text:
            data['Hajun_BY'] = msg.id
            asyncio.create_task(update_last(data))
            return '❓ <b>Скоро буде відбій тривог?</b>\n → Посадка ДРЛО А-50У ВКС рф - @Hajun_BY', True

    # If no updates, return None
    # print('get_updates end')
    await client.disconnect()
    return None, False

# async def get_last_msg(channel:str):
#     print('get_last_msg start |', channel)
#     async for msg in client.iter_messages('war_monitor', limit=1):
#         print('get_last_msg end')
#         return msg

# Test
# print(asyncio.run(get_updates()))


# Шоб ввійти в акаунт
# import asyncio
# async def main():
#     client = TelegramClient('session', config.CLIENT_API_ID, config.CLIENT_API_HASH)
#     await client.connect()
#     # await client.start(phone_number, '<password>')
#     async for message in client.iter_messages('war_monitor', limit=1):
#         print(message.sender_id, ':', message.text)
# asyncio.run(main())