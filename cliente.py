import time

#!/usr/bin/env python

#importamos el modulo para trabajar con sockets
import socket

#Creamos un objeto socket para el servidor. Podemos dejarlo sin parametros pero si
#quieren pueden pasarlos de la manera server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = socket.socket()

#Nos conectamos al servidor con el metodo connect. Tiene dos parametros
#El primero es la IP del servidor y el segundo el puerto de conexion
s.connect(("localhost", 57809))

#Creamos un bucle para retener la conexion

paquete = b"00000001" #solicitud de conexión
paquete+= b"0000000000000010" #sistema autonomo
paquete+= b"00000000000000100000000000000010" #IP
paquete+= b"11111111111111111111111100000000" #mascara

#Con la instancia del objeto servidor (s) y el metodo send, enviamos el mensaje introducido
#s.send(mensaje)
s.send(paquete)

time.sleep(2)
s = socket.socket()
s.connect(("localhost", 57809))
#se crea un paquete con solicitud de desconexion
paquete = b"00000003" #solicitud de conexión
paquete+= b"0000000000000010" #sistema autonomo
paquete+= b"00000000000000100000000000000010" #IP
paquete+= b"11111111111111111111111100000000" #mascara
s.send(paquete)

#Cerramos la instancia del objeto servidor
s.close()
