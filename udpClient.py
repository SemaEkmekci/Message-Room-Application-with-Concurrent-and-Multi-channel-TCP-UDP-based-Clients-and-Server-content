import socket
import threading

serverName = "127.0.0.1"
serverPort = 12346
addr = (serverName, serverPort)
stateUserName = 0

def receiveMessage(clientSocket):
    while True:
        try:
            data, addr = clientSocket.recvfrom(1024)
            if not data:
                break
            # print("Sunucudan gelen yanıt: ")
            if(data.decode("utf-8") == "4740_invalid_srNm"):
                print("Bu kullanıcı adı zaten alınmış, lütfen başka bir kullanıcı adı girin")
                break
            elif(data.decode("utf-8").split(":")[0] == "659_valid_srNm"): 
                userName = data.decode("utf-8").split(":")[1]
                print(f"Hoşgeldiniz {userName} [UDP] ile bağlısınız")
                global stateUserName
                stateUserName = 1
            elif(data.decode("utf-8") == "2150_lv_clnt"):
                clientSocket.close()
            else:
                print(str(data.decode("utf-8")))
        except:
            break

def main():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        global stateUserName
        
        while True:
            threading.Thread(target=receiveMessage, args=(clientSocket,)).start()

            if(stateUserName == 0):
                userName = input("Kullanıcı Adı Giriniz: ")
                sendUserName = "userName:"+ userName 
                clientSocket.sendto(sendUserName.encode("utf-8"), addr)
            else:
                msg = input("Mesaj Giriniz: ")
                clientSocket.sendto(msg.encode("utf-8"), addr)
    except KeyboardInterrupt:
        exit()
    finally:
        clientSocket.close()

main()
