# -*- coding:utf-8 -*-
"""
author:tuhou
time:2022/11/3 14:47 
思路：
"""
import time
import traceback
import requests

from config import HOST


def insert_data(coll_name, _data, logger):
    while True:
        try:
            url = '{}/insert_data'.format(HOST)
            data = {
                'coll_name': coll_name,
                'data': _data,
            }
            res = requests.post(url, json=data)
            if res.status_code != 200:
                raise Exception('status_code:{}'.format(res.status_code))
            break
        except Exception as e:
            trace = traceback.format_exc()
            info = 'error:{},trace:{}'.format(str(e), trace)
            logger.error(info)
            time.sleep(5)


def insert_task(coll_name, task, logger=None):
    """
    通过控制不同的coll_name实现对不同集合的写入
    @param coll_name:
    @param task:
    @param logger:
    @return:
    """
    while True:
        try:
            url = '{}/insert_task'.format(HOST)
            data = {
                'coll_name': coll_name,
                'data': task
            }
            res = requests.post(url, json=data)
            if res.status_code != 200:
                raise Exception('status_code:{}'.format(res.status_code))
            break
        except Exception as e:
            trace = traceback.format_exc()
            info = 'error:{},trace:{}'.format(str(e), trace)
            logger.error(info)
            time.sleep(5)


def get_task(coll_name, logger):
    while True:
        try:
            url = '{}/get_task?coll_name={}'.format(HOST, coll_name)
            res = requests.get(url)
            if res.status_code != 200:
                raise Exception('status_code:{}'.format(res.status_code))
            return res.json()
        except Exception as e:
            trace = traceback.format_exc()
            info = 'error:{},trace:{}'.format(str(e), trace)
            logger.error(info)
            time.sleep(5)


def update_task(coll_name, task, status, logger):
    while True:
        try:
            data = {
                'coll_name': coll_name,
                'data': task,
                'status': status,
                'last_crawl_time': int(time.time())
            }
            url = '{}/update_task'.format(HOST)
            res = requests.post(url, json=data)
            if res.status_code != 200:
                raise Exception('status_code:{}'.format(res.status_code))
            break
        except Exception as e:
            trace = traceback.format_exc()
            info = 'error:{},trace:{}'.format(str(e), trace)
            logger.error(info)
            time.sleep(5)


def run():
    pass


if __name__ == '__main__':
    run()
