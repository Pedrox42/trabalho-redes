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
finish = False
while not finish:

    # Manda um pacote de sinal para tentar iniciar a conexão com o servidor
    if not started_connection:
        # file_name = input("Digite o nome do arquivo a ser enviado: ")
        file_name = "teste.pdf"
        print("Tamanho do arquivo: {}".format(os.stat(file_name).st_size))
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

    # Conectou com o servidor
    else:
        # Enviar o pacote para fazer o setup para o arquivo que deve ser escrito para o servidor
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
                    next_packet_to_send_id = packet_id
                else:
                    packet_id = 1

        # Envia o arquivo em pacotes para o servidor
        if connected and setup_success:
            start_from_byte = 0
            client_buffer = buffer.Buffer(file_name, start_from_byte, packet_id)

            while connected and not client_buffer.is_empty():
                next_packet_to_send = client_buffer.find_packet_by_id(next_packet_to_send_id)
                print("Enviando pacote de número {}".format(next_packet_to_send.packet_id))
                bytes_to_send = pickle.dumps(next_packet_to_send)
                UDP_client_socket.sendto(bytes_to_send, server_address_port)

                last_packet_last_byte = client_buffer.current_byte
                file = open(file_name, "rb")
                file.read(last_packet_last_byte)

                packet_id = client_buffer.packets[-1].packet_id + 1
                if client_buffer.free_space() > 0:
                    byte = file.read(client_buffer.free_space() - (math.ceil(packet_id.bit_length() / 8)))
                    if byte:
                        client_buffer.add_packet(byte, packet_id)

                try:
                    bytes_address_pair = UDP_client_socket.recvfrom(buffer.buffer_size)
                except BlockingIOError:
                    pass
                except socket.timeout:
                    UDP_client_socket.sendto(bytes_to_send, server_address_port)
                else:
                    response_packet = pickle.loads(bytes_address_pair[0])
                    response_packet_id = response_packet.packet_id
                    next_packet_to_send_id = response_packet_id
                    last_confirmed_packet = response_packet_id - 1
                    packet_to_remove = client_buffer.find_packet_by_id(last_confirmed_packet)
                    if packet_to_remove is not None:
                        client_buffer.packets.remove(packet_to_remove)

            # Envia um pacote de sin (fin) para fazer o processo de finalização da conexão
            packet_id += 1
            fin_packet = packets.SignalPacket(packet_id=packet_id, syn=False, fin=True, ack=False)
            bytes_to_send = pickle.dumps(fin_packet)
            UDP_client_socket.sendto(bytes_to_send, server_address_port)
            print("enviou o fin para o server")
            try:
                bytes_address_pair = UDP_client_socket.recvfrom(buffer.buffer_size)
            except BlockingIOError:
                pass
            except socket.timeout:
                UDP_client_socket.sendto(bytes_to_send, server_address_port)
                print("deu timeout e reenviamos o fin para o server")
            else:
                server_message = bytes_address_pair[0]
                server_message = pickle.loads(server_message)
                if isinstance(server_message, packets.SignalPacket) and server_message.get_type() == "finack":
                    packet_id += 1
                    last_ack = packets.SignalPacket(packet_id=packet_id, syn=False, fin=False, ack=True)
                    bytes_to_send = pickle.dumps(last_ack)
                    UDP_client_socket.sendto(bytes_to_send, server_address_port)

                    print("recebeu o finack do server, mandou o last_ack e resetou as variáveis")
                    packet_id = 0
                    started_connection = False
                    connected = False
                    setup_success = False
                    finish = True
