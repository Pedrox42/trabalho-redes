import socket
import packets
import buffer
import pickle

localIP = "127.0.0.1"
localPort = 20001
bufferSize = buffer.buffer_size

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))
print("Servidor UDP up e escutando...")

packet_id = 0
connected = False
while True:
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    clientAddressPort = bytesAddressPair[1]
    clientMsg = pickle.loads(message)

    if isinstance(clientMsg, packets.SignalPacket):
        print(clientMsg.get_type())
        if clientMsg.get_type() == "syn":
            synack = packets.SignalPacket(packet_id=packet_id, syn=True, fin=False, ack=True)
            bytesToSend = pickle.dumps(synack)
            UDPServerSocket.sendto(bytesToSend, clientAddressPort)

        if clientMsg.get_type() == "ack":
            connected = True

    while connected:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        clientAddressPort = bytesAddressPair[1]
        clientMsg = pickle.loads(message)

        if isinstance(clientMsg, packets.Packet):
            print(clientMsg.packet_id)
            print(clientMsg.content)
        # UDPServerSocket.sendto(pickle.dumps(1), clientAddressPort)
        #
        # print(clientMsg.packet_id)
        # f = open("teste-recebido.png", "ab")
        # f.write(clientMsg.content)
        # f.close()
