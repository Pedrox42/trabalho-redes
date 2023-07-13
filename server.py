import socket
import packets
import buffer
import pickle

localIP = "127.0.0.1"
localPort = 20001
bufferSize = buffer.buffer_size

UDP_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDP_server_socket.bind((localIP, localPort))
UDP_server_socket.settimeout(5)
print("Servidor iniciado, aguardando conexão.")

current_sequence = 0
last_written_packet = 0
next_packet = 0
connected = False
setup_success = False
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
            else:
                ack = packets.SignalPacket(packet_id=next_packet, syn=False, fin=False, ack=True)
        else:
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
                continue

            # Recebeu um pacote de arquivo que deve ser escrito
            if setup_success and isinstance(client_message, packets.Packet):
                print(client_message.packet_id)
                f = open(file_to_write_name, "ab")
                f.write(client_message.content)
                last_written_packet = client_message.packet_id
                next_packet = last_written_packet + 1
                ack = packets.SignalPacket(packet_id=next_packet, syn=False, fin=False, ack=True)
                bytes_to_send = pickle.dumps(ack)
                UDP_server_socket.sendto(bytes_to_send, client_address_port)
                f.close()
                continue

            # Recebeu um pacote de sinal do cliente para finalizar a conexão
            if setup_success and isinstance(client_message, packets.SignalPacket) and client_message.get_type() == "fin":
                current_sequence += 1
                finack = packets.SignalPacket(packet_id=current_sequence, syn=False, fin=True, ack=True)
                bytes_to_send = pickle.dumps(finack)
                UDP_server_socket.sendto(bytes_to_send, client_address_port)
                print("server recebeu fin e enviou finack para client")
                continue

            # Recebeu um pacote de sinal de ack do cliente para confirmar a finalização da conexão
            if setup_success and isinstance(client_message, packets.SignalPacket) and client_message.get_type() == "ack":
                print("recebemos o last_ack do client")
                current_sequence = 0
                connected = False
                setup_success = False
