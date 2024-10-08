import tkinter as tk   # tkinter 创建图形用户界面 (GUI) 的标准库
from tkinter import messagebox
import threading
from flask import Flask, request, jsonify
import pyautogui   # 实现自动化的图形用户界面 (GUI) 操作
import pytesseract  # 图像 文字的识别
import cv2   # opencv-python 是一个基于 BSD 许可（开源）发行的跨平台计算机视觉库， 图像处理和图像分析
import numpy as np
import time
import random

from pywinauto import Application  #pywinauto Windows应用程序自动化控制库。它支持模拟鼠标和键盘操作，实现对Windows应用程序的自动化控制


app = Flask(__name__)
is_running = False


def focus_window():
    # 启动应用程序
    # app = Application().start("notepad.exe")
    try:
        # Connect to the existing application
        curApp = Application().connect(title='记事本')
        # Get the window object
        app_window = curApp.window(title='记事本')
        # Set focus to the window
        app_window.set_focus()
        time.sleep(random.uniform(3, 5))
    except Exception as e:
        print(f"Failed to focus on the window: {e}")



def locate_gem(image_path):
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    template = cv2.imread(image_path, 0)
    res = cv2.matchTemplate(cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY), template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val > 0.8:  # 设定一个阈值
        return max_loc
    return None

def auto_mine(image_path):
    global is_running
    focus_window()
    while is_running:
        pos = locate_gem(image_path)
        if pos:
            pyautogui.click(pos[0], pos[1])
        time.sleep(5)

@app.route('/start', methods=['POST'])
def start_mining():
    global is_running
    if not is_running:
        is_running = True
        image_path = request.json.get('image_path')
        threading.Thread(target=auto_mine, args=(image_path,)).start()
        return jsonify({"status": "started"}), 200
    return jsonify({"status": "already running"}), 400

@app.route('/stop', methods=['POST'])
def stop_mining():
    global is_running
    if is_running:
        is_running = False
        return jsonify({"status": "stopped"}), 200
    return jsonify({"status": "not running"}), 400

def start_flask():
    app.run(debug=False, use_reloader=False)

def start_mining_gui():
    global is_running
    if not is_running:
        is_running = True
        image_path = 'gem.png'  # 替换为你的图片路径
        threading.Thread(target=auto_mine, args=(image_path,)).start()
        messagebox.showinfo("信息", "自动脚本已启动")

def stop_mining_gui():
    global is_running
    if is_running:
        is_running = False
        messagebox.showinfo("信息", "自动脚本已停止")

# 创建图形界面
root = tk.Tk()
root.title("自动脚本")

start_button = tk.Button(root, text="开始脚本", command=start_mining_gui)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="停止脚本", command=stop_mining_gui)
stop_button.pack(pady=10)

# 启动 Flask 服务器
threading.Thread(target=start_flask).start()

root.mainloop()