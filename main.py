# -*-coding:utf-8 -*-
"""
:创建时间: 2023/3/7 11:56
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

import sys
import threading
import time


def start_thread(target):
    thread = threading.Thread(target=target)
    thread.start()
    return thread


if __name__ == '__main__':
    import server
    import train

    server_thread = start_thread(target=server.main)
    train_thread = start_thread(target=train.main)

    while True:
        if not server_thread.is_alive():
            sys.exit(1)
        if not train_thread.is_alive():
            sys.exit(1)
        time.sleep(0.1)
