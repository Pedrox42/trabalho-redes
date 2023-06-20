import socket
import buffer
import pickle

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 200000
# bufferSize = buffer.buffer_size

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))
print("Servidor UDP up e escutando...")

while True:
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    clientMsg = pickle.loads(message)

    print(clientMsg.packet_id)
    f = open("C:/Users/pedri/Documents/Redes/teste-recebido.png", "ab")
    f.write(clientMsg.content)
    f.close()
