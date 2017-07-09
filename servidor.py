import socket
import os
import os.path
import threading
import time
import random
import sys
from _datetime import datetime

run = 0
vecinos = {}
alcanzabilidad = {}
alcanzabilidad['localhost'] = {}
#esto es completamente arbitrario
IP_HOST = "192.168.209.128"
MSK_HOST = "255.255.255.0"
SA_HOST = "2"

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

def escucha():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 57809))
    s.listen(1)

    while True:
        print("")
        print ("Esperando mensaje...")
        sc, addr = s.accept()
        recibido = sc.recv(1024)
        #se verifica si el tamaño del paquete es de una solicitud
        if len(recibido) == 22:
            #Se divide el paquete en sus respectivas partes
            tipo = recibido[0:2] #tipo de solicitud
            sa = recibido[2:6] #sistema autonomo
            ip = recibido[6:14]
            mascara = recibido[14:22]
            tipo = recibido[0:2]
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
                    print(addr)
                    sc.send(respuesta)
                    print("se envió respuesta de aceptación")
                    #se ingresa en la tabla vecinos,
                    #el tipo re refiere a si está conectado o no
                    vecinos[ip] = {'estado': tipo,'mascara': mascara,'sa': sa}
                    escribeArchivo("Se agregó el vecino: "+str(ip))
                    print("se agregó con éxito el vecino: ",ip)
            elif tipo == b"02":
                print("Solicitud de vecino aceptada")
                estado = b"01"
                vecinos[ip] = {'estado': estado,'mascara': mascara,'sa': sa}
                escribeArchivo("Se agregó el vecino: "+str(ip))
            elif tipo == b"03":
                print("se ingresó una solicitud de desconexión")
                #buscar en la tabla vecinos
                if ip in vecinos:
                    vecino = vecinos[ip]
                    if vecino['mascara'] == mascara and vecino['sa'] == sa:
                        vecino['estado'] = b"00"
                        escribeArchivo("Se desconectó el vecino: "+str(ip))
                        respuesta = b"04"
                        respuesta += encode(SA_HOST)
                        respuesta += encode(IP_HOST)
                        respuesta += encode(MSK_HOST)
                        sc.send(respuesta)
                        print("se desconectó el vecino", ip)
                else:
                    print("no existe un vecino con esa ip")
            elif tipo == b"03":
                print("Solicitud de desconexion aceptada")       
            else:
                print("Paquete con solicitud no reconocida")
            print("tabla vecinos: ",vecinos)
        else:
            print("Rec: ", recibido)
            #Se divide el paquete
            tipo = recibido[0:2]
            sa = recibido[2:6]
            ip = recibido[6:14]
            numDestinos = recibido[14:22]
            alcanzabilidad.update({ip: {}})
            cursor = 22
            destino = alcanzabilidad[ip]
            for i in range (0, int(numDestinos)):
                destino['Destino' + str(i)] = {'IP': recibido[cursor:cursor+8], 'Mascara': recibido[cursor+8:cursor+16], 'SAs': {}}
                datosDestino = destino['Destino' + str(i)]
                sistemas = datosDestino['SAs']
                cursorLista = cursor+16
                numSistemas = int(recibido[cursorLista:cursorLista + 4])
                print("numSistema: " + str(numSistemas))
                cursorLista = cursorLista + 4
                for j in range(0, numSistemas):
                    sistemas['SA' + str(j)] = recibido[cursorLista+(4*j):cursorLista+(4*j)+4]
                cursor = cursorLista+(4*(numSistemas-1))+4
            print("tabla alcanzabilidad: ", alcanzabilidad)
    sc.close()
    s.close()

def updater():
    update = threading.Timer(31.0, updater).start()
    paquete = ""
    for i in vecinos:
        for x in alcanzabilidad:
            paquete +=
        print(22)
    print("Hello")

def menu():
    os.system('clear')
    print ("Seleccione una opción")
    print ("\t1 - Enviar solicitud de vecino")
    print ("\t2 - Solicitar desconexión")
    print ("\t3 - Enviar información de alcanzabilidad")
    print ("\t9 - salir")

listener = threading.Thread(target=escucha, name = 'router')
listener.start()
updater()
input("Pulse una tecla para continuar")
os.system('clear')
print("Se necesita agregar destinos alcanzables (digite 0 para terminar)")

numDestino = 0
while True:
    ip = input("Ingrese la dirección IP del destino (0 para terminar)\n")
    if ip == "0":
        break
    else:
        ip = ip.split(".")
        for i in range(0,len(ip)):
            ip[i] = hex(int(ip[i]))[2:]
            if len(ip[i]) == 1:
                ip[i] = "0"+ip[i]
        ip = ''.join(ip)
        ip = ip.encode()
        print(ip)
        mascara = input("Ingrese la máscara del destino\n")
        mascara = mascara.split(".")
        for i in range(0,4):
            mascara[i] = hex(int(mascara[i]))[2:]
            if len(mascara[i]) == 1:
                mascara[i] = "0"+mascara[i]
        mascara = ''.join(mascara)
        mascara = mascara.encode()
        print(mascara)
        destino = alcanzabilidad['localhost']
        destino['Destino' + str(numDestino)] = {'IP': ip, 'Mascara': mascara, 'SAs': {}}
        datosDestino = destino['Destino' + str(numDestino)]
        sistemas = datosDestino['SAs']
        numSistema = 0
        print("Ingrese los sistemas autónomos a seguir para llegar a este destino (0 para terminar)\n")
        while True:
            sa = input("Ingrese número de sistema (0 para terminar)\n")
            if sa == "0":
                break
            else:
                sa = hex(int(sa))[2:]
                sistemas['SA' + str(numSistema) ] = sa
                l = len(sa)
                l = 4-l
                for i in range(0,l):
                    sa = "0"+sa
                sa = sa.encode()
                print(sa)
                numSistema +=1
        numDestino+=1

print("Alcanzables desde el principio: ", alcanzabilidad)
time.sleep(1)

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
        #se verifica que el
        if ip_hex not in vecinos:
            solicitud = b"01"
            solicitud += encode(SA_HOST)
            solicitud += encode(IP_HOST)
            solicitud += encode(MSK_HOST)
            print(solicitud)
            if confirmacion(solicitud,ip_str):
                vecinos[ip_hex] = {'estado': b"01",'mascara': mask_hex,'sa': sa_hex}
                escribeArchivo("Se agregó el vecino: "+ip_str)
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
            if not confirmacion(solicitud,ip_str):
                input("No se logro establecer conexion con : "+str(ip_str))
            vecino = vecinos[ip_hex]
            if vecino['mascara'] == mask_hex and vecino['sa'] == sa_hex:
                vecinos[ip_hex]['estado'] = b"00"
                escribeArchivo("Se desconectó el vecino: "+str(ip_str))
                print("se desconectó el vecino", ip_str)
            else:
                print("los demas datos sumistrados no corresponden a la ip "+str(ip_str))
        else:
            print("No Existe un vecino con la direccion "+str(ip_str))
    elif opcionMenu=="3":
        print ("")
        print("Ha pulsado la opción 3...")
    elif opcionMenu=="9":

        break
    else:
        print ("")
        print("No ha pulsado ninguna opción correcta...")
    input("Pulse una tecla para continuar")
    print("FIN")
os._exit(0)