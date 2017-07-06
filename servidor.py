#!/usr/bin/env python

import socket
import os
import os.path
import threading
from _datetime import datetime

run = 0
vecinos = {}
escuchando = False;

def escribeArchivo(aEscribir):
    ## Si no es la primera escritura del run, solo escribe en la bitacora
    if (run == 1):
        file = open("Bitacora.txt", "a")
        file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + aEscribir + "\n")
    ## Si es la primera escritura del run, borra la bitacora vieja y crea una nueva
    elif (run == 0):
        if (os.path.isfile("Bitacora.txt")):
            os.remove("Bitacora.txt")
        global run
        run = 1
        file = open("Bitacora.txt", "a")
        file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + aEscribir + "\n")

def escucha():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 57809))
    s.listen(1)

    #creación de tabla alcanzabilidad
    alcanzabilidad = {}
    while True:
        print("")
        print ("Esperando mensaje...")
        sc, addr = s.accept()
        recibido = sc.recv(1024)
        # se verifica si el tamaño del paquete es de una solicitud
        if len(recibido) == 22:
            #Se divide el paquete en sus respectivas partes
            tipo = recibido[0:2] #tipo de solicitud
            sa = recibido[2:6] #sistema autonomo
            ip = recibido[6:14]
            mascara = recibido[14:22]
            if tipo == b"01":
                print("se ingresó una solicitud de conexión")
                #se envía mensaje de aceptación
                respuesta = b"02"
                respuesta += sa
                respuesta += ip
                respuesta += mascara
                sc.send(respuesta)
                print("se envió respuesta de aceptación")
                #se ingresa en la tabla vecinos,
                #el tipo re refiere a si está conectado o no
                vecinos[ip] = {'estado': tipo,'mascara': mascara,'sa': sa}
                escribeArchivo("Se agregó el vecino: "+str(ip))
                print("se agregó con éxito el vecino: ",ip)
            elif tipo == b"02":
                print("Solicitud de vecino aceptada")
            elif tipo == b"03":
                print("se ingresó una solicitud de desconexión")
                #buscar en la tabla vecinos
                if ip in vecinos:
                    vecino = vecinos[ip]
                    if vecino['mascara'] == mascara and vecino['sa'] == sa:
                        vecino['tipo'] = b"00"
                        escribeArchivo("Se desconectó el vecino: "+str(ip))
                        print("se desconectó el vecino", ip)
                else:
                    print("no existe un vecino con esa ip")
            else:
                print("Paquete con solicitud no reconocida")
            print("tabla vecinos: ",vecinos)
        #else:
            #Se divide el paquete
            #tipo = recibido[0:2]
            #sa = recibido[2:6]
            #ip = recibido[6:14]
            #tam = int(recibido[14:22])
            #alcanzabilidad[ip] = {'tipo' : tipo, 'sa' : sa, 'Alcanzables': tam}
            #num = 0
            #alcanzables = alcanzabilidad[ip]
            #for i in range (0, (i+16)*int(tam)):
            #    alcanzables[str(num)] = recibido[i:i+16]
            #print("tabla alcanzabilidad: ", alcanzabilidad)
    sc.close()
    s.close()

listener = threading.Thread(target=escucha, name = 'router')

def menu():
    os.system('clear') 
    print ("Seleccione una opción")
    print ("\t1 - Enviar solicitud de vecino")
    print ("\t2 - Solicitar desconexión")
    print ("\t3 - Enviar información de alcanzabilidad")
    if not escuchando:
        print ("\t4 - Comenzar recepción de mensajes")
    print ("\t9 - salir")

while True:
    menu()
    opcionMenu = input("inserte una opción >> ")
    if opcionMenu=="1":
        print ("")
        ip = input("Ingrese la dirección IP del nuevo vecino\n")
        ip = ip.split(".")
        for i in range(0,len(ip)):
            ip[i] = hex(int(ip[i]))[2:]
            if len(ip[i]) == 1:
                ip[i] = "0"+ip[i]
        ip = ''.join(ip)
        ip = ip.encode()
        print(ip)
        mascara = input("Ingrese la máscara del nuevo vecino\n")
        mascara = mascara.split(".")
        for i in range(0,4):
            mascara[i] = hex(int(mascara[i]))[2:]
            if len(mascara[i]) == 1:
                mascara[i] = "0"+mascara[i]
        mascara = ''.join(mascara)
        mascara = mascara.encode()
        print(mascara)
        sa = input("Ingrese el sistema autonomo al que pertenece el nuevo vecino\n")
        sa = hex(int(sa))[2:]
        l = len(sa)
        l = 4-l
        for i in range(0,l):
            sa = "0"+sa
        sa = sa.encode()
        print(sa)
        solicitud = b"01"
        solicitud += sa
        solicitud += ip
        solicitud += mascara
        #solicitud.encode()
        print(solicitud)
        print("falta enviar mensaje de solicitud (se hace con los hilos)")
        estado = b"01"
        vecinos[ip] = {'estado': estado,'mascara': mascara,'sa': sa}
        escribeArchivo("Se agregó el vecino: "+str(ip))
        input("Se agregó con éxito el vecino: "+str(ip)+"\npulsa una tecla para continuar\n")
    elif opcionMenu=="2":
        print("")
        ip = input("Ingrese la dirección IP del vecino a desconectar\n")
        ip = ip.split(".")
        for i in range(0, 4):
            ip[i] = hex(int(ip[i]))[2:]
            if len(ip[i]) == 1:
                ip[i] = "0" + ip[i]
        ip = ''.join(ip)
        ip = ip.encode()
        print(ip)
        mascara = input("Ingrese la máscara del vecino a desconectar\n")
        mascara = mascara.split(".")
        for i in range(0, 4):
            mascara[i] = hex(int(mascara[i]))[2:]
            if len(mascara[i]) == 1:
                mascara[i] = "0" + mascara[i]
        mascara = ''.join(mascara)
        mascara = mascara.encode()
        print(mascara)
        sa = input("Ingrese el sistema autonomo al que pertenece el vecino a desconectar\n")
        sa = hex(int(sa))[2:]
        l = len(sa)
        l = 4 - l
        for i in range(0,l):
            sa = "0"+sa
        sa = sa.encode()
        print(sa)
        # buscar en la tabla vecinos
        if ip in vecinos:
            vecino = vecinos[ip]
            if vecino['mascara'] == mascara and vecino['sa'] == sa:
                vecinos[ip]['estado'] = b"00"
                escribeArchivo("Se desconectó el vecino: "+str(ip))
                print("se desconectó el vecino", ip)
        input("Pulsa una tecla para continuar")
    elif opcionMenu=="3":
        print ("")
        input("Ha pulsado la opción 3...\npulse una tecla para continuar")
    elif opcionMenu=="4":
        if escuchando:
            input("No ha pulsado ninguna opción correcta...\npulse una tecla para continuar")
        else:
            escuchando = True
            listener.start()
    elif opcionMenu=="9":
        break
    else:
        print ("")
        input("No ha pulsado ninguna opción correcta...\npulse una tecla para continuar")
print ("Fin")
