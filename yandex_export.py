import sys
import re
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout,
                             QLineEdit, QPushButton, QLabel, QFileDialog,
                             QMessageBox, QProgressBar, QRadioButton,
                             QButtonGroup, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QCursor

class YandexMusicExporter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupStyles()
        self.old_pos = None
        
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(700, 220)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Кастомный заголовок
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(30)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 0, 5, 0)
        
        self.title_label = QLabel("Экспорт плейлистов — ЯМузыка")
        self.title_label.setObjectName("titleLabel")
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)
        
        self.min_btn = QPushButton("–")
        self.min_btn.setObjectName("minButton")
        self.min_btn.clicked.connect(self.showMinimized)
        self.min_btn.setFixedSize(25, 25)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setFixedSize(25, 25)
        
        btn_layout.addWidget(self.min_btn)
        btn_layout.addWidget(self.close_btn)
        
        title_layout.addWidget(self.title_label)
        title_layout.addLayout(btn_layout)
        title_bar.setLayout(title_layout)
        main_layout.addWidget(title_bar)

        # Основной контент
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(25, 20, 25, 20)
        content_layout.setSpacing(30)

        # Левый блок (ввод данных)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Вставьте ссылку на плейлист...")
        self.url_input.textChanged.connect(self.sanitize_url)
        left_layout.addWidget(self.url_input)

        format_layout = QHBoxLayout()
        self.format_group = QButtonGroup(self)
        
        self.txt_radio = QRadioButton("TXT")
        self.csv_radio = QRadioButton("CSV")
        self.json_radio = QRadioButton("JSON")
        self.txt_radio.setChecked(True)
        
        for rb in [self.txt_radio, self.csv_radio, self.json_radio]:
            self.format_group.addButton(rb)
            format_layout.addWidget(rb)
        
        left_layout.addLayout(format_layout)
        content_layout.addLayout(left_layout)

        # Правый блок (управление)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        self.export_btn = QPushButton("Экспорт")
        self.export_btn.setObjectName("exportButton")
        self.export_btn.clicked.connect(self.start_export)
        right_layout.addWidget(self.export_btn)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        right_layout.addWidget(self.progress)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        right_layout.addWidget(self.status_label)

        content_layout.addLayout(right_layout)
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)

        self.setLayout(main_layout)

    def setupStyles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: 'Segoe UI';
            }
            #titleBar {
                background-color: #ffffff;
                border-bottom: 1px solid #eeeeee;
            }
            #titleLabel {
                font-size: 13px;
                color: #666666;
                font-weight: 500;
            }
            #minButton, #closeButton {
                border: none;
                background: transparent;
                font-size: 18px;
                color: #999999;
                border-radius: 3px;
            }
            #minButton:hover {
                background-color: #ffcc00;
                color: white;
            }
            #closeButton:hover {
                background-color: #f80000;
                color: white;
            }
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                color: #404040;
                min-height: 36px;
            }
            QLineEdit:focus {
                border-color: #ffcc00;
                background-color: #fff9e6;
            }
            QRadioButton {
                font-size: 14px;
                color: #404040;
                spacing: 8px;
                min-height: 30px;
                padding: 5px;
            }
            QRadioButton:hover {
                background-color: rgba(255, 204, 0, 0.2);
                border-radius: 5px;
                border: none;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator::unchecked {
                border: 2px solid #e0e0e0;
                border-radius: 9px;
                background: white;
            }
            QRadioButton::indicator::checked {
                border: 2px solid #f80000;
                border-radius: 9px;
                background-color: #f80000;
            }
            QRadioButton::indicator::unchecked {
                border: 2px solid #e0e0e0;
                border-radius: 9px;
                background: white;
            }
            #exportButton {
                background-color: #ffffff;
                color: #f80000;
                border: 2px solid #f80000;
                border-radius: 5px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                min-height: 40px;
                min-width: 120px;
            }
            #exportButton:hover {
                background-color: #f80000;
                color: white;
            }
            #exportButton:disabled {
                border-color: #cccccc;
                color: #999999;
                background-color: #f5f5f5;
            }
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                height: 8px;
                background: white;
            }
            QProgressBar::chunk {
                background-color: #ffcc00;
                border-radius: 4px;
            }
            QLabel {
                color: #666666;
                font-size: 13px;
                max-height: 40px;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def sanitize_url(self):
        """Очистка URL от параметров"""
        url = self.url_input.text()
        clean_url = url.split('?')[0].strip()
        if url != clean_url:
            self.url_input.setText(clean_url)
        
    def start_export(self):
        url = self.url_input.text().strip()
        if not url:
            self.show_error("Введите ссылку на плейлист")
            return

        self.set_ui_enabled(False)
        self.progress.setVisible(True)
        self.update_status("Начало обработки...", 0)

        QTimer.singleShot(100, lambda: self.process_export(url))

    def process_export(self, url):
        try:
            self.update_status("Проверка ссылки...", 10)
            owner_id, playlist_id, username = self.parse_url(url)
            
            self.update_status("Загрузка данных...", 30)
            tracks, playlist_title = self.get_playlist_tracks(owner_id, playlist_id)
            
            self.update_status("Сохранение файла...", 70)
            self.save_tracks(tracks, playlist_title, username)
            
            self.update_status("Готово! Файл успешно сохранен", 100)
            QTimer.singleShot(1000, lambda: self.status_label.clear())

        except Exception as e:
            self.show_error(str(e))
        finally:
            self.set_ui_enabled(True)
            self.progress.setVisible(False)

    def parse_url(self, url):
        clean_url = url.split('?')[0]
        parts = clean_url.split('/')
        
        try:
            user_index = parts.index('users') + 1
            playlist_index = parts.index('playlists') + 1
            username = parts[user_index]
            return parts[user_index], parts[playlist_index], username
        except (ValueError, IndexError):
            raise ValueError("Некорректный формат ссылки. Пример правильной ссылки:\n"
                             "https://music.yandex.ru/users/ваш_логин/playlists/номер")

    def get_playlist_tracks(self, owner_id, playlist_id):
        api_url = f'https://music.yandex.ru/handlers/playlist.jsx'
        params = {'owner': owner_id, 'kinds': playlist_id}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': f'https://music.yandex.ru/users/{owner_id}/playlists/{playlist_id}'
        }

        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            playlist_title = data['playlist']['title']
            tracks = []
            
            for track in data['playlist']['tracks']:
                title = track.get('title', 'Без названия').strip()
                artists = ', '.join(a.get('name', 'Неизвестен').strip() for a in track.get('artists', []))
                tracks.append((title, artists))

            return tracks, playlist_title

        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка подключения: {str(e)}")
        except KeyError:
            raise Exception("Не удалось распознать ответ сервера")

    def save_tracks(self, tracks, playlist_title, username):
        # Определение формата
        if self.txt_radio.isChecked():
            file_ext = 'txt'
        elif self.csv_radio.isChecked():
            file_ext = 'csv'
        else:
            file_ext = 'json'
        
        # Генерация безопасного имени файла
        clean_title = re.sub(r'[\\/*?:"<>|]', "", playlist_title)
        clean_username = re.sub(r'[\\/*?:"<>|]', "", username)
        default_name = f"{clean_title} ({clean_username}).{file_ext}"
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            'Сохранить файл',
            default_name,
            f'{file_ext.upper()} Files (*.{file_ext})'
        )

        if not filename:
            raise Exception("Сохранение отменено")

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if file_ext == 'txt':
                    for title, artist in tracks:
                        f.write(f"{artist} - {title}\n")
                elif file_ext == 'csv':
                    f.write("Исполнитель;Название\n")
                    for title, artist in tracks:
                        f.write(f'"{artist}";"{title}"\n')
                elif file_ext == 'json':
                    import json
                    data = [{"artist": a, "title": t} for t, a in tracks]
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.status_label.setStyleSheet("color: #38A169;")
        except Exception as e:
            raise Exception(f"Ошибка сохранения: {str(e)}")

    def update_status(self, message, progress):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #666666;")
        self.progress.setValue(progress)
        QApplication.processEvents()

    def set_ui_enabled(self, state):
        self.export_btn.setEnabled(state)
        self.url_input.setEnabled(state)
        for rb in [self.txt_radio, self.csv_radio, self.json_radio]:
            rb.setEnabled(state)

    def show_error(self, message):
        self.status_label.setStyleSheet("color: #E53E3E;")
        self.status_label.setText(message)
        QMessageBox.critical(self, "Ошибка", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont('Segoe UI', 11))
    ex = YandexMusicExporter()
    ex.show()
    sys.exit(app.exec_())