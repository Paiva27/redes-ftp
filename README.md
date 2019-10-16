###	Informações	### 

Autores: Alexander Cristian e Rafael Paiva	Data: 10 de outubro de 2019

Este trabalho tem como objetivo implementar um protocolo FTP Simples utilizando a biblioteca sockets.

*usuario:alex
*senha:123456

###	Comandos	###

*put: o comando put envia um arquivo que está armazenado no cliente para o 
  servidor. A sintaxe do comando é: put nome_arquivo. 

*get: o comando get faz com que o cliente receba um arquivo que está armazenado
  no servidor. A sintaxe do comando é: get nome_arquivo.

*ls: o comando ls busca o nome de todos os arquivos na pasta do servidor e 
  mostra para o cliente.

###	Compilação	###
Dentro do diretorio ftp_server
$ ftpserver.py

###	Executar	###
Dentro do diretorio ftp_client
$ ftp_client.py