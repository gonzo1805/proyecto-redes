import time

#!/usr/bin/env python

import socket
s = socket.socket()
s.connect(("localhost", 57809))

#Mensaje de prueba de conexión

paquete = [1]
paquete.append(0)
paquete.append(2)
paquete.append(10)
paquete.append(1)
paquete.append(92)
paquete.append(89)
paquete.append(255)
paquete.append(255)
paquete.append(0)
paquete.append(0)
info = bytes(paquete)
s.send(info)

#Mensaje de prueba sobre alcanzabilidad
time.sleep(2)
s = socket.socket()
s.connect(("localhost", 57809))

paquete = [5]
paquete.append(10)
paquete.append(1)
paquete.append(92)
paquete.append(89)
paquete.append(1)
paquete.append(10)
paquete.append(1)
paquete.append(0)
paquete.append(1)
paquete.append(255)
paquete.append(0)
paquete.append(0)
paquete.append(0)
paquete.append(1)
paquete.append(0)
paquete.append(4)
info = bytes(paquete)
s.send(info)

time.sleep(2)
s = socket.socket()
s.connect(("localhost", 57809))

#se crea un paquete con solicitud de desconexion
paquete = [3]
paquete.append(0)
paquete.append(2)
paquete.append(10)
paquete.append(1)
paquete.append(92)
paquete.append(89)
paquete.append(255)
paquete.append(255)
paquete.append(0)
paquete.append(0)
info = bytes(paquete)
s.send(info)

s.close()
