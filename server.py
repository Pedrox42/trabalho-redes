import random
import socket
import packets
import buffers
import pickle

localIP = "127.0.0.1"
localPort = 20001
bufferSize = buffers.buffer_size

UDP_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDP_server_socket.bind((localIP, localPort))
UDP_server_socket.settimeout(0.008)
print("Servidor iniciado, aguardando conexão.")
current_sequence = 0
i = 0
ending_connection_timeout_counter = 0
client_address_port = ()
connected = False
setup_success = False
storage_buffer = buffers.ServerBuffer(bufferSize)

while True:
    # Esperando conexão do cliente
    if not connected:
        try:
            bytes_address_pair = UDP_server_socket.recvfrom(bufferSize)
        except BlockingIOError:
            pass
        except socket.timeout:
            pass
        else:
            client_message = bytes_address_pair[0]
            client_address_port = bytes_address_pair[1]
            client_message = pickle.loads(client_message)

            if isinstance(client_message, packets.SignalPacket) and not connected:
                if client_message.get_type() == "syn":
                    synack = packets.SignalPacket(packet_id=current_sequence, syn=True, fin=False, ack=True)
                    bytes_to_send = pickle.dumps(synack)
                    UDP_server_socket.sendto(bytes_to_send, client_address_port)
                    current_sequence += 1

                if client_message.get_type() == "ack":
                    connected = True
                    current_sequence += 1

    # Conectou com o cliente
    else:
        try:
            bytes_address_pair = UDP_server_socket.recvfrom(bufferSize)
        except BlockingIOError:
            pass
        except socket.timeout:
            if not setup_success:
                ack = packets.SignalPacket(packet_id=current_sequence, syn=False, fin=False, ack=True)
                bytes_to_send = pickle.dumps(ack)
                UDP_server_socket.sendto(bytes_to_send, client_address_port)
                i += 1
            else:
                ack = packets.SignalPacket(packet_id=next_packet, syn=False, fin=False, ack=True)
                bytes_to_send = pickle.dumps(ack)
                UDP_server_socket.sendto(bytes_to_send, client_address_port)
                print("Enviando ack pedindo pacote: {}, i = {}".format(next_packet, i))
                i += 1
            if ending_connection:
                ending_connection_timeout_counter += 1
            if ending_connection_timeout_counter > 3:
                print("Não recebemos o last ack do cliente e já pedimos 3 vezes. Fechando conexão.")
                current_sequence = 0
                ending_connection_timeout_counter = 0
                connected = False
                setup_success = False
                ending_connection = False
                f.close()
                continue
        else:
            if random.randint(0, 100) <= 10:
                continue
            # Fazendo o setup para receber o arquivo
            client_message = bytes_address_pair[0]
            client_address_port = bytes_address_pair[1]
            client_message = pickle.loads(client_message)
            if not setup_success and isinstance(client_message, packets.Packet) and client_message.packet_id == 2:
                file_to_write_name = "received_" + str(client_message.content)
                current_sequence += 1
                ack = packets.SignalPacket(packet_id=current_sequence, syn=False, fin=False, ack=True)
                bytes_to_send = pickle.dumps(ack)
                UDP_server_socket.sendto(bytes_to_send, client_address_port)
                setup_success = True
                ending_connection = False
                last_written_packet = 2
                next_packet = 3
                continue

            # Recebeu um pacote de arquivo que deve ser escrito
            if setup_success and isinstance(client_message, packets.Packet) and not ending_connection:
                # Armazenar o pacote se não for pra escrever, escrever até ter que parar de novo
                if storage_buffer.find_packet_by_id(client_message.packet_id) is None and client_message.packet_id > last_written_packet:
                    storage_buffer.add_packet(client_message)

                f = open(file_to_write_name, "ab")
                for packet in storage_buffer.packets:
                    if last_written_packet + 1 == packet.packet_id:
                        print(packet.packet_id)
                        f.write(packet.content)
                        last_written_packet = packet.packet_id
                        next_packet = last_written_packet + 1
                        storage_buffer.packets.remove(packet)
                    else:
                        break
                ack = packets.SignalPacket(packet_id=next_packet, syn=False, fin=False, ack=True)
                bytes_to_send = pickle.dumps(ack)
                UDP_server_socket.sendto(bytes_to_send, client_address_port)
                continue

            # Recebeu um pacote de sinal do cliente para finalizar a conexão
            if setup_success and isinstance(client_message, packets.SignalPacket) and client_message.get_type() == "fin":
                current_sequence += 1
                finack = packets.SignalPacket(packet_id=current_sequence, syn=False, fin=True, ack=True)
                bytes_to_send = pickle.dumps(finack)
                UDP_server_socket.sendto(bytes_to_send, client_address_port)
                print("server recebeu fin e enviou finack para client")
                ending_connection = True
                continue

            # Recebeu um pacote de sinal de ack do cliente para confirmar a finalização da conexão
            if setup_success and isinstance(client_message, packets.SignalPacket) and client_message.get_type() == "ack":
                print("recebemos o last_ack do client")
                current_sequence = 0
                connected = False
                setup_success = False
                ending_connection = False
                ending_connection_timeout_counter = 0
                f.close()

