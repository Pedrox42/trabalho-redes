import matplotlib.pyplot as plt
import buffers
from matplotlib.lines import Line2D


# Congestion Control Protocol - TCP
class TcpPcc:
    def __init__(self, mss, tcp_type='reno', fast_forward=True):
        # atributos do protocolo
        self.cwnd = 1
        self.ssthresh = float('inf')
        self.last_ack = -1
        self.duplicate_acks = 0
        self.confirmed_acks = 0
        self.MSS = mss
        self.ack_protocol = self.reno if tcp_type == 'reno' else self.tahoe
        self.fast_forward = fast_forward
        self.max = buffers.total_packets

        # metricas p/ plot
        self.track_ssthresh = []
        self.track_cwnd = []
        self.track_rtt = []
        self.track_troughput = []
        self.track_timeout = []
        self.track_duplicate_acks = []
        self.track_fast_forwards = []

    # definir proximo tamanho de janela
    def next_mss(self, ack, rtt=1, timeout=False):

        # espera ultima chamada para saber o rtt
        self.track(rtt, timeout)

        if timeout:
            self.handle_timeout()
        else:
            self.handle_ack(ack)

        return self.MSS*self.cwnd

    # atualizar ssthresh
    def update_ssthresh(self):
        self.ssthresh = max(self.cwnd // 2, 2)

    # atualizar cwnd
    def update_cwnd(self):
        if self.cwnd < self.ssthresh:
            self.cwnd *= 2  # Slow start
            self.track_fast_forwards.append(0)
        elif self.fast_forward and self.confirmed_acks >= 5:
            self.cwnd *= 2  # fast_forward
            self.confirmed_acks = 0
            self.track_fast_forwards.append(1)
        else:
            self.cwnd += 1   # Congestion avoidance
            self.track_fast_forwards.append(0)
        self.cwnd = min(self.cwnd, self.max)

    # lidar com timeout
    def handle_timeout(self):
        self.update_ssthresh()
        self.cwnd = 1
        self.confirmed_acks = 0
        self.duplicate_acks = 0
        self.track_duplicate_acks.append(0)
        self.track_fast_forwards.append(0)

    # lidar e atualizar acks
    def handle_ack(self, ack):
        if ack > self.last_ack:
            self.last_ack = ack
            self.update_cwnd()
            self.confirmed_acks += 1
            self.track_duplicate_acks.append(0)
        else:
            self.confirmed_acks = 0
            self.duplicate_acks += 1
            self.track_duplicate_acks.append(1)
            self.track_fast_forwards.append(0)

        if self.duplicate_acks >= 3:
            self.ack_protocol()

    # protocolo tcp-reno
    def reno(self):
        self.update_ssthresh()
        self.cwnd = self.ssthresh
        self.duplicate_acks = 0

    # protocolo tcp-tahoe
    def tahoe(self):
        self.update_ssthresh()
        self.cwnd = 1
        self.duplicate_acks = 0

    # função para track
    def track(self, rtt, timeout):
        self.track_ssthresh.append(self.MSS*self.ssthresh)
        self.track_cwnd.append(self.MSS*self.cwnd)
        self.track_rtt.append(rtt)
        self.track_troughput.append(self.MSS*self.cwnd/rtt)
        self.track_timeout.append(timeout)

    # função de plot principal
    def plot_congestion(self):
        time = range(len(self.track_cwnd))
        total_steps = len(self.track_cwnd)

        # plots principais cwnd e ssthresh
        plt.figure(figsize=(10, 6))
        plt.plot(time, self.track_cwnd, label='cwnd')
        plt.plot(time, self.track_ssthresh, '--', label='ssthresh')

        # plottar timeouts como 'x' vermelho
        for idx, timeout in enumerate(self.track_timeout):
            if timeout:
                plt.scatter(idx, self.track_cwnd[idx], color='red', marker='x')

        # plotar acks duplicados como 'o' azul
        for idx, duplicate in enumerate(self.track_duplicate_acks):
            if duplicate:
                plt.scatter(idx, self.track_cwnd[idx], color='blue', marker='o')

        # plotar fast_forward como 'o' verde
        for idx, duplicate in enumerate(self.track_fast_forwards):
            if duplicate:
                plt.scatter(idx, self.track_cwnd[idx], color='green', marker='^')

        # dados para legenda
        handles, labels = plt.gca().get_legend_handles_labels()

        # legenda para timeout, ack duplicado, fast forward
        handles.append(Line2D([], [], color='red', marker='x', linestyle='', markersize=8))
        labels.append('Timeout')
        handles.append(Line2D([], [], color='blue', marker='o', linestyle='', markersize=8))
        labels.append('Ack Duplicado')
        handles.append(Line2D([], [], color='green', marker='^', linestyle='', markersize=8))
        labels.append('Fast Forward')

        plt.legend(handles, labels)
        plt.xlabel('Time')
        plt.ylabel('Valores')
        plt.title('TCP Congestion Protocol')
        plt.grid(True)
        plt.show()

    # plot do round trip time
    def plot_rtt(self):
        time = range(len(self.track_troughput))

        plt.figure(figsize=(10, 6))
        plt.plot(time, self.track_rtt, label='RTT')

        plt.xlabel('Tempo')
        plt.ylabel('RTT')
        plt.title('TCP Congestion Protocol')
        plt.legend()
        plt.grid(True)
        plt.show()

    # plot de vazão
    def plot_throughput(self):
        time = range(len(self.track_troughput))

        plt.figure(figsize=(10, 6))
        plt.plot(time, self.track_troughput, label='Vazão')

        plt.xlabel('Tempo')
        plt.ylabel('Vazão')
        plt.title('TCP Congestion Protocol')
        plt.legend()
        plt.grid(True)
        plt.show()

# grafico para visualizar tamanho de janela, ssthresh, timeouts e acks duplicados ao longo do tempo
# protocol.plot_congestion()

# grafico de vazão x tempo
# protocol.plot_throughput()

# gráfico de rtt ao longo do tempo
# protocol.plot_rtt()
