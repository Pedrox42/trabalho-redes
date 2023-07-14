import math
import packets

pickle_dump_size = 69
max_packet_size = 1024 - pickle_dump_size
buffer_size = 30 * max_packet_size

# Deixar o timeout do servidor menor que do cliente, pra mandar o ack mais cedo e pedir o pacote novamente caso perca
# Fazer a janela deslizante


class Buffer:

    def __init__(self, size):
        self.size = size
        self.packets = []

    def is_empty(self):
        return len(self.packets) == 0

    def is_full(self):
        return math.ceil(self.size / max_packet_size) <= len(self.packets)

    def free_space(self):
        free_size = buffer_size
        for packet in self.packets:
            free_size -= len(packet)
        return free_size

    def find_packet_by_id(self, packet_id):
        for packet in self.packets:
            if packet.packet_id == packet_id:
                return packet
        return None


class ClientBuffer(Buffer):
    def __init__(self, size, file_name, start_from_byte, current_packet_id):
        super().__init__(size)
        self.current_byte = start_from_byte
        self.start_from_byte = start_from_byte
        self.arrange_packets(file_name, start_from_byte, current_packet_id)

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


class ServerBuffer(Buffer):

    def __init__(self, size):
        super().__init__(size)

    def add_packet(self, packet):
        if not self.is_full():
            self.packets.append(packet)
            self.packets.sort(key=lambda x: x.packet_id)
        else:
            print("Buffer cheio!")
