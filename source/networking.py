import socket


def send_datagram(udp_socket: socket, datagram: bytes, ip, port):
    if datagram is not None and len(datagram) > 0:
        udp_socket.sendto(datagram, (ip, port))


def open_port(udp_ip: str, udp_port: int):

    udp_socket = socket.socket(socket.AF_INET,  # Internet
                               socket.SOCK_DGRAM)  # UDP
    udp_socket.settimeout(0.01)
    try:
        udp_socket.bind((udp_ip, udp_port))
    except socket.error as error:
        print('\n'
              '#############\n'
              'Socket error: {}\n'
              '#############\n'.format(error))
        udp_socket.close()
        udp_socket = None
    except ValueError as error:
        print('\n'
              '#############\n'
              'Value error: {}\n'
              '#############\n'.format(error))
        udp_socket.close()
        udp_socket = None
    except Exception as error:
        print('\n'
              '#############\n'
              'Unknown error: {}\n'
              '#############\n'.format(error))
        udp_socket.close()
        udp_socket = None

    return udp_socket
