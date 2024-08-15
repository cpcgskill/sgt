# -*-coding:utf-8 -*-
"""
:创建时间: 2023/2/14 23:31
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

import os
if os.path.isfile('./sgt.env'):
    import dotenv
    dotenv.load_dotenv('./sgt.env')

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
)

def main():
    import sgt.train

    sgt.train.main()


if __name__ == '__main__':
    main()
