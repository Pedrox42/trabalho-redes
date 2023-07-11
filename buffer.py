import math
import packets

pickle_dump_size = 69
max_packet_size = 1024 - pickle_dump_size
buffer_size = 30 * max_packet_size
# Último pacote -> FIN -> FINACK -> ACK -> Finaliza
# Fazer o ack de confirmação
# Fazer a janela deslizante


class Buffer:
    def __init__(self, file_name, start_from_byte, current_packet_id):
        self.packets = []
        self.current_byte = start_from_byte
        self.start_from_byte = start_from_byte
        self.arrange_packets(file_name, start_from_byte, current_packet_id)

    def is_empty(self):
        return len(self.packets) == 0

    def is_full(self):
        return math.ceil(buffer_size / max_packet_size) <= len(self.packets)

    def free_space(self):
        free_size = buffer_size
        for packet in self.packets:
            free_size -= len(packet)
        return free_size

    def add_packet(self, content, packet_id):
        if not self.is_full():
            packet = packets.Packet(content, packet_id)
            self.packets.append(packet)
            self.current_byte += len(content)
        else:
            print("Buffer cheio!")

    def arrange_packets(self, file_name, start_from_byte, current_packet_id):
        file = open(file_name, "rb")

        file.read(start_from_byte)
        byte = file.read(max_packet_size)

        packet_id = current_packet_id

        while byte:
            if not self.is_full():
                self.add_packet(byte, packet_id)
                packet_id += 1
                byte = file.read(max_packet_size - (math.ceil(packet_id.bit_length() / 8)))
            else:
                break

        file.close()

    def total_file_read_size(self):
        read_size = 0
        for packet in self.packets:
            read_size += len(packet.content)
        return read_size
