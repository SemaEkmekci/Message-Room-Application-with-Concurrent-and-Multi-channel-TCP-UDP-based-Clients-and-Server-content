import socket
import threading

host = "127.0.0.1"
tcpPort = 12345
addr = (host, tcpPort)
stateUserName = 0
userNameConfirmed = threading.Event()

def receive_messages(clientSocket):
    global stateUserName
    while True:
        try:
            data = clientSocket.recv(1024)
            if not data:
                break
            decoded_data = data.decode("utf-8")
            if decoded_data == "4740_invalid_srNm":
                print("Bu kullanıcı adı zaten alınmış, lütfen başka bir kullanıcı adı girin")
                stateUserName = 0
                userNameConfirmed.clear()
            elif decoded_data.split(":")[0] == "659_valid_srNm":
                userName = decoded_data.split(":")[1]
                print(f"Hoşgeldiniz {userName} [TCP] ile bağlısınız")
                stateUserName = 1
                userNameConfirmed.set()
            else:
                # print("\n")
                print(decoded_data)
        except Exception as e:
            print(f"Hata: {e}")
            break

def main():
    global stateUserName
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((host, tcpPort))

    threading.Thread(target=receive_messages, args=(clientSocket,)).start()

    try:
        while True:
            if stateUserName == 0:
                userName = input("Kullanıcı Adı Giriniz: ")
                sendUserName = "userName:" + userName
                clientSocket.send(sendUserName.encode("utf-8"))
                if not userNameConfirmed.wait(timeout=1):
                    pass
            else:
                # payload = input("Mesaj Yazınız: ")
                payload = input("")
                # print("\n")
                clientSocket.send(payload.encode("utf-8"))
    except KeyboardInterrupt:
        exit()
    finally:
        clientSocket.close()

main()
