#!/usr/bin/env python

#importamos el modulo socket
import socket
import os
import os.path
from _datetime import datetime
run = 0

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




def menu():
    os.system('clear') # NOTA para windows tienes que cambiar clear por cls
    print ("Seleccione una opción")
    print ("\t1 - Enviar solicitud de vecino")
    print ("\t2 - Solicitar desconexión")
    print ("\t3 - Enviar información de alcanzabilidad")
    print ("\t4 - Comenzar recepción de mensajes")
    print ("\t9 - salir")

while True:
    menu()
    opcionMenu = input("inserte una opción >> ")
    if opcionMenu=="1":
        print ("")
        ip = input("Ingrese la dirección IP del nuevo vecino\n")
        ip = ip.split(".")
        for i in range(0,4):
            ip[i] = bin(int(ip[i]))
        print(ip)
        input("pulsa una tecla para continuar")
    elif opcionMenu=="2":
        print ("")
        input("Has pulsado la opción 2...\npulsa una tecla para continuar")
        escribeArchivo("gato")
    elif opcionMenu=="3":
        print ("")
        input("Has pulsado la opción 3...\npulsa una tecla para continuar")
    elif opcionMenu=="4":
        #instanciamos un objeto para trabajar con el socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Con el metodo bind le indicamos que puerto debe escuchar y de que servidor esperar conexiones
        #Es mejor dejarlo en blanco para recibir conexiones externas si es nuestro caso
        s.bind(("", 57809))

        #Aceptamos conexiones entrantes con el metodo listen, y ademas aplicamos como parametro
        #El numero de conexiones entrantes que vamos a aceptar
        s.listen(1)

        #Instanciamos un objeto sc (socket cliente) para recibir datos, al recibir datos este
        #devolvera tambien un objeto que representa una tupla con los datos de conexion: IP y puerto
        #sc, addr = s.accept()

        #creación de tabla vecinos
        vecinos = {}
        alcanzabilidad = {}

        while True:
            #Recibimos el mensaje, con el metodo recv recibimos datos y como parametro
            #la cantidad de bytes para recibir
            print("")
            print ("Esperando mensaje...")
            sc, addr = s.accept()
            recibido = sc.recv(1024)
            # se verifica si el tamaña del paquete es de una solicitud
            if len(recibido) == 88:
                #Se divide el paquete en sus respectivas partes
                tipo = recibido[0:8] #tipo de solicitud
                sa = recibido[8:24] #sistema autonomo
                ip = recibido[24:56]
                mascara = recibido[56:88]
                if tipo == b"00000001":
                    print("se ingresó una solicitud de conexión")
                    #se envía mensaje de aceptación
                    respuesta = b"00000010"
                    respuesta += sa
                    respuesta += ip
                    respuesta += mascara
                    sc.send(respuesta)
                    print("se envió respuesta de aceptación")
                    #se ingresa en la tabla vecinos,
                    #el tipo re refiere a si está conectado o no
                    vecinos = {ip:{'tipo': tipo,'mascara': mascara,'sa': sa}}
                    print("se agregó con éxito el vecino: ",ip)
                elif tipo == b"00000002":
                    print("Solicitud de vecino aceptada")
                elif tipo == b"00000003":
                    print("se ingresó una solicitud de desconexión")
                    #buscar en la tabla vecinos
                    if ip in vecinos:
                        vecino = vecinos[ip]
                        if vecino['mascara'] == mascara and vecino['sa'] == sa:
                            vecino['tipo'] = b"00000000"
                            print("se desconectó el vecino", ip)
                    else:
                        print("no existe un vecino con esa ip")
                else:
                    print("Paquete con solicitud no reconocida")
            print("tabla vecinos: ",vecinos)
            #Cerramos la instancia del socket cliente y servidor
        sc.close()
        s.close()
    elif opcionMenu=="9":
        break
    else:
        print ("")
        input("No has pulsado ninguna opción correcta...\npulsa una tecla para continuar")

print ("Fin")

