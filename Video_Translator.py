import settings;
import utils;
from download import Download;
from converter import Converter
from transcribe import Transcribe
import transcribe
from speech import Speech
import os
import mix


class VideoTranslate:

    def __init__(self, settings: any) -> None:
        self.settings = settings
        self.video_url = None

    def translate_from_url(self, source_language, target_language, voice, final_name, translation_language, option):
        if not self.video_url:
            raise ValueError("Video URL not set")

        temp_files = []
        try:
            video_path = self.__download_video()
            temp_files.append(video_path)
            
            audio_path = settings.VIDEOS_PATH + "audio1.mp3"
            self.__get_mp3_from_mp4(video_path)
            temp_files.append(audio_path)
            
            transcribe = self.__get_text_from_long_audio(audio_path, source_language)
            if not transcribe:
                raise ValueError("Failed to transcribe audio")
                
            translated = self.__translate_long(transcribe, translation_language)
            if not translated:
                raise ValueError("Failed to translate text")
            
            translated = translated.replace('\n', '').replace('\r', '')
            self.__translated_to_speech(translated, voice)
            
            wav_path = settings.VIDEOS_PATH + "/extracted_data/0001.wav"
            output_path = os.path.join(self.settings.VIDEOS_PATH, final_name)
            
            mix.mixing(video_path, wav_path, output_path)
            return output_path
            
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
        finally:
            # Cleanup temporary files
            for file in temp_files:
                try:
                    if os.path.exists(file):
                        os.remove(file)
                except:
                    pass # Ignore cleanup errors

    def __get_url_from_video(self) -> None:

        url = input("Please, type the video url: ");

        if(utils.is_url(url)):
             self.video_url = url
        else:
             print('the url is not valid');

    def __download_video(self) -> str:
        if not self.video_url:
            raise ValueError("Video URL not set")

        video_path = self.settings.VIDEOS_PATH
        video = Download(video_path, self.video_url)
        video_path = video.dowload_YT()
        return video_path

    def __get_mp3_from_mp4(self, video_path: str, audio_name="audio1.mp3") -> str:

        converter  = Converter(video_path);
        converter.mp3_from_video(self.settings.VIDEOS_PATH, audio_name)

    def __wait_upload(self):
        input("Press Enter to continue...")
        print("Continuing after Enter was pressed")

    def __get_text_from_long_audio(self, file_mp3: str, language, option=1) -> str:
        
        transcribe = Transcribe(self.settings.AZURE_SPEECH_SERVICE, self.settings.REGION, self.settings.AZURE_STORAGE, self.settings.AZURE_CONTAINER, self.settings.AZURE_TRANSLATOR, self.settings.VIDEOS_PATH)
        return transcribe.transcribe_long(language, option)
    
    def __translate_long(self, transcribe_, target_language):
        transcribe = Transcribe(self.settings.AZURE_SPEECH_SERVICE, self.settings.REGION, self.settings.AZURE_STORAGE, self.settings.AZURE_CONTAINER, self.settings.AZURE_TRANSLATOR, self.settings.VIDEOS_PATH)
        return transcribe.translate_long(transcribe_, target_language)
    
    def __translated_to_speech(self, text: str, voice) -> None:

         azure_key = self.settings.AZURE_SPEECH_SERVICE
         region= self.settings.REGION

         speech  = Speech(azure_key, region)
         speech.text_to_mp3_long(text, voice, self.settings.VIDEOS_PATH)
         