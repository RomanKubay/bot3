from pymongo import MongoClient
import config
import time

bot = None
auth_now = False

# load database
client = MongoClient(config.MONGODB_HOST)
db = client.airalarmrobot.db

userlist:list = [[u['_id'], u['region']] for u in db.find({"_id": { "$gt": 0 }})]

db.update_one({'_id': 0}, {'$inc': {'runid': 1}})
def get_runid():
    return db.find_one({'_id': 0})['runid']
runid = get_runid()
# print("Чекаємо 5 секунд")
# time.sleep(5.2)
print("Підключено до MongoDB")

def new_user(id:int, reg:int):
    if get_user_i(id) is not None: return
    db.insert_one({'_id': id, 'region': reg})
    userlist.append([id, reg])

def change_region(id:int, reg:int):
    i = get_user_i(id)
    if i is None: return
    userlist[i][1] = reg
    db.update_one({'_id': id}, {'$set': {'region': reg}})

def remove_user(id:int):
    db.find_one_and_delete({'_id': id})
    for u in range(len(userlist)): 
        if userlist[u][0] == id: userlist.pop(u); return

def users_by_region(reg:int):
    # for u in userlist: print(u[1], reg, u[1] == reg)
    print('Search users by region', reg)
    lst = [u[0] for u in userlist if u[1] == reg]
    return lst

def get_user_i(id:int):
    for u in range(len(userlist)): 
        if userlist[u][0] == id: return u
    return None

def get_data():
    return db.find_one({'_id': 0})['data']

def update_data(value:dict):
    db.update_one({'_id': 0}, {'$set': {'data': value}})