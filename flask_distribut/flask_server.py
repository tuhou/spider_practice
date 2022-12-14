# -*- coding:utf-8 -*-
"""
author:tuhou
time:2022/11/3 14:02 
思路：
"""
import threading
import time
import traceback
from queue import Queue

from flask import Flask, request, jsonify
from mongo_handler import get_db
from pymongo import InsertOne, UpdateMany, UpdateOne

db = get_db()
app = Flask(__name__)
insert_data_queue = Queue(maxsize=100)
update_task_queue = Queue(maxsize=100)
task_queues = {}


def handle_insert_data():
    print('start handle_insert_data')
    while True:
        try:
            ds = {}
            while insert_data_queue.qsize() > 0:
                try:
                    coll, data = insert_data_queue.get_nowait()
                    insert_data_queue.task_done()
                except Exception as e:
                    break
                if coll in ds:
                    ds[coll].append(InsertOne(data))
                else:
                    ds[coll] = [InsertOne(data)]
            print(ds)
            for coll, datas in ds.items():
                db[coll].bulk_write(datas)
            time.sleep(10)
        except Exception as e:
            trace = traceback.format_exc()
            info = 'error:{},trace:{}'.format(str(e), trace)
            print(info)


def handle_update_task():
    print('start handle_update_task')
    while True:
        try:
            ds = {}
            while update_task_queue.qsize() > 0:
                try:
                    coll, task, status = update_task_queue.get_nowait()
                    update_task_queue.task_done()
                except Exception as e:
                    break
                if coll in ds:
                    ds[coll].append(UpdateOne({'url': task['url']}, {'$set': {'status': status}}, upsert=True))
                else:
                    ds[coll] = [UpdateOne({'url': task['url']}, {'$set': {'status': status}}, upsert=True)]
            print(ds)
            for coll, datas in ds.items():
                db[coll].bulk_write(datas)
            time.sleep(10)
        except Exception as e:
            trace = traceback.format_exc()
            info = 'error:{},trace:{}'.format(str(e), trace)
            print(info)


t = threading.Thread(target=handle_insert_data, args=())
t.start()

t = threading.Thread(target=handle_update_task, args=())
t.start()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/insert_data', methods=['POST'])
def insert_data():
    rj = request.get_json()
    print(rj)
    coll_name = rj['coll_name']
    data = rj['data']

    if not db[coll_name].find_one({'url': data['url']}):
        insert_data_queue.put((coll_name, data))
        # db[coll_name].insert_one(data)

    return 'OK'


@app.route('/insert_task', methods=['POST'])
def insert_task():
    """
    当存在url时不更新
    @return:
    """
    rj = request.get_json()
    coll_name = rj['coll_name']
    data = rj['data']
    if not db[coll_name].find_one({'url': data['url']}):
        db[coll_name].insert_one(data)
    return 'OK'


@app.route('/get_task')
def get_task():
    coll_name = request.args.get('coll_name', None)
    if coll_name not in task_queues:
        task_queues[coll_name] = Queue()
    # task = db[coll_name].find_and_modify({'status': 0}, {'$set': {'status': 1}})
    if task_queues[coll_name].qsize() <= 0:
        tasks = db[coll_name].find({'status': 0}).limit(100)

        requests = []
        for task in tasks:
            requests.append(
                UpdateMany({'url': task["url"]}, {"$set": {"status": 1, "last_crawl_time": 0}}))
            task_queues[coll_name].put(task)
        if len(requests) > 0:
            db[coll_name].bulk_write(requests)
    try:
        task = task_queues[coll_name].get_nowait()
    except:
        task = {}
    # 此处删除_id的原因是因为_id对象是一个object类型的
    task.pop('_id', None)
    return jsonify(task)


@app.route('/update_task', methods=['POST'])
def update_task():
    rj = request.get_json()
    coll_name = rj['coll_name']
    task = rj['data']
    status = rj['status']
    # db[coll_name].update_one({'url': task['url']}, {'$set': {'status': status}})
    update_task_queue.put((coll_name, task, status))
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
