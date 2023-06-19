import os
import socket
import buffer
import pickle

buffers = []
serverAddressPort = ("127.0.0.1", 20001)
while True:
    file_name = input("Digite o nome do arquivo a ser enviado: ")
    byte = True

    print("Tamanho do arquivo: " + str(os.stat(file_name).st_size))

    start_from_byte = 0
    while byte:
        current_buffer = buffer.Buffer(file_name, start_from_byte)
        buffers.append(current_buffer)

        file = open(file_name, "rb")
        start_from_byte += current_buffer.total_file_read_size()
        file.read(start_from_byte)
        byte = file.read(buffer.buffer_size)
        file.close()

    print("Total de buffers: " + str(len(buffers)))

    total_packets = 0
    total_packets_size = 0

    for current_buffer in buffers:
        total_packets += len(current_buffer.packets)
        for packet in current_buffer.packets:
            total_packets_size += len(packet)

    print("Total de pacotes: " + str(total_packets))
    print("Tamanho total de pacotes: " + str(total_packets_size))

    for current_buffer in list(buffers):
        for packet in current_buffer.packets:
            bytesToSend = pickle.dumps(packet)
            UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        buffers.remove(current_buffer)

    print("Total de buffers: " + str(len(buffers)))

