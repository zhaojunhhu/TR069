# -*- coding:utf8 -*-


import os
import shutil
import sys
import MySQLdb
import json

from sys import argv

# 数据库参数
host = "127.0.0.1"
user = "root"
passwd = "root"
dbname = "tr069_v3_0"

# 工单参数
ISP = argv[1]
VERSION = argv[2]
DOMAIN = argv[3]
METHOD = []
WORKLISTDOC = []
WORKLISTARG = []



ROOT_PATH = "F:\\GitHub\\TR069\\lib\\worklists\\operator"
ROOT_PATH = os.path.join(ROOT_PATH, ISP, VERSION, 'business', DOMAIN)

# 遍历获取工单参数
for filename in os.listdir(ROOT_PATH):
    METHOD.append(filename)
    parent = os.path.join(ROOT_PATH, filename)
    try:
        i = sys.path.index(parent)
        if (i !=0):
            # stratege= boost priviledge
            sys.path.pop(i)
            sys.path.insert(0, parent)
    except Exception,e:
        sys.path.insert(0, parent)

    import data
    reload(data)
    from data import *

    WORKLISTDOC.append(WORKLIST_DOC)
    WORKLISTARG.append(WORKLIST_ARGS)

    # 删除pyc文件
    DEL_parent = os.path.join(parent, 'data.pyc')
    os.remove(DEL_parent)

# 数据库插入
db = MySQLdb.connect(host, user, passwd, dbname, charset='utf8')
cursor = db.cursor()

sql = """
    INSERT INTO wl_template(ISP, VERSION, DOMAIN, METHOD, PARAMETERS, DOC) VALUES (%s, %s, %s, %s, %s, %s)
"""
for i in range(len(METHOD)):
    cursor.execute(sql, (ISP, VERSION, DOMAIN, METHOD[i], json.dumps(WORKLISTARG[i]), WORKLISTDOC[i]))

cursor.close()
db.commit()
db.close()
