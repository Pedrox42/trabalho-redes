import math


class Packet:
    def __init__(self, content, packet_id):
        self.content = content
        self.packet_id = packet_id

    def __len__(self):
        return len(self.content) + math.ceil(self.packet_id.bit_length() / 8)


class SignalPacket:
    def __init__(self, packet_id, syn, fin, ack, recvwnd=10):
        self.packet_id = packet_id
        self.syn = syn
        self.fin = fin
        self.ack = ack
        self.recvwnd = recvwnd

    def is_syn(self):
        return self.syn and not self.ack

    def is_fin(self):
        return self.fin and not self.ack

    def is_syn_ack(self):
        return self.syn and self.ack

    def is_fin_ack(self):
        return self.fin and self.ack

    def is_ack(self):
        return self.ack and not self.syn and not self.fin

    def get_type(self):
        if self.is_syn():
            return "syn"

        if self.is_syn_ack():
            return "synack"

        if self.is_fin():
            return "fin"

        if self.is_fin_ack():
            return "finack"

        if self.is_ack():
            return "ack"
