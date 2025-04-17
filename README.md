# Video Translator

A desktop application for translating video content using Azure Cognitive Services.

## Features

- Download videos from YouTube
- Extract audio from videos
- Transcribe audio to text
- Translate text to multiple languages
- Convert translated text to speech
- Combine translated audio with original video
- Support for multiple languages and voices

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed and available in system PATH
- Azure CLI installed
- Azure subscription with following services:
  - Azure Speech Service
  - Azure Translator
  - Azure Blob Storage

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SynaTore/video-translator.git
cd video-translator
```

2. Login to Azure:
```bash
az login
```
Follow the instructions in your browser to complete the authentication process.

3. Create a .env file with your Azure credentials:
```env
VIDEOS_PATH=path/to/videos/directory
AZURE_STORAGE=your-storage-account-name
AZURE_CONTAINER=your-container-name
AZURE_SPEECH_SERVICE_KEY=your-speech-service-key
AZURE_TRANSLATOR_KEY=your-translator-key
REGION=your-azure-region
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Enter a YouTube URL in the input field

3. Select source and target languages

4. Click "Translate" to start the translation process

5. The translated video will be saved in your videos directory

## Project Structure

- `converter/`: Handles video/audio conversion
- `download/`: YouTube video download functionality
- `speech/`: Text-to-speech conversion using Azure
- `transcribe/`: Audio transcription using Azure
- `translate/`: Text translation using Azure
- `UI/`: PyQt6-based user interface
- `Video/`: Working directory for video processing

## License

MIT License. See LICENSE file for details.

## Acknowledgments

- Azure Cognitive Services
- PyTube for YouTube downloads
- FFmpeg for media processing
- PyQt6 for the user interface
