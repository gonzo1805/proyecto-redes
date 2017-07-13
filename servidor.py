import socket
import os
import os.path
import threading
import time
import random
import sys
from _datetime import datetime

import struct

run = 0
vecinos = {}
alcanzabilidad = {}
alcanzabilidad['localhost'] = {}
#esto es completamente arbitrario
IP_HOST = "10.1.130.155"
MSK_HOST = "255.255.0.0"
SA_HOST = "31"

def escribeArchivo(aEscribir, nombreArchivo):
    ## Si no es la primera escritura del run, solo escribe en la bitacora
    if (run == 1):
        file = open(nombreArchivo, "a")
        file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + aEscribir + "\n")
    ## Si es la primera escritura del run, borra la bitacora vieja y crea una nueva
    elif (run == 0):
        if (os.path.isfile(nombreArchivo)):
            os.remove(nombreArchivo)
        global run
        run = 1
        file = open(nombreArchivo, "a")
        file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + aEscribir + "\n")

def confirmacion(paquete,ip):
    try:
        print(paquete)
        s = socket.socket()      
        s.connect((ip, 57809)) #"192.168.1.21"      
        s.send(paquete)
        s.close()
    except:
        return 0
    else:
        return 1

def encode(direccion):
    direccion = direccion.split(".")
    if len(direccion) == 1:
        sa_hex = hex(int(direccion[0]))[2:]
        l = len(sa_hex)
        l = 4-l
        for i in range(0,l):
            sa_hex = "0"+sa_hex
        direccion = sa_hex.encode()
    else:
        for i in range(0,len(direccion)):
            direccion[i] = hex(int(direccion[i]))[2:]
            if len(direccion[i]) == 1:
                direccion[i] = "0"+direccion[i]
        direccion = ''.join(direccion)
        direccion = direccion.encode()

    return direccion

def decode(direccion):
    string = direccion.decode("utf-8")
    decoded = ""
    parte1 = string[0:2]
    parte2 = string[2:4]
    if len(direccion) == 4:
        x = int(parte1, 16)
        decoded += x.__str__()
        x = int(parte2, 16)
        decoded += x.__str__()
    else:
        parte3 = string[4:6]
        parte4 = string[6:]
        x = int(parte1, 16)
        decoded += x.__str__()
        decoded += "."
        x = int(parte2, 16)
        decoded += x.__str__()
        decoded += "."
        x = int(parte3, 16)
        decoded += x.__str__()
        decoded += "."
        x = int(parte4, 16)
        decoded += x.__str__()
    return decoded


