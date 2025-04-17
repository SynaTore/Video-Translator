from PyQt6.QtWidgets import QApplication, QMessageBox
from UI.main_window import MainWindow
import sys
import os

def check_environment():
    required_env_vars = [
        'VIDEOS_PATH',
        'AZURE_STORAGE',
        'AZURE_CONTAINER',
        'AZURE_SPEECH_SERVICE_KEY',
        'AZURE_TRANSLATOR_KEY',
        'REGION'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Check for required environment variables
    missing_vars = check_environment()
    if missing_vars:
        QMessageBox.critical(None, "Configuration Error",
                           f"Missing required environment variables:\n{', '.join(missing_vars)}\n\n"
                           "Please set these in your .env file.")
        sys.exit(1)
        
    # Create videos directory if it doesn't exist
    videos_path = os.getenv('VIDEOS_PATH')
    if not os.path.exists(videos_path):
        os.makedirs(videos_path)
    
    # Start the application
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
