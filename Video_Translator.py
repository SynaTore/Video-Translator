import settings;
import utils;
from download import Download;
from converter import Converter
from transcribe import Transcribe
from speech import Speech
import os
import mix

os.environ["FFMPEG_BINARY"] = "C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe"
class VideoTranslate:

    def __init__(self, settings: any) -> None:
        self.settings = settings
    def translate_from_url(self, target_language, voice, final_name, translation_language, option):

        self.__get_url_from_video()
        video_path = self.__download_video()
        mp3_file   = self.__get_mp3_from_mp4(video_path)
        self.__wait_upload()
        transcribe = self.__get_text_from_long_audio(settings.VIDEOS_PATH + "audio1.mp3", "en-US")
        translated = self.__translate_long(transcribe, translation_language).replace('\n', '').replace('\r', '');
        print(translated)
        # self.__translated_to_speech(translated, voice)
        # mix.mixing(self.settings.VIDEOS_PATH + "/test.mp4", self.settings.VIDEOS_PATH + "/extracted_data/0001.wav", self.settings.VIDEOS_PATH + "/mixed.mp4")
        # self.__wait_upload()
        subtitle = self.__get_text_from_long_audio(settings.VIDEOS_PATH + "audio2.mp3", target_language, 2)
        self.convert_to_srt(subtitle, settings.VIDEOS_PATH + "subtitle_" + target_language + ".srt" )
        self.__create_the_new_video(settings.VIDEOS_PATH + final_name, settings.VIDEOS_PATH + "audio2.mp3", settings.VIDEOS_PATH + "video_background.mp4")
    def __get_url_from_video(self) -> None:

        url = input("Please, type the video url: ");

        if(utils.is_url(url)):
             self.video_url = url
        else:
             print('the url is not valid');
    def __download_video(self) -> str:

        video_path = self.settings.VIDEOS_PATH

        if(self.video_url):

             video      = Download(video_path, self.video_url)
             video_path = video.dowload_YT()

             return video_path
    def __get_mp3_from_mp4(self, video_path: str) -> str:

        converter  = Converter(video_path);
        return converter.mp3_from_video(self.settings.VIDEOS_PATH)
    def __wait_upload(self):
        input("Press Enter to continue...")
        print("Continuing after Enter was pressed")

    def __get_text_from_long_audio(self, file_mp3: str, language, option=1) -> str:
        
        speechKey = self.settings.AZURE_SPEECH_SERVICE

        transcribe = Transcribe(speechKey, self.settings.REGION, self.settings.AZURE_STORAGE, self.settings.AZURE_CONTAINER, self.settings.AZURE_TRANSLATOR)
        return transcribe.transcribe_long(language, option)
    
    def __translate_long(self, transcribe_, target_language):
        transcribe = Transcribe(self.settings.AZURE_SPEECH_SERVICE, self.settings.REGION, self.settings.AZURE_STORAGE, self.settings.AZURE_CONTAINER, self.settings.AZURE_TRANSLATOR)
        return transcribe.translate_long(transcribe_, target_language)
    
    def __translated_to_speech(self, text: str, voice) -> None:

         azure_key = self.settings.AZURE_SPEECH_SERVICE
         region= self.settings.REGION

         speech  = Speech(azure_key, region)
         speech.text_to_mp3_long(text, voice, self.settings.VIDEOS_PATH)

video_translate = VideoTranslate(settings)
video_translate.translate_from_url('zh-CN', "zh-CN-XiaoxiaoNeural", "video-AR-SA.mp", 'zh', 1)