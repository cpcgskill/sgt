# -*-coding:utf-8 -*-
"""
:创建时间: 2023/1/23 3:14
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


def main():
    from flask import Flask
    import sgt.flask_bp

    app = Flask(__name__)

    bps = [
        sgt.flask_bp.bp,
    ]
    for bp in bps:
        app.register_blueprint(bp, url_prefix="/{}".format(bp.name))
    app.run(host='127.0.0.1', port=8000, debug=os.environ.get('sgt_debug', default='false').lower() in {'true', 'on'})


if __name__ == '__main__':
    main()
