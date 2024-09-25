import json
import os
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, Menu

def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            return json.load(file)
    except Exception as e:
        messagebox.showerror("错误", f"无法读取或解析文件: {file_path}\n错误: {str(e)}")
    return None

def find_plays_with_all_characters(directory, character_names):
    play_names = []
    file_names = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            data = read_json_file(file_path)
            if data:
                # 尝试从 _meta 中提取剧本名称
                play_name = next((item.get('name') for item in data if item.get('id') == "_meta"), None)

                # 如果没有找到剧本名称，使用文件名作为剧本名称
                if not play_name:
                    play_name = os.path.splitext(filename)[0]  # 去掉文件扩展名

                # 提取角色名并进行匹配
                character_set = set(item.get('name') for item in data if item.get('id') != "_meta" and 'name' in item)
                if all(name in character_set for name in character_names):
                    play_names.append(play_name)
                    file_names.append(filename)
    return play_names, file_names

def search_plays():
    directory = directory_path.get()
    if not os.path.isdir(directory):
        messagebox.showerror("错误", "请选择一个有效的目录！")
        return
    character_input = input_text.get("1.0", tk.END).strip()
    if not character_input:
        messagebox.showwarning("警告", "请输入至少一个角色名称！")
        return
    character_names = [name.strip() for name in character_input.split("\n") if name.strip()]
    play_names, file_names = find_plays_with_all_characters(directory, character_names)

    result_text_plays.config(state=tk.NORMAL)
    result_text_plays.delete('1.0', tk.END)

    result_text_files.config(state=tk.NORMAL)
    result_text_files.delete('1.0', tk.END)

    if play_names:
        result_text_plays.insert(tk.INSERT, "\n".join(play_names))
        result_text_files.insert(tk.INSERT, "\n".join(file_names))
    else:
        result_text_plays.insert(tk.INSERT, "未找到包含指定角色的剧本。")
        result_text_files.insert(tk.INSERT, "")

    result_text_plays.config(state=tk.DISABLED)
    result_text_files.config(state=tk.DISABLED)

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_path.set(directory)

def make_popup(event):
    try:
        popup.tk_popup(event.x_root, event.y_root)
    finally:
        popup.grab_release()

# 创建主窗口
root = tk.Tk()
root.title("《染·钟楼谜团》剧本查找器")

# 创建右键菜单
popup = Menu(root, tearoff=0)
popup.add_command(label="Copy", command=lambda: root.focus_get().event_generate('<<Copy>>'))
popup.add_command(label="Paste", command=lambda: root.focus_get().event_generate('<<Paste>>'))

# 设置目录选择区域
tk.Label(root, text="目录路径：").pack()
directory_frame = tk.Frame(root)
directory_path = tk.StringVar()
directory_entry = tk.Entry(directory_frame, textvariable=directory_path, width=50)
directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
browse_button = tk.Button(directory_frame, text="浏览目录", command=select_directory)
browse_button.pack(side=tk.RIGHT)
directory_frame.pack()

# 设置角色输入区域
tk.Label(root, text="请输出角色名称（每个一行）:").pack()
input_text = scrolledtext.ScrolledText(root, height=10)
input_text.pack()
input_text.bind("<Button-3>", make_popup)

# 创建结果显示区域的 Frame，用于左右布局
results_frame = tk.Frame(root)
results_frame.pack(fill=tk.BOTH, expand=True)

# 设置左侧的剧本名称区域
tk.Label(results_frame, text="剧本名：").grid(row=0, column=0)
result_text_plays = scrolledtext.ScrolledText(results_frame, height=20, width=40)
result_text_plays.config(state=tk.DISABLED)
result_text_plays.grid(row=1, column=0)

# 设置右侧的文件名区域
tk.Label(results_frame, text="文件名：").grid(row=0, column=1)
result_text_files = scrolledtext.ScrolledText(results_frame, height=20, width=40)
result_text_files.config(state=tk.DISABLED)
result_text_files.grid(row=1, column=1)

# 设置搜索按钮
search_button = tk.Button(root, text="搜索剧本", command=search_plays)
search_button.pack()

root.mainloop()
