# Jose Antonio Garcia Linares
# Uvus: josgarlin1

import socket
import sys
import random
import os
import os.path
import select
import time
import hashlib

#Comprobamos que el numero de argumentos es correcto
if len(sys.argv) > 3:
    print "Error. Uso: cliente IP [fichero]"
    sys.exit();

#Si el numero de argumentos es correcto, comprobamos si existe el fichero
fichero = True
if len(sys.argv) == 2:
    fichero = False

if fichero == True:
    if os.path.isfile(sys.argv[2]) == False:
        print "Error.Fichero " + sys.argv[2] + " inexistente"
        sys.exit()

# I
#Creamos 2 variables donde guardamos la IP y el puerto del servidor
IP_servidor = sys.argv[1]
puerto_servidor = 55000

# II
#Creamos 2 variables donde guardamos la IP y el puerto del cliente
IP_cliente = '127.0.0.1'
puerto_cliente = random.randint(45000, 55000)

# III
#Creacion del socket UDP con el que comunicarnos con el servidor
try:
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print "Error al crear el socket"
    sys.exit()

#Enviamos al servidor el puerto TCP del cliente que pondra en escucha
socket_udp.sendto(str(puerto_cliente), (IP_servidor, puerto_servidor))

# IV
#Si pasan 3 segundos sin que el servidor confirme, dara error y cerramos el cliente
rlist, wlist, elist = select.select([socket_udp], [], [], 3)
if [rlist, wlist, elist] == [[], [], []]:
    print "Error: no hay respuesta por parte del servidor " + repr(IP_servidor) + " en el puerto " + str(puerto_servidor)
    sys.exit()
#En caso contrario, el servidor envia mensaje de confirmacion 'ok'
else:
    for sock in rlist:
        msg, (adrr, port) = socket_udp.recvfrom(100)
        if msg == 'ok':

            # V
            #Creamos socket TCP y lo ponemos en escucha
            try:
                socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except socket.error:
                print "Error al crear el socket"
                sys.exit()

            socket_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socket_tcp.bind((IP_cliente, puerto_cliente))
            socket_tcp.listen(100)

            # VI
            #Para los clientes que quieran distribuir un fichero, enviamos el segundo mensaje UDP al servidor
            if fichero == True:
                socket_udp.sendto('LISTA', (IP_servidor, puerto_servidor))

                #Si pasan 3 segundos sin recibir respuesta del servidor
                rlist, wlist, elist = select.select([socket_udp], [], [], 3)
                if [rlist, wlist, elist] == [[], [], []]:
                    print "Error: no hay respuesta por parte del servidor " + repr(IP_servidor) + " en el puerto " + str(puerto_servidor)
                    socket_tcp.close()
                    socket_udp.close()
                    sys.exit()

                #Si recibimos la lista por parte del servidor
                for sock in rlist:
                    lista, (adrr, port) = socket_udp.recvfrom(100)

                    #Hacemos la division de la lista
                    cliente = lista.split(';')
                    i = 0
                    while i < len(cliente):
                        division = cliente[i].split(',')
                        IP = division[0]
                        puerto = int(division[1])
                        i += 1

                        # IX
                        #Vamos estableciendo la conexion TCP en los clientes de la lista
                        error_conexion = False

                        #Si la ip y el puerto es del cliente que quiere distribuir el fichero no se hace nada
                        if IP == IP_cliente and puerto == puerto_cliente:
                            time.sleep(0)
                        else:
                            try:
                                socket1_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            except socket.error:
                                print "Error al crear el socket"
                                sys.exit()

                            try:
                                socket1_tcp.connect((IP, puerto))
                            except:
                                error_conexion = True
                                pass
                            if error_conexion == False:
                                #Calculamos el tamano del fichero y concatenamos con el nombre
                                statinfo = os.stat(sys.argv[2])
                                tam = statinfo.st_size
                                mensaje = sys.argv[2] + ' ' + str(tam)

                                #Mandamos el mensaje al cliente de la lista
                                try:
                                    socket1_tcp.sendall(mensaje)
                                except socket.error:
                                    print "Envio fallido"
                                    sys.exit()

                                #Si pasan 3 segundos sin respuesta del otro cliente
                                rlist, wlist, elist = select.select([socket1_tcp], [], [], 3)
                                if [rlist, wlist, elist] == [[], [], []]:
                                    print "Error: no hay respuesta por parte del cliente " + repr(IP) + " en el puerto " + str(puerto)
                                    socket1_tcp.close()
                                    socket_tcp.close()
                                    socket_udp.close()
                                    sys.exit()

                                #En caso contrario, comprobamos la respuesta del cliente
                                msg2 = socket1_tcp.recv(1024)
                                if msg2 == 'ok':
                                    #Abrimos el fichero, leemos su contenido y enviamos dicho contenido por la misma conexion TCP establecida
                                    nombre_fichero = sys.argv[2]
                                    f = open(nombre_fichero, "rb")
                                    fichero_txt = f.read()
                                    f.close()
                                    socket1_tcp.sendall(fichero_txt)

                                    #Si en 10 segundos no recibimos transfer done
                                    rlist, wlist, elist = select.select([socket1_tcp], [], [], 10)
                                    if [rlist, wlist, elist] == [[], [], []]:
                                        print "Error en la transferencia con cliente " + repr(IP)
                                        socket1_tcp.close()
                                        socket_tcp.close()
                                        socker_udp.close()
                                        sys.exit()

                                    #En el caso de recibir algo, comprobamos si es transfer done
                                    msg3 = socket1_tcp.recv(1024)
                                    if msg3 != 'transfer done':
                                        print "Error en la transferencia con cliente " + repr(IP)
                                        socket1_tcp.close()
                                        socket_tcp.close()
                                        socket_udp.close()
                                        sys.exit()
                                    else:
                                        socket1_tcp.close()

            # X
            #Aceptamos todas las conexiones con los clientes registrados en el servidor pero que no quieren distribuir fichero, y copien los ficheros que le mandan
            while 1:
                try:
                    global server
                    global desc
                    connect,ip = socket_tcp.accept()
                    server.settimeout(.1)
                    desc.append(connect)
                except:
                    pass
                time.sleep(1)

                #Recibimos el nombre del fichero y su tamano
                try:
                    fichytam = connect.recv(1024)
                    connect.settimeout(.1)
                except:
                    desc.remove(connect)

                #Enviamos mensaje de confirmacion 'ok'
                try:
                    connect.sendall('ok')
                except:
                    pass

                time.sleep(1)

                #Recibimos el contenido del fichero
                try:
                    contenido = connect.recv(1024)
                    connect.settimeout(.1)
                except:
                    desc.remove(connect)

                #Enviamos 'transfer done'
                try:
                    connect.sendall('transfer done')
                except:
                    pass

                #Dividimos el mensaje recibido (contiene el nombre y tamano del fichero)
                try:
                    nom_fich = fichytam.split(' ')[0]
                    nom_fich1 = nom_fich.strip('./')
                    tam_fich = int(fichytam.split(' ')[1]) #Tamano en bytes

                    #Copiamos el fichero
                    copiar = open(nom_fich1, 'w')
                    copiar.write(contenido)
                    copiar.close()
                except:
                    pass

        else:
            socket_udp.close()
            sys.exit()
