# Jose Antonio Garcia Linares
# Uvus: josgarlin1

import socket
import sys
import time

# Comprobamos que el numero de argumentos es correcto
if (len(sys.argv) != 2):
    print "Error. Uso: server error"
    sys.exit()

# Creamos 2 variables donde guardar la IP y el puerto del servidor
IP_servidor = ''
puerto_servidor = 55000

# Creamos el socket UDP
try:
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print "Error al crear el socket"
    sys.exit()

# Asignamos el puerto al socket
socket_udp.bind((IP_servidor, puerto_servidor))

nivel_error = sys.argv[1]

print "Nivel de error: " + nivel_error

if (nivel_error == '0' or nivel_error == '1' or nivel_error == '2'):
    print "Servidor a la escucha de registro en puerto: " + str(puerto_servidor)

    lista = "["
    LISTA = ''
    i = 0
    while 1:
        msg, (addr, port) = socket_udp.recvfrom(100)
        print "Recibido: " + msg + " desde (" + repr(addr) + ", " + str(port) + ")"

        if (msg != 'LISTA'):
            print "Solicitado el registro:"

	    if (nivel_error == '1'):
	        time.sleep(5)
	    socket_udp.sendto('ok', (addr, port))

	    if (i == 0):
	        lista += "[" + repr(addr) + ", '" + msg + "']"
		LISTA += addr + "," + msg
	    else:
		lista += ", [" + repr(addr) + ", '" + msg + "']"
		LISTA += ";" + addr + "," + msg
        if (msg == 'LISTA'):
            print "Solicitada lista de registrados. Envio lista:"

	    if (nivel_error == '2'):
		time.sleep(5)
	    socket_udp.sendto(LISTA, (addr, port))
	    print LISTA

        print "Clientes Registrados:\n" + lista + "]"
        i += 1
else:
    print "Nivel de error no valido"
    socket_udp.close()
    sys.exit()
