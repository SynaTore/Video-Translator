from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QFileDialog, QLineEdit,
    QMessageBox, QProgressBar, QFrame, QGridLayout, QSlider,
    QStackedWidget, QToolButton, QStyleFactory
)
from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal, QSize, QMimeData
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QDragEnterEvent, QDropEvent
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
import os
import settings
from Video_Translator import VideoTranslate
import subprocess
import platform
import logging
import utils

class TranslationWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, translator, params):
        super().__init__()
        self.translator = translator
        self.params = params
        self.logger = logging.getLogger('VideoTranslator')

    def run(self):
        try:
            self.progress.emit(10)
            self.logger.info("Starting translation process")
            output_path = self.translator.translate_from_url(**self.params)
            self.progress.emit(100)
            self.logger.info(f"Translation completed successfully: {output_path}")
            self.finished.emit(output_path)
        except Exception as e:
            self.logger.error(f"Translation failed: {str(e)}")
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        # Language configurations
        self.language_configs = {
            "en-US": {
                "display": "English (en-US)",
                "voices": [
                    "en-US-JennyNeural",
                    "en-US-GuyNeural",
                    "en-US-AriaNeural",
                    "en-US-SaraNeural",
                    "en-US-ChristopherNeural"
                ]
            },
            "zh-CN": {
                "display": "中文 (zh-CN)",
                "voices": [
                    "zh-CN-XiaoxiaoNeural",
                    "zh-CN-YunxiNeural",
                    "zh-CN-XiaochenNeural",
                    "zh-CN-YunjianNeural",
                    "zh-CN-XiaoyiNeural"
                ]
            },
            "ar-SA": {
                "display": "العربية (ar-SA)",
                "voices": [
                    "ar-SA-ZariyahNeural",
                    "ar-SA-HamedNeural",
                    "ar-SA-FahedNeural",
                    "ar-SA-NasserNeural",
                    "ar-SA-AmanyNeural"
                ]
            },
            "fr-FR": {
                "display": "Français (fr-FR)",
                "voices": [
                    "fr-FR-DeniseNeural",
                    "fr-FR-HenriNeural",
                    "fr-FR-AlainNeural",
                    "fr-FR-BrigitteNeural",
                    "fr-FR-YvesNeural"
                ]
            },
            "de-DE": {
                "display": "Deutsch (de-DE)",
                "voices": [
                    "de-DE-KatjaNeural",
                    "de-DE-ConradNeural",
                    "de-DE-AmalaNeural",
                    "de-DE-BerndNeural",
                    "de-DE-ElkeNeural"
                ]
            },
            "es-ES": {
                "display": "Español (es-ES)",
                "voices": [
                    "es-ES-ElviraNeural",
                    "es-ES-AlvaroNeural",
                    "es-ES-AbrilNeural",
                    "es-ES-ArnauNeural",
                    "es-ES-DarioNeural"
                ]
            }
        }
        # Add reverse lookup for language codes
        self.display_to_code = {
            conf["display"]: code for code, conf in self.language_configs.items()
        }

        super().__init__()
        self.logger = logging.getLogger('VideoTranslator')
        self.logger.info("Initializing main window")
        self.setWindowTitle("Video Translator")
        self.setMinimumSize(1024, 768)  # Larger window for video players
        
        # Apply custom styling
        self.setup_theme()
        
        self.translator = VideoTranslate(settings)
        
        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # URL section with fixed height
        url_section = QWidget()
        url_section.setFixedHeight(50)
        url_layout = QHBoxLayout(url_section)
        url_layout.setContentsMargins(5, 5, 5, 5)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL or drag & drop video file")
        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self.preview_video)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_video)
        
        url_layout.addWidget(QLabel("Video Source:"))
        url_layout.addWidget(self.url_input, stretch=1)
        url_layout.addWidget(self.browse_button)
        url_layout.addWidget(self.preview_button)
        
        layout.addWidget(url_section)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Video preview section
        preview_layout = QVBoxLayout()
        
        # Stacked widget to switch between original and translated video
        self.video_stack = QStackedWidget()
        
        # Create single video widget and player
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(360)  # Standard 16:9 ratio
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Add video widget to stack
        self.video_stack.addWidget(self.video_widget)
        preview_layout.addWidget(self.video_stack)
        
        # Playback controls
        controls_layout = QHBoxLayout()
        
        self.play_button = QToolButton()
        self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.play_button.clicked.connect(self.toggle_playback)
        
        # Volume control
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(
            lambda v: self.audio_output.setVolume(v / 100))
        
        # Video switch button
        self.switch_video_button = QPushButton("Switch Video")
        self.switch_video_button.clicked.connect(self.switch_video)
        self.switch_video_button.setEnabled(False)
        
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(QLabel("Volume:"))
        controls_layout.addWidget(self.volume_slider)
        controls_layout.addWidget(self.switch_video_button)
        
        preview_layout.addLayout(controls_layout)
        layout.addLayout(preview_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lang_layout.setSpacing(20)  # Add more space between elements
        
        # Create containers for each combo
        source_container = QVBoxLayout()
        source_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        target_container = QVBoxLayout()
        target_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        voice_container = QVBoxLayout()
        voice_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Source language selection with label
        source_label = QLabel("Source Language:")
        source_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.source_lang = QComboBox()
        self.source_lang.setFixedWidth(200)
        self.source_lang.addItems([conf["display"] for conf in self.language_configs.values()])
        source_container.addWidget(source_label)
        source_container.addWidget(self.source_lang)
        
        # Target language selection with label
        target_label = QLabel("Translate To:")
        target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.target_lang = QComboBox()
        self.target_lang.setFixedWidth(200)
        self.target_lang.addItems([conf["display"] for conf in self.language_configs.values()])
        target_container.addWidget(target_label)
        target_container.addWidget(self.target_lang)
        
        # Voice selection with label
        voice_label = QLabel("Voice:")
        voice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voice_select = QComboBox()
        self.voice_select.setFixedWidth(200)
        self.target_lang.currentIndexChanged.connect(self.update_voices)
        voice_container.addWidget(voice_label)
        voice_container.addWidget(self.voice_select)
        
        # Add containers to main layout
        lang_layout.addLayout(source_container)
        lang_layout.addLayout(target_container)
        lang_layout.addLayout(voice_container)
        
        layout.addLayout(lang_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.translate_button = QPushButton("Translate Video")
        self.translate_button.clicked.connect(self.translate_video)
        self.open_result_button = QPushButton("Play in System Player")
        self.open_result_button.clicked.connect(self.open_in_system_player)
        self.show_folder_button = QPushButton("Show in Folder")
        self.show_folder_button.clicked.connect(self.show_in_folder)
        self.open_result_button.setEnabled(False)
        self.show_folder_button.setEnabled(False)
        controls_layout.addWidget(self.translate_button)
        controls_layout.addWidget(self.open_result_button)
        controls_layout.addWidget(self.show_folder_button)
        layout.addLayout(controls_layout)
        
        # Add keyboard shortcuts
        self.preview_button.setShortcut("Alt+P")
        self.preview_button.setToolTip("Preview Video (Alt+P)")
        
        self.translate_button.setShortcut("Alt+T")
        self.translate_button.setToolTip("Translate Video (Alt+T)")
        
        self.switch_video_button.setShortcut("Alt+S")
        self.switch_video_button.setToolTip("Switch Video (Alt+S)")
        
        self.open_result_button.setShortcut("Alt+O")
        self.open_result_button.setToolTip("Open in System Player (Alt+O)")
        
        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
    
    def setup_theme(self):
        # Set application style
        self.setStyle(QStyleFactory.create("Fusion"))
        
        # Set dark theme colors
        dark_palette = QPalette()
        
        # Define colors
        background = QColor("#2B2B2B")
        foreground = QColor("#F0F0F0")
        accent = QColor("#007ACC")
        secondary = QColor("#3C3F41")
        
        # Apply colors to palette
        dark_palette.setColor(QPalette.ColorRole.Window, background)
        dark_palette.setColor(QPalette.ColorRole.WindowText, foreground)
        dark_palette.setColor(QPalette.ColorRole.Base, secondary)
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, background)
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, foreground)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, foreground)
        dark_palette.setColor(QPalette.ColorRole.Text, foreground)
        dark_palette.setColor(QPalette.ColorRole.Button, secondary)
        dark_palette.setColor(QPalette.ColorRole.ButtonText, foreground)
        dark_palette.setColor(QPalette.ColorRole.Highlight, accent)
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, foreground)
        
        self.setPalette(dark_palette)
        
        # Set application-wide custom font
        app_font = QFont("Segoe UI", 10)  # Removed DemiBold
        self.setFont(app_font)
        
        # Apply custom stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2B2B2B;
            }
            QLabel {
                color: #F0F0F0;
                font-size: 11px;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005C9F;
            }
            QPushButton:disabled {
                background-color: #4D4D4D;
                color: #A0A0A0;
            }
            QLineEdit {
                padding: 8px;
                border-radius: 4px;
                background-color: #3C3F41;
                color: #F0F0F0;
                border: 1px solid #5C5C5C;
            }
            QComboBox {
                padding: 8px;
                border-radius: 4px;
                background-color: #3C3F41;
                color: #F0F0F0;
                border: 1px solid #5C5C5C;
            }
            QProgressBar {
                border: 2px solid #007ACC;
                border-radius: 5px;
                text-align: center;
                color: #F0F0F0;
            }
            QProgressBar::chunk {
                background-color: #007ACC;
            }
            QSlider::groove:horizontal {
                border: 1px solid #5C5C5C;
                height: 8px;
                background: #3C3F41;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #007ACC;
                border: none;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QToolButton {
                background-color: #3C3F41;
                border: none;
                padding: 6px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #4C4F51;
            }
            QVideoWidget {
                background-color: #1E1E1E;
                border: 2px solid #3C3F41;
                border-radius: 8px;
            }
            QStatusBar {
                color: #F0F0F0;
            }
        """)

    def update_voices(self):
        self.voice_select.clear()
        display_text = self.target_lang.currentText()
        lang_code = self.display_to_code.get(display_text)
        if lang_code in self.language_configs:
            self.voice_select.addItems(self.language_configs[lang_code]["voices"])

    def toggle_playback(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))
        else:
            self.media_player.play()
            self.play_button.setIcon(QIcon.fromTheme("media-playback-pause"))

    def switch_video(self):
        if hasattr(self, 'current_video') and self.current_video == 'original':
            # Switch to translated
            if hasattr(self, 'last_output_path'):
                self.media_player.setSource(QUrl.fromLocalFile(self.last_output_path))
                self.current_video = 'translated'
        else:
            # Switch to original
            if hasattr(self, 'original_path'):
                self.media_player.setSource(QUrl.fromLocalFile(self.original_path))
                self.current_video = 'original'
        self.media_player.play()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = event.mimeData().urls()
        if files:
            file_path = files[0].toLocalFile()
            if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.mkv')):
                self.url_input.setText(file_path)
                self.translator.video_url = None
                self.translator.video_path = file_path
                self.preview_video()
            else:
                QMessageBox.warning(self, "Invalid File", 
                                  "Please drop a valid video file (mp4, avi, mov, wmv, mkv)")

    def browse_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.wmv *.mkv)"
        )
        if file_path:
            self.url_input.setText(file_path)
            self.translator.video_url = None
            self.translator.video_path = file_path
            self.preview_video()

    def preview_video(self):
        if not self.url_input.text():
            self.logger.warning("No URL or file provided for preview")
            return
        
        try:
            self.logger.info(f"Previewing video from source: {self.url_input.text()}")
            if utils.is_url(self.url_input.text()):
                self.translator.video_url = self.url_input.text()
                self.translator.video_path = None
                video_path = self.translator._VideoTranslate__download_video()
            else:
                video_path = self.url_input.text()
            
            self.original_path = video_path
            self.current_video = 'original'
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.audio_output.setVolume(0.5)
            self.media_player.play()
            self.play_button.setIcon(QIcon.fromTheme("media-playback-pause"))
            self.status_label.setStyleSheet("color: #F0F0F0; font-weight: bold;")
            self.logger.info("Video preview started successfully")
        except Exception as e:
            self.logger.error(f"Video preview failed: {str(e)}")
            self.status_label.setStyleSheet("color: #FF6B68; font-weight: bold;")
            QMessageBox.critical(self, "Error", f"Failed to preview video: {str(e)}")

    def open_in_system_player(self):
        if not hasattr(self, 'last_output_path') or not os.path.exists(self.last_output_path):
            self.logger.warning("Attempted to open non-existent output file")
            return
            
        try:
            self.logger.info(f"Opening video in system player: {self.last_output_path}")
            if platform.system() == 'Windows':
                os.startfile(self.last_output_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self.last_output_path])
            else:  # Linux
                subprocess.run(['xdg-open', self.last_output_path])
        except Exception as e:
            self.logger.error(f"Failed to open video in system player: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open video: {str(e)}")

    def show_in_folder(self):
        if not hasattr(self, 'last_output_path') or not os.path.exists(self.last_output_path):
            self.logger.warning("Attempted to show non-existent output file")
            return
            
        try:
            self.logger.info(f"Showing video in folder: {self.last_output_path}")
            if platform.system() == 'Windows':
                abs_path = os.path.abspath(self.last_output_path)
                subprocess.run(['explorer', '/select,', abs_path], shell=True)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', '-R', self.last_output_path])
            else:  # Linux
                subprocess.run(['xdg-open', os.path.dirname(self.last_output_path)])
        except Exception as e:
            self.logger.error(f"Failed to show video in folder: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to show video location: {str(e)}")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def translate_video(self):
        url = self.url_input.text()
        if not url:
            self.logger.warning("Translation attempted without URL")
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL")
            return
            
        source_display = self.source_lang.currentText()
        target_display = self.target_lang.currentText()
        source_lang = self.display_to_code.get(source_display)
        target_lang = self.display_to_code.get(target_display)
        voice = self.voice_select.currentText()
        
        if not target_lang:
            self.logger.error("Invalid target language selection")
            QMessageBox.critical(self, "Error", "Invalid target language selection")
            return
            
        # Validate language-voice match
        if not voice in self.language_configs[target_lang]["voices"]:
            self.logger.error(f"Voice {voice} doesn't match target language {target_lang}")
            QMessageBox.critical(self, "Error", "Selected voice doesn't match target language")
            return
            
        self.logger.info(f"Starting translation from {source_lang} to {target_lang} using voice {voice}")
        final_name = f"translated_video_{target_lang}.mp4"
        
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.translate_button.setEnabled(False)
        
        # Create worker thread
        self.worker = TranslationWorker(
            self.translator,
            {
                "source_language": source_lang,
                "target_language": target_lang,
                "voice": voice,
                "final_name": final_name,
                "translation_language": target_lang[:2],
                "option": 1
            }
        )
        
        # Connect signals
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.translation_finished)
        self.worker.error.connect(self.translation_error)
        
        # Start translation in background
        self.translator.video_url = url
        self.worker.start()

    def translation_finished(self, output_path):
        self.logger.info(f"Translation completed: {output_path}")
        self.translate_button.setEnabled(True)
        self.last_output_path = output_path
        self.open_result_button.setEnabled(True)
        self.show_folder_button.setEnabled(True)
        self.switch_video_button.setEnabled(True)
        
        # Switch to translated video
        self.media_player.setSource(QUrl.fromLocalFile(output_path))
        self.current_video = 'translated'
        self.media_player.play()
        
        self.status_label.setText(f"Translation completed! Saved as: {output_path}")
        self.status_label.setStyleSheet("color: #85C47C; font-weight: bold;")
        QMessageBox.information(self, "Success", 
                              f"Video has been translated and saved as:\n{output_path}")

    def translation_error(self, error_msg):
        self.logger.error(f"Translation error: {error_msg}")
        self.progress_bar.hide()
        self.translate_button.setEnabled(True)
        self.status_label.setStyleSheet("color: #FF6B68; font-weight: bold;")
        QMessageBox.critical(self, "Error", f"Translation failed: {error_msg}")
        self.status_label.setText(f"Error: {error_msg}")

    def closeEvent(self, event):
        """Clean up resources when closing the window."""
        self.logger.info("Closing main window")
        try:
            if hasattr(self, 'media_player'):
                self.media_player.stop()
            if hasattr(self, 'worker') and self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
        event.accept()