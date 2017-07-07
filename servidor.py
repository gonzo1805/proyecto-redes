import socket
import os
import os.path
import threading
import time
import random
from _datetime import datetime

run = 0
vecinos = {}
alcanzabilidad = {}
alcanzabilidad['localhost'] = {}
#esto es completamente arbitrario
IP_HOST = str(random.randrange(256)) + "." + str(random.randrange(256)) + "." + str(random.randrange(256)) + "." + str(random.randrange(256))
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
    s = socket.socket()
    s.settimeout(5)
    try:
        s.connect((ip, 57809))
        s.send(paquete)
    except socket.timeout:
        return 0
    except:
        raise
    else:
        return 1

def encode(direccion):
    direccion = direccion.split(".")
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
        else:
            print("Rec: ", recibido)
            #Se divide el paquete
            tipo = recibido[0:2]
            sa = recibido[2:6]
            ip = recibido[6:14]
            tam = recibido[14:22]
            alcanzabilidad.update({ip: {}})
            #alcanzabilidad[ip] = {'tipo' : tipo, 'sa' : sa, 'Alcanzables': tam}
            num = 0
            pos = 22
            vectorR = alcanzabilidad[ip]
            #alcanzables = alcanzabilidad[ip]
            for i in range (0, int(tam)):

                vectorR['Destino' + str(num)] = {'IP': recibido[pos:pos+8], 'Mascara': recibido[pos+8:pos+16], 'SAs': {}}
                #alcanzables['alcanzable' + str(num)] = recibido[pos+(16*i):pos+(16*i)+8]
                #alcanzables['mascara' + str(num)] = recibido[pos+(16*i)+8:pos+(16*i)+16]
                destData = vectorR['Destino' + str(num)]
                alcanzables = destData['SAs']
                pos2 = pos+16
                numSas = int(recibido[pos2:pos2 + 4])
                print("NUM: " + str(numSas))
                pos2 = pos2 + 4
                saID = 0
                #sistemas = alcanzables['alcanzable' + str(num)]
                for j in range(0, int(numSas)):
                    alcanzables['SA' + str(saID)] = recibido[pos2+(4*j):pos2+(4*j)+4]
                num += 1
                pos = pos2+(4*(int(numSas)-1))+4
                #pos = (pos+(16*i)+16)+4+(
            num = pos+(16*(int(tam)-1))+16
            #print("num", num)
            #alcanzables['SAs'] = recibido[num:num+4]
            #alcanzables['SA0'] = recibido[num+4:num+8]
            print("tabla alcanzabilidad: ", alcanzabilidad)
    sc.close()
    s.close()

listener = threading.Thread(target=escucha, name = 'router')
listener.start()

def menu():
    os.system('clear')
    print ("Seleccione una opción")
    print ("\t1 - Enviar solicitud de vecino")
    print ("\t2 - Solicitar desconexión")
    print ("\t3 - Enviar información de alcanzabilidad")
    print ("\t9 - salir")

os.system('clear')
print("Se necesita agregar destinos alcanzables (digite 0 para terminar)")

curDest = 0
while True:
    ip = input("Ingrese la dirección IP del destino\n")
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
        #alcanzabilidad['localhost'] = {'Destino' + str(curDest): {}}
        vectorR = alcanzabilidad['localhost']
        vectorR['Destino' + str(curDest)] = {'IP': ip, 'Mascara': mascara, 'SAs': {}}
        destData = vectorR['Destino' + str(curDest)]
        alcanzables = destData['SAs']
        num = 0
        while True:
            sa = input("Ingrese los sistemas autónomos a seguir para llegar a este destino (0 para terminar)\n")
            if sa == "0":
                break
            else:
                sa = hex(int(sa))[2:]
                alcanzables['Sa' + str(num) ] = sa
                l = len(sa)
                l = 4-l
                for i in range(0,l):
                    sa = "0"+sa
                sa = sa.encode()
                print(sa)
                num +=1
        curDest+=1

print("Alcanzables desde el principio: ", alcanzabilidad)
time.sleep(5)

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
                estado = b"01"
                vecinos[ip] = {'estado': estado,'mascara': mask_hex,'sa': sa_hex}
                escribeArchivo("Se agregó el vecino: "+str(ip_str))
                input("Se agregó con éxito el vecino: "+str(ip_str)+"\npulsa una tecla para continuar\n")
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
        sa_hex = hex(int(sa_str))[2:]
        l = len(sa_hex)
        l = 4-l
        for i in range(0,l):
            sa_hex = "0"+sa_hex
        sa_hex = sa_hex.encode()
        print(sa_hex)
        # buscar en la tabla vecinos
        if ip_hex in vecinos:
            vecino = vecinos[ip_hex]
            if vecino['mascara'] == mask_hex and vecino['sa'] == sa_hex:
                vecinos[ip_hex]['estado'] = b"00"
                escribeArchivo("Se desconectó el vecino: "+str(ip_str))
                print("se desconectó el vecino", ip_str)
        input("Pulsa una tecla para continuar")
    elif opcionMenu=="3":
        print ("")
        input("Ha pulsado la opción 3...\npulse una tecla para continuar")
    elif opcionMenu=="9":
        break
    else:
        print ("")
        input("No ha pulsado ninguna opción correcta...\npulse una tecla para continuar")
print ("Fin")