def escucha():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 57809))
    s.listen(1)

    while True:
        print("")
        print ("Esperando mensaje...")
        sc, addr = s.accept()
        recibido = sc.recv(1024)
        recibido = list(recibido)
        print(recibido)
        if len(recibido) != 0:
            #se verifica si el tamaño del paquete es de una solicitud
            if recibido[0] != 5:
                tipo = b"0" + bytes(hex(recibido[0])[2:],"utf-8")
                sa = recibido[1]
                sa += recibido[2]
                sa = encode(str(sa))
                ip = str(recibido[3])+"."
                ip += str(recibido[4])+"."
                ip += str(recibido[5])+"."
                ip += str(recibido[6])
                ip = encode(ip)
                mascara = str(recibido[7])+"."
                mascara += str(recibido[7])+"."
                mascara += str(recibido[9])+"."
                mascara += str(recibido[10])
                mascara = encode(mascara)
                recibido = b''
                recibido += tipo+sa+ip+mascara
                print(recibido)
                #Se divide el paquete en sus respectivas partes
                if tipo == b"01":
                    print("se ingresó una solicitud de conexión")
                    if ip in vecinos:
                        print("Ya existe un vecino la dirección:",ip)
                        input("Pulse una tecla para continuar")
                    else:                
                        #se envía mensaje de aceptación
                        respuesta = b"02"
                        respuesta += encode(SA_HOST)
                        respuesta += encode(IP_HOST)
                        respuesta += encode(MSK_HOST)
                        ip_int = IP_HOST.split(".")
                        msk_int = MSK_HOST.split(".")
                        sa_int = str(SA_HOST)
                        lista = [2]            
                        lista.append(int(sa_int[0]))
                        lista.append(int(sa_int[1]))
                        for i in ip_int:
                            lista.append(int(i))
                        for i in msk_int:
                            lista.append(int(i))
                        respuesta = bytes(lista)
                        print(respuesta)
                        sc.send(respuesta)
                        print("se envió respuesta de aceptación")
                        #se ingresa en la tabla vecinos, el tipo re refiere a si está conectado o no
                        vecinos[ip] = {'estado': tipo,'mascara': mascara,'sa': sa}
                        escribeArchivo("Se agregó el vecino: "+str(ip), "Vecinos.txt")
                        print("se agregó con éxito el vecino: ",ip)
                elif tipo == b"02":
                    print("Solicitud de vecino aceptada")
                    estado = b"01"
                    vecinos[ip] = {'estado': estado,'mascara': mascara,'sa': sa}
                    escribeArchivo("Se agregó el vecino: "+str(ip), "Vecinos.txt")
                elif tipo == b"03":
                    print("se ingresó una solicitud de desconexión")
                    #buscar en la tabla vecinos
                    if ip in vecinos:
                        vecino = vecinos[ip]
                        if vecino['mascara'] == mascara and vecino['sa'] == sa:
                            vecino['estado'] = b"00"
                            del alcanzabilidad[ip]
                            escribeArchivo("Se desconectó el vecino: "+str(ip), "Vecinos.txt")
                            respuesta = b"04"
                            respuesta += encode(SA_HOST)
                            respuesta += encode(IP_HOST)
                            respuesta += encode(MSK_HOST)
                            ip_int = IP_HOST.split(".")
                            msk_int = MSK_HOST.split(".")
                            sa_int = str(SA_HOST)
                            lista = [4]            
                            lista.append(int(sa_int[0]))
                            lista.append(int(sa_int[1]))
                            for i in ip_int:
                                lista.append(int(i))
                            for i in msk_int:
                                lista.append(int(i))
                            respuesta = bytes(lista)
                            print(respuesta)
                            sc.send(respuesta)
                            print("se desconectó el vecino", ip)
                    else:
                        print("no existe un vecino con esa ip")
                elif tipo == b"03":
                    print("Solicitud de desconexion aceptada")       
                else:
                    print("Paquete con solicitud no reconocida")
                print("tabla vecinos: ",vecinos)
            elif recibido[0] == 5:
                print("Rec: ", recibido)
                indice = 0
                
                ip = str(recibido[1])+"."
                ip += str(recibido[2])+"."
                ip += str(recibido[3])+"."
                ip += str(recibido[4])
                ip = encode(ip)

                numDestinos = recibido[5]
                
                if not ip in alcanzabilidad:
                    alcanzabilidad.update({ip: {}})
                else:
                    indice = len(alcanzabilidad[ip])
                cursor = 6
                destino = alcanzabilidad[ip]
                escribeArchivo("Recibiendo destinos alcanzables del vecino "+str(ip), "Alcanzables.txt")
                for i in range (indice, indice + int(numDestinos)):                    
                    ipDestino = str(recibido[cursor])+"."
                    ipDestino += str(recibido[cursor+1])+"."
                    ipDestino += str(recibido[cursor+2])+"."
                    ipDestino += str(recibido[cursor+3])
                    ipDestino = encode(ipDestino)
                    existente = False
                    for j in range (0, len(destino)):
                        datosDestino = destino['Destino' + str(j)]
                        if ipDestino == datosDestino['IP']:
                            existente = True
                            break
                    if not existente:
                        cursor = cursor + 4
                        mascara = str(recibido[cursor])+"."
                        mascara += str(recibido[cursor+1])+"."
                        mascara += str(recibido[cursor+2])+"."
                        mascara += str(recibido[cursor+3])
                        mascara = encode(mascara)
                        destino['Destino' + str(i)] = {'IP': ipDestino, 'Mascara': mascara, 'SAs': {}}
                        datosDestino = destino['Destino' + str(i)]
                        sistemas = datosDestino['SAs']
                        cursor =  cursor + 4
                        numSistemas = int(recibido[cursor])
                        cursor = cursor + 1
                        print("numSistema: " + str(numSistemas))
                        for j in range(0, numSistemas):
                            sistemas['SA' + str(j)] = encode(str(recibido[cursor]) + str(recibido[cursor+1]))
                            cursor = cursor + 2
                        escribeArchivo("Se agregó el destino: "+str(ipDestino), "Alcanzables.txt")
                print("tabla alcanzabilidad: ", alcanzabilidad)
    sc.close()
    s.close()

