import json
import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QComboBox, QTextEdit, QFileDialog, QMessageBox
)


def evaluate_conditions(character_set, conditions):
    """根据 AND 和 OR 条件评估角色是否匹配"""
    and_conditions = [cond['term'] for cond in conditions if cond['type'] == "AND"]
    or_conditions = [cond['term'] for cond in conditions if cond['type'] == "OR"]

    if all(cond in character_set for cond in and_conditions):
        if not or_conditions or any(cond in character_set for cond in or_conditions):
            return True
    return False


class PlayFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.search_conditions = None
        self.result_text_plays = None
        self.search_frame_layout = None
        self.result_text_files = None
        self.directory_path = None
        self.settings_file = 'settings.json'  # 用于保存目录路径的文件
        self.initUI()

    def initUI(self):
        self.setWindowTitle("《染·钟楼谜团》剧本查找器")
        self.setGeometry(100, 100, 800, 600)

        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 目录选择区域
        directory_layout = QHBoxLayout()
        self.directory_path = QLineEdit()
        browse_button = QPushButton("浏览目录")
        browse_button.clicked.connect(self.select_directory)
        directory_layout.addWidget(QLabel("目录路径："))
        directory_layout.addWidget(self.directory_path)
        directory_layout.addWidget(browse_button)
        main_layout.addLayout(directory_layout)

        # 读取上次的目录路径
        self.load_last_directory()

        # 搜索条件区域
        main_layout.addWidget(QLabel("搜索条件："))
        self.search_conditions = []
        self.search_frame_layout = QVBoxLayout()
        self.add_search_row()  # 添加第一行搜索条件
        main_layout.addLayout(self.search_frame_layout)

        # 添加/清除条件按钮
        button_layout = QHBoxLayout()
        add_row_button = QPushButton("添加条件")
        add_row_button.clicked.connect(self.add_search_row)
        clear_button = QPushButton("清除条件")
        clear_button.clicked.connect(self.clear_search_rows)
        button_layout.addWidget(add_row_button)
        button_layout.addWidget(clear_button)
        main_layout.addLayout(button_layout)

        # 设置结果显示区域
        results_layout = QHBoxLayout()

        # 设置字体加粗
        font = QLabel().font()
        font.setBold(True)

        # 剧本名区域
        script_layout = QVBoxLayout()
        script_name_label = QLabel("剧本名：")
        script_name_label.setFont(font)
        self.result_text_plays = QTextEdit()
        self.result_text_plays.setReadOnly(True)
        script_layout.addWidget(script_name_label)
        script_layout.addWidget(self.result_text_plays)

        # 文件名区域
        file_layout = QVBoxLayout()
        file_name_label = QLabel("文件名：")
        file_name_label.setFont(font)
        self.result_text_files = QTextEdit()
        self.result_text_files.setReadOnly(True)
        file_layout.addWidget(file_name_label)
        file_layout.addWidget(self.result_text_files)

        # 将左右两个布局添加到结果布局中
        results_layout.addLayout(script_layout)
        results_layout.addLayout(file_layout)

        # 添加到主布局
        main_layout.addLayout(results_layout)

        # 搜索按钮
        search_button = QPushButton("搜索剧本")
        search_button.clicked.connect(self.search_plays)
        main_layout.addWidget(search_button)

        self.setLayout(main_layout)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择目录")
        if directory:
            self.directory_path.setText(directory)
            self.save_last_directory(directory)  # 保存选择的目录路径

    def add_search_row(self):
        row_layout = QHBoxLayout()
        condition_type = QComboBox()
        condition_type.addItems(["AND", "OR"])
        search_term = QLineEdit()
        remove_button = QPushButton("-")
        remove_button.clicked.connect(lambda: self.remove_search_row(row_layout))

        row_layout.addWidget(condition_type)
        row_layout.addWidget(QLabel("角色名"))
        row_layout.addWidget(search_term)
        row_layout.addWidget(remove_button)

        self.search_conditions.append({"layout": row_layout, "condition_type": condition_type, "search_term": search_term})
        self.search_frame_layout.addLayout(row_layout)

    def remove_search_row(self, row_layout):
        """移除指定的搜索行"""
        for condition in self.search_conditions:
            if condition["layout"] == row_layout:
                for i in reversed(range(row_layout.count())):
                    widget = row_layout.itemAt(i).widget()
                    if widget:
                        widget.deleteLater()
                self.search_frame_layout.removeItem(row_layout)
                self.search_conditions.remove(condition)
                break

    def clear_search_rows(self):
        """清除所有搜索条件"""
        while self.search_conditions:
            condition = self.search_conditions.pop()
            condition['layout'].deleteLater()

    def search_plays(self):
        directory = self.directory_path.text()
        if not os.path.isdir(directory):
            QMessageBox.critical(self, "错误", "请选择一个有效的目录！")
            return

        # 收集用户添加的条件
        conditions = []
        for condition in self.search_conditions:
            condition_type = condition['condition_type'].currentText()
            search_term = condition['search_term'].text().strip()
            if search_term:
                conditions.append({"type": condition_type, "term": search_term})

        if not conditions:
            QMessageBox.warning(self, "警告", "请输入至少一个搜索条件！")
            return

        # 搜索剧本
        play_names, file_names = self.find_plays_with_conditions(directory, conditions)

        # 更新显示结果
        self.result_text_plays.clear()
        self.result_text_files.clear()

        if play_names:
            self.result_text_plays.append("\n".join(play_names))
            self.result_text_files.append("\n".join(file_names))
        else:
            self.result_text_plays.append("未找到包含指定条件的剧本。")

    def find_plays_with_conditions(self, directory, conditions):
        play_names = []
        file_names = []
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                data = self.read_json_file(file_path)
                if data:
                    play_name = next((item.get('name') for item in data if item.get('id') == "_meta"), None)
                    if not play_name:
                        play_name = os.path.splitext(filename)[0]

                    character_set = set(item.get('name') for item in data if item.get('id') != "_meta" and 'name' in item)

                    if evaluate_conditions(character_set, conditions):
                        play_names.append(play_name)
                        file_names.append(filename)
        return play_names, file_names

    def read_json_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                return json.load(file)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法读取或解析文件: {file_path}\n错误: {str(e)}")
        return None

    # 新增部分：保存并读取目录路径
    def save_last_directory(self, directory):
        """保存上次选择的目录路径到文件"""
        settings = {'last_directory': directory}
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)

    def load_last_directory(self):
        """加载上次保存的目录路径"""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                last_directory = settings.get('last_directory', '')
                self.directory_path.setText(last_directory)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlayFinder()
    window.show()
    sys.exit(app.exec())
