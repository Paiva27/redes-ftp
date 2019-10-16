#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os,hashlib
import json
from conf import settings
from modules import auth_user
from modules import socket_server


def create_db():
    '''cria o banco de dados'''
    user_database={}
    encryption = auth_user.User_operation()
    limitsize = settings.LIMIT_SIZE
    for k,v in settings.USERS_PWD.items():
        username = k
        password = encryption.hash(v)
        user_db_path  = settings.DATABASE +"/%s.db"%username
        user_home_path = settings.HOME_PATH +"/%s"%username
        user_database["username"] = username
        user_database["password"] = password
        user_database["limitsize"] = limitsize
        user_database["homepath"] = user_home_path
        if not os.path.isfile(user_db_path):
            with open(user_db_path,"w") as file:
                file.write(json.dumps(user_database))

def create_dir():
    '''cria diretórios dos usuarios'''
    for username in settings.USERS_PWD:
        user_home_path = settings.HOME_PATH + r"\%s" %username
        if not os.path.isdir(user_home_path):
            os.popen("mkdir %s" %user_home_path)



if __name__ == "__main__":
    '''chama a função main'''
    create_db()         #Cria um banco de dados
    create_dir()        #Cria os diretórios
                        #Configura o FTP
    server = socket_server.socketserver.ThreadingTCPServer(settings.IP_PORT, socket_server.Myserver)
    server.serve_forever()