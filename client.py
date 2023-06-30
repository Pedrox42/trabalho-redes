import os
import socket
import buffer
import pickle
import math

serverAddressPort = ("127.0.0.1", 20001)
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.setblocking(False)
while True:
    # file_name = input("Digite o nome do arquivo a ser enviado: ")
    file_name = "teste.pdf"
    print("Tamanho do arquivo: {}".format(os.stat(file_name).st_size))

    start_from_byte = 0
    client_buffer = buffer.Buffer(file_name, start_from_byte)

    while not client_buffer.is_empty():
        for packet in list(client_buffer.packets):
            print("Enviando pacote de número {}".format(packet.packet_id))
            bytesToSend = pickle.dumps(packet)
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)

            last_packet_first_byte = client_buffer.current_byte
            last_packet_last_byte = last_packet_first_byte + len(client_buffer.packets[-1].content)
            file = open(file_name, "rb")
            file.read(last_packet_last_byte)

            packet_id = client_buffer.packets[-1].packet_id + 1
            if client_buffer.free_space() > 0:
                byte = file.read(client_buffer.free_space() - (math.ceil(packet_id.bit_length() / 8)))
                if byte:
                    client_buffer.add_packet(byte, packet_id)

            # try:
            #     bytesAddressPair = UDPClientSocket.recvfrom(buffer.buffer_size)
            # except BlockingIOError:
            #     pass
            # else:
            #     response_packet = pickle.loads(bytesAddressPair[0])
            #     response_packet_id = response_packet.packet_id
            client_buffer.packets.remove(packet)
    break

