#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socketserver
import sys,os
import hashlib
from os.path import join, getsize
from conf import settings
from modules import auth_user



class Myserver(socketserver.BaseRequestHandler):
    '''Servidor FTP'''
    def handle(self):
        try:
            self.conn = self.request
            while True:
                login_info = self.conn.recv(1024).decode()    #Recebe a senha do usuario enviado pelo cliente
                result = self.authenticat(login_info)
                status_code = result[0]
                self.conn.sendall(status_code.encode())
                if status_code == "400":
                    continue
                self.user_db = result[1]             #Informação do usuário logado
                self.current_path = self.user_db["homepath"]  #Diretório bd do usuário atual
                self.home_path = self.user_db["homepath"]  #Diretorio do host do usuário

                while True:
                    command = self.conn.recv(1024).decode()
                    command_str = command.split()[0]
                    if hasattr(self,command_str):
                        func = getattr(self,command_str)
                        func(command)
                    else:self.conn.sendall("401".encode())
        except ConnectionResetError as e:
            self.conn.close()
            print(e)

    def authenticat(self,login_info):
        '''Usuário autentificado'''
        auth = auth_user.User_operation()       # Cria a instancia de autentificação
        result = auth.authentication(login_info)    # Usuário autentificado
        if result:return "200",result
        else:return "400",result

    def get(self,command):
        '''Download'''
        if len(command.split()) > 1:
            filename = command.split()[1]
            file_path = self.current_path + r"/%s"%filename
            if os.path.isfile(file_path):               #Verifica existência do arquivo
                self.conn.sendall("201".encode())      #Comando executavel
                file_size = os.stat(file_path).st_size  # Tamanho total arquivo
                status_code = self.conn.recv(1024).decode()    #Recebe status 403

                # O arquivo existe no cliente
                if status_code == "403":
                    self.conn.sendall("000".encode())
                    has_send_size = self.conn.recv(1024).decode()
                    has_send_size = int(has_send_size)   #Recebe tamanho do arquivo 
                    # Arquivo do cliente é incompleto 
                    if has_send_size < file_size:
                        self.conn.sendall("205".encode())   
                        file_size -= has_send_size  
                        response = self.conn.recv(1024)  

                    # Arquivo impossível de ler e não pode ter download
                    else:
                        self.conn.sendall("405".encode())
                        return
                # O arquivo não existe no cliente
                elif status_code == "402":
                    has_send_size = 0
                self.conn.sendall(str(file_size).encode())  # pega o tamanho do arquivo
                response = self.conn.recv(1024)  # Espera por uma confirmação do tamanho do arquivo pelo cliente
                with open(file_path,"rb") as file:
                    file.seek(has_send_size)
                    m = hashlib.md5()
                    for line in file:
                        m.update(line)
                        self.conn.sendall(line)               #Manda arquivo
                self.conn.sendall(m.hexdigest().encode())     #Encriptação md5
            else:self.conn.sendall("402".encode()) 
            print(file_path)
        else:self.conn.sendall("401".encode())

    def put(self,command):
        '''Upload'''
        filename = command.split()[1]
        file_path = self.current_path + r"/%s" % filename
        self.conn.sendall("000".encode())   #Manda confirmação
        file_size = self.conn.recv(1024).decode()  # Tamanho do arquivo
        file_size = int(file_size)
        limit_size = self.user_db["limitsize"]      #Quota de disco
        used_size = self.__getdirsize(self.home_path)   #Espaço de disco usado
        if limit_size >= file_size+used_size:
            self.conn.sendall("202".encode())
            with open(file_path, "wb") as file:  # Começa a receber
                revice_size = 0
                m = hashlib.md5()
                while revice_size < file_size:
                    minus_size = file_size - revice_size
                    if minus_size > 1024:
                        size = 1024
                    else:
                        size = minus_size
                    data = self.conn.recv(size)
                    revice_size += len(data)
                    file.write(data)
                    m.update(data)
                new_file_md5 = m.hexdigest() 
                server_file_md5 = self.conn.recv(1024).decode()
                if new_file_md5 == server_file_md5: 
                    self.conn.sendall("203".encode())
        else:self.conn.sendall("404".encode())

    
    def ls(self,command):
        '''Lista arquivos de um diretório'''
        print(self.current_path)
        if len(command.split()) == 1:
            self.conn.sendall("201".encode()) 
            try:
                response = self.conn.recv(1024)
                print(self.current_path)
                send_data = os.popen('ls %s'%self.current_path)
                self.conn.sendall(send_data.read().encode())
            except:
                print("Erro")
        else:self.conn.sendall("401".encode())
    
    def pwd(self,command):
        '''Vê o caminho atual do usuário'''
        if len(command.split()) == 1:
            self.conn.sendall("201".encode())
            response = self.conn.recv(1024)
            send_data = self.current_path
            print(send_data)
            self.conn.sendall(send_data.encode())
        else:self.conn.sendall("401".encode())
    
    def mkdir(self,command):
        '''Cria um diretório'''
        if len(command.split()) > 1:
            dir_name = command.split()[1]       #Nome do diretório
            dir_path = self.current_path + "%s"%dir_name #Caminho do diretório
            if not os.path.isdir(dir_path):     #Caminho não existe
                self.conn.sendall("201".encode())
                response = self.conn.recv(1024)
                os.popen("mkdir %s"%dir_path)
            else:self.conn.sendall("403".encode())
        else:self.conn.sendall("401".encode())
    

    def __getdirsize(self,home_path):
        '''Pega tamanho de diretório'''
        size = 0
        for root, dirs, files in os.walk(home_path):
            size += sum([getsize(join(root, name)) for name in files])
        return size