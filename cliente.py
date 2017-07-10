import time

#!/usr/bin/env python

import socket
s = socket.socket()
s.connect(("localhost", 57809))

#Mensaje de prueba de conexión

paquete = b"01" #solicitud de conexión
paquete+= b"0002" #sistema autonomo
paquete+= b"0a0a0a0a" #IP
paquete+= b"FFFFFF00" #mascara

s.send(paquete)

#Mensaje de prueba sobre alcanzabilidad
time.sleep(2)
s = socket.socket()
s.connect(("localhost", 57809))
paquete= b"02" #Intercambio de información
paquete+= b"0002" #Sistema autónomo
paquete+= b"00020002" #Dirección IP
paquete+= b"00000002" #Cantidad de destinos
paquete+= b"00030003"
paquete+= b"FFFFFF00"
paquete+= b"0003" #Cantidad de SAs
paquete+= b"0024" #SAs a seguir
paquete+= b"0025"
paquete+= b"0026"
paquete+= b"00070007" #Direcciones IP
paquete+= b"FFFFFF00" #Máscaras
paquete+= b"0003" #Cantidad de SAs
paquete+= b"0043" #SAs a seguir
paquete+= b"0044"
paquete+= b"0045"
s.send(paquete)

#Mensaje de prueba sobre alcanzabilidad
time.sleep(2)
s = socket.socket()
s.connect(("localhost", 57809))
paquete= b"02" #Intercambio de información
paquete+= b"0002" #Sistema autónomo
paquete+= b"00020002" #Dirección IP
paquete+= b"00000002" #Cantidad de destinos
paquete+= b"00030004"
paquete+= b"FFFFFFF0"
paquete+= b"0003" #Cantidad de SAs
paquete+= b"0010" #SAs a seguir
paquete+= b"0011"
paquete+= b"0012"
paquete+= b"00090099" #Direcciones IP
paquete+= b"FFFFFFF0" #Máscaras
paquete+= b"0003" #Cantidad de SAs
paquete+= b"0067" #SAs a seguir
paquete+= b"0068"
paquete+= b"0069"
s.send(paquete)

time.sleep(2)
s = socket.socket()
s.connect(("localhost", 57809))

#se crea un paquete con solicitud de desconexion
paquete = b"03" #solicitud de conexión
paquete+= b"0002" #sistema autonomo
paquete+= b"00020002" #IP
paquete+= b"FFFFFF00" #mascara
s.send(paquete)

s.close()