def updater():
    update = threading.Timer(31.0, updater).start()
    for i in vecinos:
        direccionString = decode(i)
        soc = socket.socket()
        soc.connect((direccionString, 57809))
        paquete = [5]
        ip_int = 0
        for x in alcanzabilidad:                                             #Itera sobre cada vecino con destinos alcanzables que estén en la tabla de alcanzabilidad
            if x == "localhost":                                             #Si la entrada pertenece a localhost, envía el paquete con su propia IP como fuente
                ip_int = IP_HOST.split(".")
            else:                                                            #Si no, envía la IP ya codificada que está en la tabla (es un vecino)
                ip_int = str(decode(x)).split(".")
            for i in ip_int:
                paquete.append(int(i))
            destino = alcanzabilidad[x]                                      #Para acceder a la lista de destinos asociados a la IP del vecino
            paquete.append(len(destino))                                     #Para enviar el total de destinos alcanzables como valor hex
            for y in destino:                                                #Itera sobre cada destino para obtener sus datos
                datosDestino = destino[y]
                ip_int = str(decode(datosDestino['IP'])).split(".")          #Para acceder a los datos del destino
                for i in ip_int:                                             #Almacena la IP del destino
                    paquete.append(int(i))
                msk_int = str(decode(datosDestino['Mascara'])).split(".")
                for i in msk_int:                                            #Almacena la máscara del vecino
                    paquete.append(int(i))
                sistemas = datosDestino['SAs']                               #Para acceder a los sistmas asociados al vecino
                paquete.append(len(sistemas))                                #Para enviar el total de sistemas por los que se debe pasar para llegar a ldestino
                numero = 0
                for z in sistemas:                                           #Itera sobre cada sistema y obtiene su ID
                    sa_int = str(decode(sistemas[z]))
                    paquete.append(int(sa_int[0]))
                    paquete.append(int(sa_int[1]))                           #Almacena el ID del sistema
        if len(paquete) != 1:
            if paquete[5] != 0:                        
                respuesta = bytes(paquete)
                soc.send(respuesta)
        soc.close()

def menu():
    os.system('clear')
    print ("Seleccione una opción")
    print ("\t1 - Enviar solicitud de vecino")
    print ("\t2 - Solicitar desconexión")
    print ("\t3 - Enviar información de alcanzabilidad")
    print ("\t9 - salir")


os.system('clear')
print("Se necesita agregar destinos alcanzables (digite 0 para terminar)")

escribeArchivo("Agregando destinos alcanzables directamente (localhost)", "Alcanzables.txt")
numDestino = 0
while True:
    ip_str = input("Ingrese la dirección IP del destino (0 para terminar)\n")
    if ip_str == "0":
        break
    else:
        ip_hex = encode(ip_str)
        print(ip_hex)
        mascara_str = input("Ingrese la máscara del destino\n")
        mascara_hex = encode(mascara_str)
        print(mascara_hex)
        destino = alcanzabilidad['localhost']
        destino['Destino' + str(numDestino)] = {'IP': ip_hex, 'Mascara': mascara_hex, 'SAs': {}}
        datosDestino = destino['Destino' + str(numDestino)]
        sistemas = datosDestino['SAs']
        numSistema = 0
        print("Ingrese los sistemas autónomos a seguir para llegar a este destino (0 para terminar)\n")
        while True:
            sa_str = input("Ingrese número de sistema (0 para terminar)\n")
            if sa_str == "0":
                break
            else:
                sa_hex = encode(sa_str)
                sistemas['SA' + str(numSistema) ] = sa_hex
                print(sa_hex)
                numSistema +=1
        numDestino+=1
        escribeArchivo("Se agregó el destino: "+str(ip_str), "Alcanzables.txt")

