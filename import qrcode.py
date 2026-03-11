import qrcode
import segno
from PIL import Image
import socket
import threading
import sys
import time
import io
import pyscreenshot
import mss
import struct
import PIL

def get_local():
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        IP= s.getsockname()[0]
        s.close()
        return IP
    except  Exception:
        return '127.0.0.1'
    
def generate_qr_code(ip_adrees,port):
    data=f"CONNECT_MIRROR:{ip_adrees}:{port}"
    img=qrcode.make(data)
    filename="connection_qr.png"
    img.save(filename)
    print(f"QR CODE gerado:{filename}")
    print(f"aponte a camerado seu aplicativo  para o qr code si conectar a {ip_adrees}:{port}")
    img.show()
    return filename

def start_streaming_server(port):
    sever_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sever_socket.bind(('',port))
    sever_socket.listen(1)
    print(f"servidor ouvindo em *{port}")

    conn,addr = sever_socket.accept()
    print(f"conexao estabelecida com {addr}")

    with mss.mss() as sct:
        monitor= sct.monitors[1]
        try:
            while True:
                sct_img=sct.grab(monitor)
                img= Image.frombytes("RGB",sct_img.size,sct_img.bgra,"raw","BGRX")
                img_byte_arr= io.BytesIO()
                img.save( img_byte_arr,format='JPEG',quality=  50)
                img_bytes= img_byte_arr.getvalue()

                size=len(img_bytes)
                conn.sendall(struct.pack('!I',size))

                conn.sendall(img_bytes)

                time.sleep(0.01)
        except (BrokenPipeError,ConnectionResetError):
            print("cliente desconectado")
        except KeyboardInterrupt:
            print("servidor encerrado pelo usuario")
        finally:
            conn.close()
            sever_socket.close() 



if __name__ == "__main__":
    IP_ADDRESS= get_local()
    PORT= 12345

    if IP_ADDRESS=='127.0.0.1':
        print("aviso nao foi possivel conectar")
        
        
    generate_qr_code(IP_ADDRESS,PORT)
       
    start_streaming_server(PORT)
       

