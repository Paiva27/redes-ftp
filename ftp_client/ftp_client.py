#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import os,sys
import hashlib

class Myclient():
    #Servidor FTP
    def __init__(self,ip_port):
        self.ip_port = ip_port
    def connect(self):
    #Conectado
        self.client = socket.socket()
        self.client.connect(self.ip_port)

    def start(self):
    #Programa começa
        self.connect()
        while True:
            username = input("usuario:").strip()
            password = input("senha:").strip()
            login_info = ("%s:%s" %(username, password))
            self.client.sendall(login_info.encode())        #Logando
            status_code = self.client.recv(1024).decode()   #Status de login
            if status_code == "400":
                print("[%s] Problema de senha ou usuário"%status_code)
                continue
            else:print("[%s] Usuario autentificado com sucesso!"%status_code)
            self.interactive()

    def interactive(self):
        #shell
        while True:
            command = input("->>").strip()
            if not command:continue
            command_str = command.split()[0]
            if hasattr(self,command_str):           #Executando o comando 
                func = getattr(self,command_str)
                func(command)
            else:print("[%s] Comando não existe"%401)

    def get(self,command):
        '''下载文件'''
        self.client.sendall(command.encode())  #Manda o comando para execução
        status_code = self.client.recv(1024).decode()
        if status_code == "201":            #Se o comando for executado entra
            filename = command.split()[1]

            # O nome do arquivo existe
            if os.path.isfile(filename):
                revice_size = os.stat(filename).st_size     #Tamanho do arquivo passado
                self.client.sendall("403".encode())        #Manda status 403 se n tiver caminho
                response = self.client.recv(1024)           
                self.client.sendall(str(revice_size).encode())   #Envia tamanho do arquivo recebido
                status_code = self.client.recv(1024).decode()  #Seta o satus code

                # Tamanho do arquivo inconsistente
                if status_code == "205":          #Status 205, assim pode ser continuado
                    print("Continue com a localizacao do ultimo upload")
                    self.client.sendall("000".encode())   #Status de nova interação

                # O tamanho do arquivo é o mesmo, sem download
                elif status_code == "405":
                    print("O arquivo já existe e o tamanho é o mesmo")
                    return

            # Arquivo não existe
            else:
                self.client.sendall("402".encode())
                revice_size = 0

            file_size = self.client.recv(1024).decode() #Tamanho do arquivo
            file_size = int(file_size)
            self.client.sendall("000".encode())  #Envia que aceitou o tamanho do arquivo

            with open(filename,"ab") as file:      #Começa a receber
                #file_size = tamanho do arquivo total
                file_size +=revice_size
                m = hashlib.md5()
                while revice_size < file_size:
                    minus_size = file_size - revice_size
                    if minus_size > 1024:
                        size = 1024
                    else:
                        size = minus_size
                    data = self.client.recv(size)   #Recebendo arquivo
                    revice_size += len(data)
                    file.write(data)
                    m.update(data)
                    self.__progress(revice_size,file_size,"Baixando")      #Barra de progresso
                new_file_md5 = m.hexdigest()        
                server_file_md5 = self.client.recv(1024).decode()
                if new_file_md5 == server_file_md5:     
                    print("Arquivo baixado com sucesso!")
        else:print("[%s] Erro！"%(status_code))

    def put(self,command):
        '''上传文件'''
        if len(command.split()) > 1:
            filename = command.split()[1]
            if os.path.isfile(filename):               #Se o arquivo existir entra:
                self.client.sendall(command.encode())  #Manda comando para execução
                response = self.client.recv(1024)      #Recebe um ACK
                file_size = os.stat(filename).st_size  # Pega o tamanho do arquivo
                self.client.sendall(str(file_size).encode())  # Manda o tamanho do arquivo
                status_code = self.client.recv(1024).decode()  # Esperando resposta o status de retorno
                if status_code == "202":
                    with open(filename,"rb") as file:
                        m = hashlib.md5()
                        for line in file:
                            m.update(line)
                            send_size = file.tell()   #Guarda a posição do arquivo
                            self.client.sendall(line)
                            self.__progress(send_size, file_size, "Enviando")  #Barra de progresso
                    self.client.sendall(m.hexdigest().encode())   
                    status_code = self.client.recv(1024).decode() 
                    if status_code == "203":
                        print("Arquivo enviado com sucesso!")
                else:print("[%s] Erro！"%(status_code))
            else:
                print("[402] Erro")
        else: print("[401] Erro")

    def ls(self,command):
        '''Lista'''
        self.__universal_method_data(command)
        pass
 
    def pwd(self,command):
        '''Diretorio Atual'''
        self.__universal_method_data(command)
        pass

    def mkdir(self,command):
        '''Cria diretorio'''
        self.__universal_method_none(command)
        pass


    def __progress(self, trans_size, file_size,mode):
        bar_length = 100    #tamanho da barra de progresso
        percent = float(trans_size) / float(file_size)
        hashes = '=' * int(percent * bar_length)    
        spaces = ' ' * (bar_length - len(hashes))    
        sys.stdout.write("%s:%.2fM/%.2fM %d%% [%s]\n"%(mode,trans_size/1048576,file_size/1048576,percent*100,hashes+spaces))
        sys.stdout.flush()

    def __universal_method_none(self,command):
        self.client.sendall(command.encode())  
        status_code = self.client.recv(1024).decode()
        if status_code == "201": 
            self.client.sendall("000".encode())  
        else:
            print("[%s] Erro！" % (status_code))

    def __universal_method_data(self,command):
        self.client.sendall(command.encode())   
        status_code = self.client.recv(1024).decode()
        if status_code == "201":   
            self.client.sendall("000".encode())     
            data = self.client.recv(1024).decode()
            print(data)
        else:print("[%s] Erro！" % (status_code))

if __name__ == "__main__":
    ip_port =("127.0.0.1",9999)         #ip porta e endereco
    client = Myclient(ip_port)            #novo cliente
    client.start()                      #comeca o programa