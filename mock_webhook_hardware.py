import tkinter as tk
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json

# 状态颜色映射
STATE_COLORS = {
    1: ("#A6DA95", "IDLE (空闲) - LED 熄灭"),
    2: ("#8AADF4", "THINKING (思考中) - LED 闪烁"),
    3: ("#EED49F", "WAITING (等待确认) - LED 常亮"),
    4: ("#ED8796", "ERROR (报错) - LED 红色警报")
}

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = {}
        if post_data:
            try:
                data = json.loads(post_data.decode('utf-8'))
            except:
                pass
                
        state_code = data.get("state_code", 1)
        # 通知主线程更新 UI 窗口
        self.server.app.update_state(state_code)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass # 屏蔽 HTTP 日志输出

class WebhookHardwareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AgyPet 虚拟硬件指示灯")
        self.root.geometry("350x200")
        self.root.attributes("-topmost", True) # 窗口置顶，方便观察
        
        self.label = tk.Label(root, text="等待接收 AgyPet 信号...\n(请在 AgyPet 设置中填入 Webhook: http://127.0.0.1:8888)", 
                              font=("Microsoft YaHei", 10, "bold"), bg="#303446", fg="white", wraplength=300)
        self.label.pack(expand=True, fill=tk.BOTH)

    def update_state(self, state_code):
        color, text = STATE_COLORS.get(state_code, ("#FFFFFF", f"未知状态: {state_code}"))
        # Tkinter UI 更新必须在主线程，通过 after 确保安全
        self.root.after(0, lambda: self.label.config(bg=color, text=text, fg="#24273A"))

def start_server(app):
    server = HTTPServer(('127.0.0.1', 8888), WebhookHandler)
    server.app = app # 将 app 实例挂载到 server 上
    print("虚拟硬件已启动，正在监听端口 8888...")
    server.serve_forever()

if __name__ == "__main__":
    root = tk.Tk()
    app = WebhookHardwareApp(root)
    
    # 在后台线程启动 Webhook 接收服务器
    server_thread = threading.Thread(target=start_server, args=(app,), daemon=True)
    server_thread.start()
    
    root.mainloop()
