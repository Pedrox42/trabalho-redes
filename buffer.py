import math

buffer_size = 8192
max_packet_size = 1024


class Packet:
    def __init__(self, content, packet_id):
        self.content = content
        self.packet_id = packet_id

    def __len__(self):
        return len(self.content) + math.ceil(self.packet_id.bit_length() / 8)


class Buffer:
    def __init__(self, file_name, start_from_byte):
        self.packets = []
        self.start_from_byte = start_from_byte
        self.arrange_packets(file_name, start_from_byte)

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
            packet = Packet(content, packet_id)
            self.packets.append(packet)
        else:
            print("Buffer cheio!")

    def arrange_packets(self, file_name, start_from_byte):
        file = open(file_name, "rb")

        file.read(start_from_byte)
        byte = file.read(max_packet_size)

        packet_id = 0
        while byte:
            if not self.is_full():
                self.add_packet(byte, packet_id)
                packet_id += len(byte)
                byte = file.read(max_packet_size - (math.ceil(packet_id.bit_length() / 8)))
            else:
                break

        file.close()

    def total_file_read_size(self):
        read_size = 0
        for packet in self.packets:
            read_size += len(packet.content)
        return read_size
