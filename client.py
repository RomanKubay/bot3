import asyncio
loop = asyncio.get_event_loop()
from telethon.sync import TelegramClient
import database as db
import keyboards as kb
import config

""" data['alarm_level'] - Рівень тривоги | 0:нема, 1:вся Україна """
data = db.get_data()
CHANNELS, ALARMS = [], []
auth_code, password = None, None

async def update_last(value:dict):
    db.update_data(value)

async def updates_loop():
    global auth_code, password
    client = TelegramClient('session', config.CLIENT_API_ID, config.CLIENT_API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print('Потрібно авторизуватись')
        await client.send_code_request(config.PHONE_NUMBER)
        await db.bot.send_message(config.TG_ID, "⏳ Чекаю на код, який тобі прийшов, і пароль через пробіл.", reply_markup=kb.close)
        db.auth_now = True
        while auth_code is None: await asyncio.sleep(0.2)

        try: await client.sign_in(config.PHONE_NUMBER, auth_code)
        except: await client.sign_in(password=password)

        await db.bot.send_message(config.TG_ID, "✅ Готово", reply_markup=kb.close)
        del auth_code, password
    print('Telegram client connected')
    first_time = True
    while True:
        ch = None
        # Check @war_monitor | monitor
        async for msg in client.iter_messages('war_monitor', limit=1): break
        if msg.id != data['war_monitor'] and msg.text is not None:
            if  data['alarm_level'] == 0 and 'Зліт МіГ' in msg.text:
                data['war_monitor'] = msg.id
                data['alarm_level'] = 1
                asyncio.create_task(update_last(data))
                ch = '🚨 <b>Зараз тривога по всій Україні!</b>\n → <i>Зліт МіГ-31К ВПС рф</i> - @war_monitor'
            elif data['alarm_level'] == 1 and 'Відбій по областях' in msg.text:
                data['war_monitor'] = msg.id
                data['alarm_level'] = 0
                asyncio.create_task(update_last(data))
                ch = '❕ <b>Відбій тривоги по областях</b> - @war_monitor'

        # Check @Hajun_BY | Беларускі Гаюн
        async for msg in client.iter_messages('Hajun_BY', limit=1): break
        if msg.id != data['Hajun_BY'] and msg.text is not None:
            if data['alarm_level'] == 0 and 'Взлёт МиГ' in msg.text:
                data['Hajun_BY'] = msg.id
                data['alarm_level'] = 1
                asyncio.create_task(update_last(data))
                ch = '❗️ <b>Скоро буде тривога по всій Україні!</b>\n → <i>Зліт МіГ-31К над територією білорусі</i> - @Hajun_BY'
            elif data['alarm_level'] == 0 and 'Взлёт ДРЛО' in msg.text:
                data['Hajun_BY'] = msg.id
                asyncio.create_task(update_last(data))
                ch = '❕ <b>Скоро <i>може</i> бути тривога по всій Україні.</b>\n → <i>Зліт ДРЛВ А-50У</i> - @Hajun_BY\n\nЗазвичай через 5-30 хв. після цього злітає МіГ-31К, <b>але не завжди</b>.'
            elif 'Посадка ДРЛО' in msg.text:
                data['Hajun_BY'] = msg.id
                asyncio.create_task(update_last(data))
                ch = '❓ <b>Скоро буде відбій тривог?</b>\n → <i>Посадка ДРЛО А-50У</i> - @Hajun_BY'

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
                    print((i, t))
                    alarms.append((i, t))
                    break
        if lmid is not None:
            data['alert'] = lmid
            asyncio.create_task(update_last(data))

        if not first_time:
            if ch is not None: CHANNELS.append(ch); print(ch)
            for a in alarms: ALARMS.append(a); print(a)
        first_time = False
        await asyncio.sleep(config.CHECK_DELAY)
loop.create_task(updates_loop())

print('client')