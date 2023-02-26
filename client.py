from telethon.sync import TelegramClient
import database as db
import config
import asyncio

""" data['alarm_level'] - Рівень тривоги | 0:нема, 1:вся Україна """
data = db.get_data()
client = TelegramClient('session', config.CLIENT_API_ID, config.CLIENT_API_HASH)

async def update_last(value:dict):
    db.update_data(value)

async def get_channel_updates():
    await client.connect()
    ch = None
    # Check @war_monitor | monitor
    async for msg in client.iter_messages('war_monitor', limit=1): break
    if msg.id != data['war_monitor']:
        if 'Зліт МіГ' in msg.text:
            data['war_monitor'] = msg.id
            data['alarm_level'] = 1
            asyncio.create_task(update_last(data))
            ch = '🚨 <b>Тривога по всій Україні!</b>\n → <i>Зліт МіГ-31К ВПС рф</i> - @war_monitor'
        elif 'Відбій по областях' in msg.text:
            data['war_monitor'] = msg.id
            data['alarm_level'] = 0
            asyncio.create_task(update_last(data))
            ch = '❕ <b>Відбій тривоги по областях</b> - @war_monitor'

    # Check @Hajun_BY | Беларускі Гаюн
    async for msg in client.iter_messages('Hajun_BY', limit=1): break
    if msg.id != data['Hajun_BY']:
        if 'Взлёт МиГ' in msg.text:
            data['Hajun_BY'] = msg.id
            asyncio.create_task(update_last(data))
            ch = '❗️ <b>Скоро буде тривога по всій Україні!</b>\n → <i>Зліт МіГ-31К ВПС рф над територією білорусі</i> - @Hajun_BY'
        elif 'Посадка ДРЛО' in msg.text:
            data['Hajun_BY'] = msg.id
            asyncio.create_task(update_last(data))
            ch = '❓ <b>Скоро буде відбій тривог?</b>\n → <i>Посадка ДРЛО А-50У ВКС рф</i> - @Hajun_BY'

    # Повітряні тривоги
    alarms = []
    lmid = None
    async for msg in client.iter_messages('air_alert_ua', limit=30):
        if lmid is None: lmid = msg.id; 
        if msg.id == data['alert']: break

        text = msg.text
        if '🟡' in text: text = text[:90]
        
        if 'Повітряна' in text: t = 0 # Повітряна тривога
        elif 'Відбій тр' in text: t = 1 # Відбій повітряної тривоги
        elif 'Загроза ар' in text: t = 2 # Загроза артобстрілу
        elif 'Відбій за' in text: t = 3 # Відбій загрози артобстрілу
        else: t = 4 # Шось відбувається невідоме

        for i in range(len(config.regions_short)):
            if config.regions_short[i] in text:
                alarms.append((i, t))
                break
    if lmid is not None:
        data['alert'] = lmid
        asyncio.create_task(update_last(data))


    # If no updates, return None
    await client.disconnect()
    return ch, alarms

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