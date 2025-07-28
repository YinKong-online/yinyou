import json
import librosa
import soundfile as sf
import pygame
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# 初始化 pygame
pygame.mixer.init()

# 加载音频文件
filename = r"C:\Users\lenovo\Desktop\hezhe.mp3"
y, sr = librosa.load(filename)

# 将 mp3 转换为 wav
sf.write("hezhe.wav", y, sr)

# 创建主窗口
root = tk.Tk()
root.title("音频弹奏跟随")

# 初始化变量
recorded_times = []
start_time = 0.0

# 播放音频的函数
def play_audio():
    global start_time
    pygame.mixer.music.load("hezhe.wav")
    pygame.mixer.music.play()
    start_time = datetime.now().timestamp()

# 记录当前时间的函数
def record_time():
    current_time = datetime.now().timestamp()
    if start_time > 0:
        recorded_time = current_time - start_time
        recorded_times.append(recorded_time)
        update_label()
    else:
        messagebox.showinfo("提示", "请先播放音频。")

# 更新标签的函数
def update_label():
    label.config(text=f"已记录的时间点: {recorded_times}")

# 保存记录的时间点到 JSON 文件
def save_times():
    data = {"filename": filename, "recorded_times": recorded_times}
    try:
        with open("chuli.json", "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []
    existing_data.append(data)
    with open("chuli.json", "w") as f:
        json.dump(existing_data, f)
    messagebox.showinfo("成功", "时间点已记录并保存到文件。")
    recorded_times.clear()  # 清空记录的时间点

# 创建按钮
play_button = tk.Button(root, text="播放音频", command=play_audio)
play_button.pack(pady=10)

record_button = tk.Button(root, text="记录时间", command=record_time)
record_button.pack(pady=10)

save_button = tk.Button(root, text="保存时间点", command=save_times)
save_button.pack(pady=10)

# 创建标签
label = tk.Label(root, text="已记录的时间点: ")
label.pack(pady=10)

root.mainloop()
