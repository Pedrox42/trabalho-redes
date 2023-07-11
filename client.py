import os
import socket
import buffer
import pickle
import math

import packets

server_address_port = ("127.0.0.1", 20001)
UDP_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDP_client_socket.setblocking(False)
UDP_client_socket.settimeout(5)
packet_id = 0
started_connection = False
connected = False
setup_success = False
while True:
    # file_name = input("Digite o nome do arquivo a ser enviado: ")
    file_name = "teste.png"
    print("Tamanho do arquivo: {}".format(os.stat(file_name).st_size))

    if not started_connection:
        syn_packet = packets.SignalPacket(packet_id=packet_id, syn=True, fin=False, ack=False)
        bytes_to_send = pickle.dumps(syn_packet)
        UDP_client_socket.sendto(bytes_to_send, server_address_port)
        try:
            bytes_address_pair = UDP_client_socket.recvfrom(buffer.buffer_size)
        except BlockingIOError:
            pass
        except socket.timeout:
            UDP_client_socket.sendto(bytes_to_send, server_address_port)
        else:
            server_message = bytes_address_pair[0]
            server_message = pickle.loads(server_message)
            if isinstance(server_message, packets.SignalPacket):
                if server_message.get_type() == "synack":
                    started_connection = True
                    packet_id += 1

    else:
        if not setup_success:
            ack = packets.SignalPacket(packet_id=packet_id, syn=False, fin=False, ack=True)
            bytes_to_send = pickle.dumps(ack)
            UDP_client_socket.sendto(bytes_to_send, server_address_port)
            packet_id += 1

            setup_packet = packets.Packet(file_name, packet_id)
            bytes_to_send = pickle.dumps(setup_packet)
            UDP_client_socket.sendto(bytes_to_send, server_address_port)
            try:
                bytes_address_pair = UDP_client_socket.recvfrom(buffer.buffer_size)
            except BlockingIOError:
                pass
            except socket.timeout:
                packet_id = 1
            else:
                server_message = bytes_address_pair[0]
                server_message = pickle.loads(server_message)
                if isinstance(server_message, packets.SignalPacket) and server_message.packet_id == 3:
                    packet_id += 1
                    connected = True
                    setup_success = True
                else:
                    packet_id = 1

        if connected and setup_success:
            start_from_byte = 0
            client_buffer = buffer.Buffer(file_name, start_from_byte, packet_id)

            while connected and not client_buffer.is_empty():
                for packet in list(client_buffer.packets):
                    print("Enviando pacote de número {}".format(packet.packet_id))
                    bytes_to_send = pickle.dumps(packet)
                    UDP_client_socket.sendto(bytes_to_send, server_address_port)

                    last_packet_last_byte = client_buffer.current_byte
                    file = open(file_name, "rb")
                    file.read(last_packet_last_byte)

                    packet_id = client_buffer.packets[-1].packet_id + 1
                    if client_buffer.free_space() > 0:
                        byte = file.read(client_buffer.free_space() - (math.ceil(packet_id.bit_length() / 8)))
                        if byte:
                            client_buffer.add_packet(byte, packet_id)

                    # try:
                    #     bytes_address_pair = UDP_client_socket.recvfrom(buffer.buffer_size)
                    # except BlockingIOError:
                    #     pass
                    # else:
                    #     response_packet = pickle.loads(bytes_address_pair[0])
                    #     response_packet_id = response_packet.packet_id
                    client_buffer.packets.remove(packet)
                # Fin -> connected = False, started_connection = False, setup_success = False
            break

