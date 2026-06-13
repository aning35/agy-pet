import tkinter as tk
import serial
import threading
import time

# 状态颜色映射
STATE_COLORS = {
    0x01: ("#A6DA95", "IDLE (空闲) - LED 熄灭"),
    0x02: ("#8AADF4", "THINKING (思考中) - LED 闪烁"),
    0x03: ("#EED49F", "WAITING (等待确认) - LED 常亮"),
    0x04: ("#ED8796", "ERROR (报错) - LED 红色警报")
}

# 这里配置虚拟串口对的另一端，比如 AgyPet 连 COM3，这里连 COM4
LISTEN_PORT = "COM4" 
BAUDRATE = 115200

class VirtualSerialHardwareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AgyPet 虚拟串口硬件测试")
        self.root.geometry("350x200")
        self.root.attributes("-topmost", True)
        
        self.label = tk.Label(root, text=f"尝试打开串口 {LISTEN_PORT} ...\n(请确保您已经使用 com0com 等软件\n创建了虚拟串口对)", 
                              font=("Microsoft YaHei", 10, "bold"), bg="#303446", fg="white", wraplength=300)
        self.label.pack(expand=True, fill=tk.BOTH)

    def update_state(self, state_code):
        color, text = STATE_COLORS.get(state_code, ("#FFFFFF", f"收到未知状态码: {hex(state_code)}"))
        self.root.after(0, lambda: self.label.config(bg=color, text=text, fg="#24273A"))

    def show_error(self, err_msg):
        self.root.after(0, lambda: self.label.config(bg="#ED8796", text=err_msg, fg="white"))

def read_serial(app):
    try:
        # 打开串口
        ser = serial.Serial(LISTEN_PORT, BAUDRATE, timeout=1)
        app.root.after(0, lambda: app.label.config(text=f"已成功监听串口: {LISTEN_PORT}\n等待接收 AgyPet 蓝牙/串口数据..."))
        
        while True:
            if ser.in_waiting > 0:
                data = ser.read(1)
                state_code = data[0]
                print(f"收到十六进制数据: 0x{state_code:02X}")
                app.update_state(state_code)
            time.sleep(0.1)
    except serial.SerialException as e:
        app.show_error(f"串口错误: 找不到 {LISTEN_PORT} 或者被占用。\n请确认您已创建虚拟串口！")
    except Exception as e:
        app.show_error(f"发生错误: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualSerialHardwareApp(root)
    
    # 启动串口读取线程
    serial_thread = threading.Thread(target=read_serial, args=(app,), daemon=True)
    serial_thread.start()
    
    root.mainloop()
