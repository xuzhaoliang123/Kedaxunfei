# -*- encoding:utf-8 -*-
import hashlib
import hmac
import base64
from socket import *
import json, time, threading
from websocket import create_connection
import websocket
from urllib.parse import quote
import logging
from captureAudio import CA
import pyaudio

import tkinter as tk
import asyncio



# reload(sys)
# sys.setdefaultencoding("utf8")
class Client():
    ouput_str=""
    def __init__(self):
        
        
       
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        self.end_tag = "{\"end\": true}"

        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()
               

    def send(self, file_path):
        FORMAT = pyaudio.paInt16  # 音频数据的格式
        CHANNELS = 1  # 声道数，2代表立体声
        RATE = 16000 # 采样率，单位是Hz
        CHUNK = 1280# 每个缓冲区的帧数
        RECORD_SECONDS = 15  # 录制时间，单位是秒
        WAVE_OUTPUT_FILENAME = "./audio.pcm"  # 输出文件名    
        audio = pyaudio.PyAudio()
       
       
    # 打开流
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    
        print("开始录音...")      
        
        while True:
          data=stream.read(CHUNK)
          self.ws.send(data)
          

    def recv(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                   
                    print("handshake success, result: " + result)

                if result_dict["action"] == "result":
                    
                    result_1 = result_dict["data"]
                    state=json.loads(result_1)['cn']['st']['type']
                    
                    rs=json.loads(result_1)['cn']['st']['rt']
                    a=''
                    
                    for i in rs:
                         for x in i["ws"]:
                             w=x["cw"][0]["w"]
                             wp=x["cw"][0]["wp"]
                             if wp!='s':
                                a=w
                                print(state,a) 
                                if int(state)==0:                            
                                   Client.ouput_str+=a
                                   print("------->",Client.ouput_str)
                               
                    #print("------->",Client.ouput_str)   
                    

                
                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            print("receive result end")


def initChannel():
      file_path = r"./audio.pcm"
      client = Client()
      client.send(file_path)
  

def close(self):
        self.ws.close()
        print("connection closed")

def updateStr():
    words.config(text=Client.ouput_str)
    root.after(300,updateStr)



def closeTrans():
     root.destroy()
       

if __name__ == '__main__':
    
   
    logging.basicConfig()
    app_id = "37d85e4a"
    api_key = "8563c3101ed5547e4677797f695cd0ed"   
    root=tk.Tk()
    root.title("SETV实时转写")
    root.geometry("1280x700")
    # words = tk.Text(root, wrap=tk.WORD)  # 设置wrap为tk.WORD以自动换行
    # words.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
 
# 插入多行文本
    
    canvas = tk.Canvas(root, bg="white", height=1280, width=720)
    canvas.pack(fill="both", expand=True)
    words=tk.Label(canvas,width=700,height=50,text=Client.ouput_str,font=("Times New Roman",20,"bold"),justify=tk.LEFT,wraplength=700,pady=0,padx=0,anchor='nw')
    words.pack()
    output=threading.Thread(target=initChannel)
    output.start()
    updateStr()
    root.mainloop()
    
    
   
    
