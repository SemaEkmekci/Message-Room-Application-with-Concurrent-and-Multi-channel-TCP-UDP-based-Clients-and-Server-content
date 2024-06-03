import socket
from _thread import start_new_thread, allocate_lock

TCP_PORT = 12345
UDP_PORT = 12346
BUFFER_SIZE = 1024
LOCALHOST = "127.0.0.1"

tcp_clients = []
tcp_lock = allocate_lock()

udp_clients = []
udp_lock = allocate_lock()


def tcpClientThread(connection, address):
    # connection.send(str.encode("Sunucuya bağlandınız."))
    userName = None
    try:
        while True:
            data = connection.recv(BUFFER_SIZE)
            if not data:
                break
            message = data.decode("utf-8")

            if message.split(":")[0] == "userName":
                message_parts = message.split(":")
                new_user_name = message_parts[1]
                if not (any(client["userName"] == new_user_name for client in tcp_clients) or
                        any(client["userName"] == new_user_name for client in udp_clients)):
                    userName = new_user_name
                    print(f"{userName} [TCP] ile sohbete katıldı.")
                    msg = "659_valid_srNm:" + userName
                    with tcp_lock:
                        if not any(client["address"] == address for client in tcp_clients):
                            info = {"socket": connection, "userName": userName, "address": address}
                            tcp_clients.append(info)
                    connection.sendall(msg.encode("utf-8"))
                else:
                    errorMessage = "4740_invalid_srNm"
                    connection.sendall(errorMessage.encode("utf-8"))
            else:
                print(f"{userName} [TCP]: {message}")
                sendMessage = f"{userName} [TCP]: {message}"
                with tcp_lock:
                    for client_info in tcp_clients:
                        client_info["socket"].sendall(sendMessage.encode("utf-8"))
                    for udp_addr in udp_clients:
                        udp_socket.sendto(sendMessage.encode("utf-8"), udp_addr["address"])
                
    except Exception as e:
        # print(f"TCP Client Handler Error: {e}")
        pass
    finally:
        with tcp_lock:
            for client in tcp_clients:
                if client["address"] == address:
                    tcp_clients.remove(client)
                    break
        if userName:
            print(f"{userName} [TCP] sohbetten ayrıldı.")
        connection.close()


def udpServerThread(udpSocket):
    while True:
        try:
            data, address = udpSocket.recvfrom(BUFFER_SIZE)
            message = data.decode("utf-8")
            if message.split(":")[0] == "userName":
                message_parts = message.split(":")
                new_user_name = message_parts[1]
                if not (any(client["userName"] == new_user_name for client in udp_clients) or
                        any(client["userName"] == new_user_name for client in tcp_clients)):
                    userName = new_user_name
                    print(f"{userName} [UDP] ile sohbete katıldı.")
                    msg = "659_valid_srNm:" + userName
                    with udp_lock:
                        if not any(client["address"] == address for client in udp_clients):
                            info = {"userName": userName, "address": address}
                            udp_clients.append(info)
                    udpSocket.sendto(msg.encode("utf-8"), address)
                else:
                    errorMessage = "4740_invalid_srNm"
                    udpSocket.sendto(errorMessage.encode("utf-8"), address)
            elif message == "görüşürüz":
                userName = next((client["userName"] for client in udp_clients if client["address"] == address), "Bilinmiyor")
                print(f"{userName} [UDP] sohbetten ayrıldı.")
                with udp_lock:
                    for client in udp_clients:
                        if client["address"] == address:
                            udp_clients.remove(client)
                            break
                message = "2150_lv_clnt"
                udpSocket.sendto(message.encode("utf-8"), address)
            else:
                userName = next((client["userName"] for client in udp_clients if client["address"] == address), "Bilinmiyor")
                print(f"{userName} [UDP]: {message}")
                sendMessage = f"{userName}[UDP]: {message}"
                with tcp_lock:
                    for client_info in tcp_clients:
                        try:
                            client_info["socket"].sendall(sendMessage.encode("utf-8"))
                        except Exception as e:
                            print(f"Error sending message to TCP client {client_info['address']}: {e}")
                    for udp_addr in udp_clients:
                        udp_socket.sendto(sendMessage.encode("utf-8"), udp_addr["address"])
        except Exception as e:
            print(f"UDP Server Handler Error: {e}")

def main():
    global udp_socket

    # Create TCP socket
    tcpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        tcpServerSocket.bind((LOCALHOST, TCP_PORT))
        print("TCP bağlantı bekleniyor...")
        tcpServerSocket.listen(5)
    except socket.error as e:
        print(f"TCP Socket error: {e}")
        return

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_socket.bind((LOCALHOST, UDP_PORT))
        print("UDP bağlantısı bekleniyor...")
    except socket.error as e:
        print(f"UDP Socket error: {e}")
        return

    start_new_thread(udpServerThread, (udp_socket,))
    
    
    while True:
        try:
            client, address = tcpServerSocket.accept()
            print(f"{address[0]}, {str(address[1])}'a bağlandı.")
            start_new_thread(tcpClientThread, (client, address))
            
        except Exception as e:
            print(f"Error accepting connections: {e}")
            break
    tcpServerSocket.close()
    udp_socket.close()

main()