print("Alcanzables desde el principio: ", alcanzabilidad)
time.sleep(1)

listener = threading.Thread(target=escucha, name = 'router')
listener.start()
updater()
os.system('clear')

while True:
    menu()
    opcionMenu = input("inserte una opción >> ")
    if opcionMenu=="1":
        print ("")
        ip_str = input("Ingrese la dirección IP del nuevo vecino\n")
        ip_hex = encode(ip_str)
        print(ip_hex)
        mask_str = input("Ingrese la máscara del nuevo vecino\n")
        mask_hex = encode(mask_str)
        print(mask_hex)
        sa_str = input("Ingrese el sistema autonomo al que pertenece el nuevo vecino\n")
        sa_hex = hex(int(sa_str))[2:]
        l = len(sa_hex)
        l = 4-l
        for i in range(0,l):
            sa_hex = "0"+sa_hex
        sa_hex = sa_hex.encode()
        print(sa_hex)
        if ip_hex not in vecinos:
            solicitud = b"01"
            solicitud += encode(SA_HOST)
            solicitud += encode(IP_HOST)
            solicitud += encode(MSK_HOST)            
            ip_int = IP_HOST.split(".")
            msk_int = MSK_HOST.split(".")
            sa_int = str(SA_HOST)
            lista = [1]            
            lista.append(int(sa_int[0]))
            lista.append(int(sa_int[1]))
            for i in ip_int:
                lista.append(int(i))
            for i in msk_int:
                lista.append(int(i))
            respuesta = bytes(lista)
            print(respuesta)
            if confirmacion(respuesta,ip_str):
                vecinos[ip_hex] = {'estado': b"01",'mascara': mask_hex,'sa': sa_hex}
                escribeArchivo("Se agregó el vecino: "+ip_str, "Vecinos.txt")
                print("se agregó con éxito el vecino: ",ip_str)
            else:
                input("No se logro establecer conexion con : "+str(ip_str)+"\npulsa una tecla para continuar\n")
        else:
            print("Existe un vecino con esa direccion o fue desconectado anteriormente")
    elif opcionMenu=="2": 
        print("")
        ip_str = input("Ingrese la dirección IP del vecino a desconectar\n")
        ip_hex = encode(ip_str)
        print(ip_hex)
        mask_str = input("Ingrese la máscara del vecino a desconectar\n")
        mask_hex = encode(mask_str)
        sa_str = input("Ingrese el sistema autonomo al que pertenece el vecino a desconectar\n")
        sa_hex = encode(sa_str)
        print(sa_hex)
        # buscar en la tabla vecinos
        if ip_hex in vecinos:
            solicitud = b"03"
            solicitud += encode(SA_HOST)
            solicitud += encode(IP_HOST)
            solicitud += encode(MSK_HOST)
            ip_int = IP_HOST.split(".")
            msk_int = MSK_HOST.split(".")
            sa_int = int(SA_HOST)
            lista = [2]            
            lista.append(sa_int)
            for i in ip_int:
                lista.append(int(i))
            for i in msk_int:
                lista.append(int(i))
            respuesta = bytes(lista)
            print(respuesta)
            if not confirmacion(respuesta,ip_str):
                input("No se logro establecer conexion con : "+str(ip_str))
            vecino = vecinos[ip_hex]
            if vecino['mascara'] == mask_hex and vecino['sa'] == sa_hex:
                vecinos[ip_hex]['estado'] = b"00"
                escribeArchivo("Se desconectó el vecino: "+str(ip_str), "Vecinos.txt")
                del alcanzabilidad[ip_hex]
                print("se desconectó el vecino", ip_str)
            else:
                print("los demas datos sumistrados no corresponden a la ip "+str(ip_str))
        else:
            print("No Existe un vecino con la direccion "+str(ip_str))
    elif opcionMenu=="3":
        print ("")
        updater()
    elif opcionMenu == "4":
        print("Tabla alcanzabilidad:\n ")
        print("Alcanzables: ", alcanzabilidad)
    elif opcionMenu=="9":
        break
    else:
        print ("")
        print("No ha pulsado ninguna opción correcta...")
    input("Pulse una tecla para continuar")
    print("FIN")
os._exit(0)
