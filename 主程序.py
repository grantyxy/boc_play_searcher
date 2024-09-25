import json
import os
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk

def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            return json.load(file)
    except Exception as e:
        messagebox.showerror("错误", f"无法读取或解析文件: {file_path}\n错误: {str(e)}")
    return None

def find_plays_with_conditions(directory, conditions):
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

                # 提取角色名
                character_set = set(item.get('name') for item in data if item.get('id') != "_meta" and 'name' in item)

                # 处理 AND 和 OR 条件
                if evaluate_conditions(character_set, conditions):
                    play_names.append(play_name)
                    file_names.append(filename)
    return play_names, file_names

def evaluate_conditions(character_set, conditions):
    """根据 AND 和 OR 条件评估角色是否匹配"""
    and_conditions = [cond['term'] for cond in conditions if cond['type'] == "AND"]
    or_conditions = [cond['term'] for cond in conditions if cond['type'] == "OR"]

    # AND 条件：所有必须存在
    if all(cond in character_set for cond in and_conditions):
        # OR 条件：至少有一个存在
        if not or_conditions or any(cond in character_set for cond in or_conditions):
            return True
    return False

def search_plays():
    directory = directory_path.get()
    if not os.path.isdir(directory):
        messagebox.showerror("错误", "请选择一个有效的目录！")
        return

    # 收集用户添加的条件
    conditions = []
    for row in search_rows:
        condition_type = row['condition_type'].get()
        search_term = row['search_term'].get().strip()
        if search_term:
            conditions.append({"type": condition_type, "term": search_term})

    if not conditions:
        messagebox.showwarning("警告", "请输入至少一个搜索条件！")
        return

    play_names, file_names = find_plays_with_conditions(directory, conditions)

    result_text_plays.config(state=tk.NORMAL)
    result_text_plays.delete('1.0', tk.END)

    result_text_files.config(state=tk.NORMAL)
    result_text_files.delete('1.0', tk.END)

    if play_names:
        result_text_plays.insert(tk.INSERT, "\n".join(play_names))
        result_text_files.insert(tk.INSERT, "\n".join(file_names))
    else:
        result_text_plays.insert(tk.INSERT, "未找到包含指定条件的剧本。")
        result_text_files.insert(tk.INSERT, "")

    result_text_plays.config(state=tk.DISABLED)
    result_text_files.config(state=tk.DISABLED)

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_path.set(directory)

def add_search_row():
    row_frame = tk.Frame(search_frame)
    row_frame.pack(fill=tk.X, pady=5)

    condition_type = ttk.Combobox(row_frame, values=["AND", "OR"], width=5)
    condition_type.set("AND")
    condition_type.pack(side=tk.LEFT, padx=5)

    field_label = tk.Label(row_frame, text="角色名")
    field_label.pack(side=tk.LEFT)

    search_term = tk.Entry(row_frame, width=30)
    search_term.pack(side=tk.LEFT, padx=5)

    # 添加 "-" 按钮
    remove_button = tk.Button(row_frame, text="-", command=lambda: remove_search_row(row_frame))
    remove_button.pack(side=tk.LEFT, padx=5)

    search_rows.append({"frame": row_frame, "condition_type": condition_type, "search_term": search_term})

def remove_search_row(row_frame):
    """移除指定的搜索行"""
    for row in search_rows:
        if row['frame'] == row_frame:
            row_frame.destroy()  # 从界面上移除
            search_rows.remove(row)  # 从搜索条件中移除
            break

def clear_search_rows():
    for row in search_rows:
        row['frame'].destroy()
    search_rows.clear()

def make_popup(event):
    try:
        popup.tk_popup(event.x_root, event.y_root)
    finally:
        popup.grab_release()

# 创建主窗口
root = tk.Tk()
root.title("《染·钟楼谜团》剧本查找器")

# 创建右键菜单
popup = tk.Menu(root, tearoff=0)
popup.add_command(label="Copy", command=lambda: root.focus_get().event_generate('<<Copy>>'))
popup.add_command(label="Paste", command=lambda: root.focus_get().event_generate('<<Paste>>'))

# 设置目录选择区域
tk.Label(root, text="目录路径：").pack(pady=5)
directory_frame = tk.Frame(root)
directory_path = tk.StringVar()
directory_entry = tk.Entry(directory_frame, textvariable=directory_path, width=50)
directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
browse_button = tk.Button(directory_frame, text="浏览目录", command=select_directory)
browse_button.pack(side=tk.RIGHT)
directory_frame.pack(padx=10, pady=5)

# 设置搜索条件区域
tk.Label(root, text="搜索条件：").pack(pady=5)
search_frame = tk.Frame(root)
search_frame.pack(pady=5)

search_rows = []
add_search_row()  # 添加第一行搜索条件

# 添加按钮行
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
add_row_button = tk.Button(button_frame, text="添加条件", command=add_search_row)
add_row_button.pack(side=tk.LEFT, padx=5)
clear_button = tk.Button(button_frame, text="清除条件", command=clear_search_rows)
clear_button.pack(side=tk.LEFT, padx=5)

# 设置左右分栏的显示框架
results_frame = tk.Frame(root)
results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# 设置左侧的剧本名称区域
tk.Label(results_frame, text="剧本名：", font=('Helvetica', 12, 'bold')).grid(row=0, column=0)
result_text_plays = scrolledtext.ScrolledText(results_frame, height=20, width=40)
result_text_plays.config(state=tk.DISABLED)
result_text_plays.grid(row=1, column=0, padx=5)

# 设置右侧的文件名区域
tk.Label(results_frame, text="文件名：", font=('Helvetica', 12, 'bold')).grid(row=0, column=1)
result_text_files = scrolledtext.ScrolledText(results_frame, height=20, width=40)
result_text_files.config(state=tk.DISABLED)
result_text_files.grid(row=1, column=1, padx=5)

# 设置搜索按钮
search_button = tk.Button(root, text="搜索剧本", command=search_plays)
search_button.pack(pady=10)

root.mainloop()
