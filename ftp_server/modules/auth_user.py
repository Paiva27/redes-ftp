#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import sys,os
import hashlib
from conf import settings
class User_operation():
    '''A informação de login foi autentificada se falhar retrona none'''
    def authentication(self,login_info):
        list = login_info.split(":")            #Separa a informação da lista de informação do usuário
        login_name = list[0]           #Separando
        login_passwd = self.hash(list[1]) #Senha
        DB_FILE = settings.DATABASE + "/%s.db"%login_name
        if os.path.isfile(DB_FILE):
            user_database = self.cat_database(DB_FILE)  #Informação de usuário no database
            if login_name == user_database["username"]:
                if login_passwd == user_database["password"]:
                    return user_database

    def cat_database(self,DB_FILE):
        #Pega a informação do banco de dados
        with open(DB_FILE,"r") as file:
            data = json.loads(file.read())
            return  data

    def hash(self,passwd):
        '''Codigicação md5 para a senha'''
        m = hashlib.sha256()
        m.update(passwd.encode("utf-8"))
        return m.hexdigest()


