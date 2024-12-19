from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QMenuBar, QAction,
    QTextEdit, QPushButton, QFileDialog, QTabWidget, QLabel, QListWidget,
    QHBoxLayout, QMessageBox 
)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap
import sys
import json
import base64

class ImageThumbnail(QWidget):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Миниатюра изображения
        self.image_label = QLabel()
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(100, 50)  # Размер миниатюры
        self.layout.addWidget(self.image_label)

        # Заголовок (можно добавить имя файла или описание)
        self.caption = QLabel("Image")
        self.caption.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.caption)

        # Состояние окна
        self.dialog = None

    def mousePressEvent(self, event):
        if self.dialog and self.dialog.isVisible():
            # Закрыть диалоговое окно, если оно уже открыто
            self.dialog.close()
        else:
            # Создать и открыть диалоговое окно
            self.dialog = QDialog(self)
            self.dialog.setWindowTitle("Image Viewer")
            self.dialog.setGeometry(200, 200, 800, 600)  # Увеличиваем размер окна для изображений
    
            # Отображение увеличенного изображения
            dialog_layout = QVBoxLayout(self.dialog)
            enlarged_label = QLabel()
    
            # Загружаем изображение с сохранением пропорций
            pixmap = self.image_label.pixmap()
            pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Увеличиваем с сохранением пропорций
    
            enlarged_label.setPixmap(pixmap)
            enlarged_label.setAlignment(Qt.AlignCenter)  # Выравниваем изображение по центру
            dialog_layout.addWidget(enlarged_label)
    
            self.dialog.exec_()  # Запуск диалогового окна
    


class RPGEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPG Editor")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)

        self.file_menu = self.menu_bar.addMenu("File")
        self.new_action = QAction("New", self)
        self.open_action = QAction("Open", self)
        self.save_action = QAction("Save", self)
        self.export_action = QAction("Export", self)

        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.export_action)

        self.new_action.triggered.connect(self.create_new_file)
        self.open_action.triggered.connect(self.open_file)
        self.save_action.triggered.connect(self.save_file)
        self.export_action.triggered.connect(self.export_file)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.text_tab = QWidget()
        self.media_tab = QWidget()

        self.tab_widget.addTab(self.text_tab, "Text Editor")
        self.tab_widget.addTab(self.media_tab, "Media Manager")

        self.text_tab_layout = QVBoxLayout()
        self.text_tab.setLayout(self.text_tab_layout)

        self.text_edit = QTextEdit()
        self.text_tab_layout.addWidget(self.text_edit)

        self.media_tab_layout = QVBoxLayout()
        self.media_tab.setLayout(self.media_tab_layout)

        self.media_list = QListWidget()
        self.media_tab_layout.addWidget(self.media_list)

        self.add_media_button = QPushButton("Add Media")
        self.media_tab_layout.addWidget(self.add_media_button)
        self.add_media_button.clicked.connect(self.add_media)

        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.media_tab_layout.addWidget(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)

        self.profiles = {}
        self.current_file = None

    def create_new_file(self):
        self.text_edit.clear()
        self.media_list.clear()
        self.profiles = {}
        self.current_file = None

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "RPG Files (*.rpg);;All Files (*)", options=options
        )
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    data = json.load(file)
                    self.text_edit.setText(data.get("text", ""))
                    self.profiles = data.get("profiles", {})
                    self.current_file = file_name

                    # Загрузка медиаданных
                    self.media_files = data.get("media_files", [])
                    self.image_row_layout = QHBoxLayout()  # Горизонтальный ряд для изображений
                    for base64_image in self.media_files:
                        pixmap = self.decode_base64_to_pixmap(base64_image)
                        thumbnail = ImageThumbnail(pixmap)
                        self.image_row_layout.addWidget(thumbnail)
                    self.media_tab_layout.addLayout(self.image_row_layout)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w') as file:
                data = {
                    "text": self.text_edit.toPlainText(),
                    "profiles": self.profiles,
                    "media_files": self.media_files
                }
                json.dump(data, file)
        else:
            self.export_file()


    def display_base64_image(self, base64_str):
        try:
            img_data = base64.b64decode(base64_str)
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)  # Загружаем изображение из данных
            pixmap = pixmap.scaled(250, 100, aspectRatioMode=1)  # Ограничиваем размер
            self.display_image(pixmap)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display image: {e}")



    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w') as file:
                data = {
                    "text": self.text_edit.toPlainText(),
                    "profiles": self.profiles,
                    "media_files": [self.media_list.item(i).text() for i in range(self.media_list.count())]
                }
                json.dump(data, file)
        else:
            self.export_file()


    def export_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "RPG Files (*.rpg);;All Files (*)", options=options
        )
        if file_name:
            with open(file_name, 'w') as file:
                data = {
                    "text": self.text_edit.toPlainText(),
                    "profiles": self.profiles,
                    "media_files": [self.media_list.item(i).text() for i in range(self.media_list.count())]
                }
                json.dump(data, file)
            self.current_file = file_name



    def add_media(self):
        options = QFileDialog.Options()
        file_names, _ = QFileDialog.getOpenFileNames(
            self, "Add Media", "", 
            "Image Files (*.png *.jpg *.jpeg);;All Files (*)", 
            options=options
        )
        for file_name in file_names:
            try:
                # Ограничиваем размеры изображения
                pixmap = QPixmap(file_name)
                pixmap = pixmap.scaled(250, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Кодируем изображение в Base64
                with open(file_name, 'rb') as img_file:
                    img_data = img_file.read()
                    encoded_image = base64.b64encode(img_data).decode('utf-8')

                # Сохраняем Base64 строку
                self.media_files.append(encoded_image)

                # Создаем миниатюру и добавляем её в горизонтальный лейаут
                thumbnail = ImageThumbnail(pixmap)
                self.image_row_layout.addWidget(thumbnail)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add media: {e}")




    def display_image(self, pixmap):
    # Скрываем видео-плеер и отображаем изображение
        self.video_widget.hide()
        if not hasattr(self, 'image_label'):
            self.image_label = QLabel()
            self.media_tab_layout.addWidget(self.image_label)
        self.image_label.setPixmap(pixmap)
        self.image_label.setFixedSize(250, 100)  # Ограничение размера виджета
        self.image_label.show()


    def is_base64(self, s):
        try:
            # Убираем пробелы и проверяем длину
            if isinstance(s, str) and len(s) % 4 == 0:
                base64.b64decode(s, validate=True)
                return True
            return False
        except Exception:
            return False

    
    def display_base64_image(self, base64_str):
        try:
            img_data = base64.b64decode(base64_str)
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            pixmap = pixmap.scaled(250, 100, aspectRatioMode=1)  # Масштабирование до 250x100
            self.display_image(pixmap)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display image: {e}")
    
    def decode_base64_to_pixmap(self, base64_str):
        img_data = base64.b64decode(base64_str)
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)
        # Убедитесь, что pixmap получен в нужном формате
        return pixmap
 
    def closeEvent(self, event):
        self.media_player.stop()  # Останавливаем медиаплеер
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = RPGEditor()
    editor.show()
    sys.exit(app.exec_())
