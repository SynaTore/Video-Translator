from gtts import gTTS
from moviepy import *


class Converter:

    def __init__(self,  file: any) -> None:
        self.file = file
    

    def mp3_from_video(self, path):

        videoFile = VideoFileClip(self.file)
        videoFile.audio.write_audiofile(path + 'audio1.mp3')

        return path + 'audio1.mp3'

    def text_to_audio(self, text: str):

        textToSpeech = gTTS(text=text, tld='com.br', lang='pt');
        textToSpeech.save('audio.mp3');

        return 'audio.mp3'


    def change_audio_from_video(self, audioPath: str, finale_name):

        audioFile =  AudioFileClip(audioPath)

        videoFile =  VideoFileClip(self.file).set_audio(audioFile)
        videoFile.write_videofile(finale_name, videoFile.fps)