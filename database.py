from pymongo import MongoClient
import config
import time

# load database
client = MongoClient(config.MONGODB_HOST)
db = client.airalarmrobot.db

userlist:list = db.find_one({'_id': 0})['userlist']

db.update_one({'_id': 0}, {'$inc': {'runid': 1}})
def get_runid():
    return db.find_one({'_id': 0})['runid']
runid = get_runid()
print("Чекаємо 5 секунд")
time.sleep(5)
print("Підключено до MongoDB")

def new_user(id:int):
    if id in userlist: return
    db.update_one({'_id': 0}, {'$push': {'userlist': id}})
    userlist.append(id)

def remove_user(id:int):
    if not id in userlist: return
    db.update_one({'_id': 0}, {'$pull': {'userlist': id}})
    userlist.remove(id)

def get_data():
    return db.find_one({'_id': 0})['data']

def update_data(value:dict):
    db.update_one({'_id': 0}, {'$set': {'data': value}})