import socket
import threading

host = "127.0.0.1"
tcpPort = 12345
addr = (host, tcpPort)
stateUserName = 0

def receive_messages(clientSocket):
    while True:
        try:
            data = clientSocket.recv(1024)
            # print("Gelen Veri: ", data.decode("utf-8"))
            if not data:
                break
            if(data.decode("utf-8") == "4740_invalid_srNm"):
                print("Bu kullanıcı adı zaten alınmış, lütfen başka bir kullanıcı adı girin")
                break
            elif(data.decode("utf-8").split(":")[0] == "659_valid_srNm"): 
                userName = data.decode("utf-8").split(":")[1]
                print(f"Hoşgeldiniz {userName} [TCP] ile bağlısınız")
                global stateUserName
                stateUserName = 1
            else:
                print(str(data.decode("utf-8")))
        except:
            break

def main():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((host, tcpPort))

    try:
        while True:
            threading.Thread(target=receive_messages, args=(clientSocket,)).start()
            if(stateUserName == 0):
                userName = input("Kullanıcı Adı Giriniz: ")
                sendUserName = "userName:"+ userName 
                clientSocket.send(sendUserName.encode("utf-8"))
            else:
                payload = input("Mesaj Yazınız: ")
                clientSocket.send(payload.encode("utf-8"))
    except KeyboardInterrupt:
        exit()
    finally:
        clientSocket.close()

main()