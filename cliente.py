import time

#!/usr/bin/env python

import socket
s = socket.socket()
s.connect(("localhost", 57809))

#Mensaje de prueba de conexión

paquete = b"01" #solicitud de conexión
paquete+= b"0002" #sistema autonomo
paquete+= b"00020002" #IP
paquete+= b"FFFFFF00" #mascara

s.send(paquete)

#Mensaje de prueba sobre alcanzabilidad
time.sleep(2)
s = socket.socket()
s.connect(("localhost", 57809))
paquete= b"02" #Intercambio de información
paquete+= b"0002" #Sistema autónomo
paquete+= b"00020002" #Dirección IP
paquete+= b"00000005" #Cantidad de destinos
paquete+= b"00030003"
paquete+= b"FFFFFF00"
paquete+= b"00040004"
paquete+= b"FFFFFF00"
paquete+= b"FFFFFF00"
paquete+= b"00050005"
paquete+= b"FFFFFF00"
paquete+= b"00060006"
paquete+= b"00070007" #Direcciones IP
paquete+= b"FFFFFF00" #Máscaras
paquete+= b"0001" #Cantidad de SAs
paquete+= b"0002" #SAs a seguir
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
