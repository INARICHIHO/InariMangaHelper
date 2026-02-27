import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QSlider, QTextEdit, QComboBox, QProgressBar, QFrame, QSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon  # 确保导入了 QIcon

# --- 第一步：定义资源路径解析函数 ---
def get_resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和 PyInstaller 环境 """
    if hasattr(sys, '_MEIPASS'):
        # 打包后，资源会被解压到 sys._MEIPASS 目录下
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境下，相对于当前运行目录的路径
    return os.path.join(os.path.abspath("."), relative_path)

# --- 第二步：使用解析函数加载本地化资源 ---
# --- 修正后的导入部分 ---
try:
    # 获取项目根目录 (main.py 的上一级)
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 动态获取 locales 的绝对路径
    locales_dir = get_resource_path("locales")
    
    # 将 locales 所在的父目录加入系统路径，这样才能 import locales
    parent_dir = os.path.dirname(locales_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        
    from locales import zh, en, jp
except Exception as e:
    # 打印更详细的路径信息方便排查
    print(f"❌ Error: Locales not found.")
    print(f"Looking in: {locales_dir}")
    print(f"Details: {e}")
    sys.exit(1)

from core import run_rename, run_psd_export

class WorkerThread(QThread):
    progress_text = pyqtSignal(str) 
    progress_val = pyqtSignal(int)  
    finished = pyqtSignal()

    def __init__(self, folder_path, opacity, mode, texts):
        super().__init__()
        self.folder_path = folder_path
        self.opacity = opacity
        self.mode = mode 
        self.texts = texts

    def run(self):
        if self.mode == 1 or self.mode == 3:
            self.progress_text.emit(self.texts["log_rename"])
            run_rename(self.folder_path)
            self.progress_val.emit(50 if self.mode == 3 else 100)
        
        if self.mode == 2 or self.mode == 3:
            self.progress_text.emit(self.texts["log_psd"])
            def update_ui_progress(v):
                val = 50 + int(v/2) if self.mode == 3 else v
                self.progress_val.emit(val)
            run_psd_export(self.folder_path, self.opacity, update_ui_progress)
        
        self.progress_text.emit(self.texts["log_finish"])
        self.progress_val.emit(100)
        self.finished.emit()

class InariHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # --- 第三步：设置窗口左上角的图标 ---
        # 路径指向 assets 文件夹
        icon_path = get_resource_path("assets/inari.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"DEBUG: Icon not found at: {icon_path}")

        self.folder_path = ""
        self.current_lang = "zh"
        self.lang_dict = {"zh": zh.texts, "en": en.texts, "jp": jp.texts}
        self.setAcceptDrops(True) 
        self.initUI()
        self.apply_styles()
        self.retranslate_ui()

    def initUI(self):
        self.resize(600, 750)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(15)

        # --- Header Area ---
        header_layout = QHBoxLayout()
        self.title_label = QLabel("Inari Helper")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #004A8D;")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["简体中文", "English", "日本語"])
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.lang_combo)
        main_layout.addLayout(header_layout)

        # --- Section 1: Folder Selection ---
        self.path_card = QFrame()
        self.path_card.setObjectName("Card")
        path_layout = QVBoxLayout(self.path_card)
        self.path_label = QLabel()
        self.btn_browse = QPushButton()
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.btn_browse)
        main_layout.addWidget(self.path_card)

        # --- Section 2: Settings ---
        self.settings_card = QFrame()
        self.settings_card.setObjectName("Card")
        settings_layout = QVBoxLayout(self.settings_card)
        
        header_row = QHBoxLayout()
        self.opacity_title = QLabel()
        self.opacity_title.setStyleSheet("font-weight: bold; color: #004A8D;")
        
        self.spin_box = QSpinBox()
        self.spin_box.setRange(0, 100)
        self.spin_box.setValue(50)
        self.spin_box.setSuffix("%")
        self.spin_box.setFixedWidth(85)
        self.spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_row.addWidget(self.opacity_title)
        header_row.addStretch()
        header_row.addWidget(self.spin_box)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        
        settings_layout.addLayout(header_row)
        settings_layout.addWidget(self.slider)
        main_layout.addWidget(self.settings_card)

        # --- Section 3: Actions ---
        btn_layout = QHBoxLayout()
        self.btn_rename = QPushButton()
        self.btn_psd = QPushButton()
        self.btn_all = QPushButton()
        self.btn_all.setObjectName("PrimaryBtn")
        btn_layout.addWidget(self.btn_rename)
        btn_layout.addWidget(self.btn_psd)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.btn_all)

        # --- Section 4: Progress & Logs ---
        self.pbar = QProgressBar()
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.pbar)
        main_layout.addWidget(self.log_area)

        # --- Signal Connections ---
        self.lang_combo.currentIndexChanged.connect(self.handle_lang_change)
        self.btn_browse.clicked.connect(self.get_folder)
        self.slider.valueChanged.connect(self.spin_box.setValue)
        self.spin_box.valueChanged.connect(self.slider.setValue)
        
        self.btn_rename.clicked.connect(lambda: self.start_task(1))
        self.btn_psd.clicked.connect(lambda: self.start_task(2))
        self.btn_all.clicked.connect(lambda: self.start_task(3))

    def apply_styles(self):
        # ... 这里保持你之前的 QSS 样式不变 ...
        self.setStyleSheet("""
            QMainWindow { background-color: #F8FBFF; }
            QLabel { color: #334455; font-family: "Segoe UI", "Microsoft YaHei"; }
            QFrame#Card {
                background-color: white; border: 1px solid #E1E9F5;
                border-radius: 12px; padding: 10px;
            }
            QPushButton {
                background-color: #FFFFFF; border: 1px solid #D1D9E6;
                border-radius: 8px; padding: 10px; color: #445566;
            }
            QPushButton:hover { background-color: #F0F5FF; border-color: #0078D4; }
            QPushButton#PrimaryBtn {
                background-color: #0078D4; color: white; font-weight: bold; border: none;
            }
            QPushButton#PrimaryBtn:hover { background-color: #005A9E; }
            QProgressBar {
                border: none; background-color: #E1E9F5;
                height: 8px; text-align: center; border-radius: 4px;
            }
            QProgressBar::chunk { background-color: #0078D4; border-radius: 4px; }
            QTextEdit {
                background-color: white; border: 1px solid #E1E9F5;
                border-radius: 8px; color: #556677;
                font-family: "Cascadia Code", "Consolas";
            }
            QSlider::groove:horizontal { height: 4px; background: #E1E9F5; border-radius: 2px; }
            QSlider::handle:horizontal {
                background: #0078D4; width: 18px; height: 18px;
                margin: -7px 0; border-radius: 9px;
            }
            QSpinBox {
                border: 2px solid #E1E9F5; border-radius: 6px; padding: 2px 5px;
                background: #F8FBFF; color: #0078D4; font-weight: bold;
            }
            QSpinBox:focus { border: 2px solid #0078D4; }
            QSpinBox::up-button, QSpinBox::down-button { border: none; background: transparent; }
        """)

    def handle_lang_change(self, index):
        mapping = {0: "zh", 1: "en", 2: "jp"}
        self.current_lang = mapping.get(index, "zh")
        self.retranslate_ui()

    def retranslate_ui(self):
        t = self.lang_dict[self.current_lang]
        self.setWindowTitle(t["title"])
        folder_display = self.folder_path if self.folder_path else "---"
        self.path_label.setText(f"<b>{t['select_folder']}</b><br><span style='color:#667788;'>{folder_display}</span>")
        self.btn_browse.setText(t["browse"])
        self.opacity_title.setText(t["opacity_label"])
        self.btn_rename.setText(t["rename_only"])
        self.btn_psd.setText(t["psd_only"])
        self.btn_all.setText(t["run_all"])

    def get_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Folder")
        if path:
            self.folder_path = path
            self.retranslate_ui()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dropEvent(self, event):
        path = event.mimeData().urls()[0].toLocalFile()
        if os.path.isdir(path):
            self.folder_path = path
            self.retranslate_ui()

    def start_task(self, mode):
        t = self.lang_dict[self.current_lang]
        if not self.folder_path: 
            self.log_area.append(t["err_no_path"])
            return
        self.pbar.setValue(0)
        self.worker = WorkerThread(self.folder_path, int(self.slider.value()*2.55), mode, t)
        self.worker.progress_text.connect(self.log_area.append)
        self.worker.progress_val.connect(self.pbar.setValue)
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InariHelper()
    window.show()
    sys.exit(app.exec())