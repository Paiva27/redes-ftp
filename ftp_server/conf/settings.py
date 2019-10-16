#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os,sys,pprint

#Seta o diretório base
diretorioBase = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0,diretorioBase)

#Seta o diretorio do banco de dados
DATABASE = os.path.join(diretorioBase,"db")
#Seta o diretório da home pro usuario
HOME_PATH = os.path.join(diretorioBase,"home")
HOME_PATH = HOME_PATH+ '/'
print(HOME_PATH)
#Vetores de usuários
USERS_PWD = {"alex":"123456","lzl":"8888","eric":"6666"}

#tamanho máximo do arquivo são de 10M
LIMIT_SIZE = 1024000

#configuração ftp
IP_PORT = ("0.0.0.0",9999)

