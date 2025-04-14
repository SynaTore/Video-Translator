# import azure.cognitiveservices.speech as speechsdk
# from pydub import AudioSegment
import requests
import time
import zipfile
import shutil
import ffmpeg
import secrets


class Speech:

    def __init__(self, azure_key: str, region: str) -> None:
        self.azure_key = azure_key
        self.region = region

    # def text_to_mp3(self, text: str, voice, path):

    #     speech_config = speechsdk.SpeechConfig(subscription=self.azure_key, region=self.region);
    #     speech_config.speech_synthesis_voice_name = voice

    #     speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

    #     filename = path + 'audio2.mp3'

    #     audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
    #     synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    #     audio = synthesizer.speak_text_async(text).get()

    #     if audio.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    #         print("Speech synthesized  audio was saved to [{}]".format(filename))
    #     elif audio.reason == speechsdk.ResultReason.Canceled:
    #         cancellation_details = audio.cancellation_details
    #         print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    #         if cancellation_details.reason == speechsdk.CancellationReason.Error:
    #             print("Error details: {}".format(cancellation_details.error_details))

    def text_to_mp3_long(self, text: str, voice, path):

        key = secrets.token_hex(20)
        url = f"https://{self.region}.api.cognitive.microsoft.com/texttospeech/batchsyntheses/{key}?api-version=2024-04-01"

        headers = {
            "Ocp-Apim-Subscription-Key": self.azure_key,
            "Content-Type": "application/json",
        }

        # payload = {
        #     "displayName": "batch synthesis sample",
        #     "description": "my plain text test",
        #     "textType": "PlainText",
        #     "inputs": [
        #         {
        #             "text": text
        #         },
        #     ],
        #     "properties": {
        #         "outputFormat": "riff-24khz-16bit-mono-pcm",
        #         "wordBoundaryEnabled": False,
        #         "sentenceBoundaryEnabled": False,
        #         "concatenateResult": False,
        #         "decompressOutputFiles": False,
        #     },
        #     "synthesisConfig": {
        #         "Voice": voice
        #     }
        # }
        payload = {
            "description": "my test",
            "inputKind": "PlainText",
            "inputs": [
                {
                    "content": text
                }
            ],
            "properties": {
                "outputFormat": "riff-24khz-16bit-mono-pcm",
                "wordBoundaryEnabled": False,
                "sentenceBoundaryEnabled": False,
                "concatenateResult": False,
                "decompressOutputFiles": False,
            },
            "synthesisConfig": {"Voice": voice},
        }

        response = requests.put(url, headers=headers, json=payload)

        if response.status_code == 201:
            print("Request successful. Response:")
            id = response.json().get("id", "not found")
            print(id)
        else:
            id = "not found"
            print(f"Request failed with status code {response.status_code}. Response:")
            print(response.text)
            exit(0)

        if id == "not found":
            print("No id found")
            exit(0)
        print(id)

        # url = f"https://{self.region}.customvoice.api.speech.microsoft.com/api/texttospeech/3.1-preview1/batchsynthesis/{id}"
        url = f"https://{self.region}.api.cognitive.microsoft.com/texttospeech/batchsyntheses/{key}?api-version=2024-04-01"
        response = requests.get(url, headers=headers)
        print (response.json())
        while response.json()["status"] != "Succeeded":
            print(response.json()["status"])
            time.sleep(5)
            response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("checking on the request {id} failed")

        zip_url = response.json()["outputs"]["result"]

        local_zip_filename = path + "file.zip"

        extracted_dir = path + "extracted_data"

        response = requests.get(zip_url)

        if response.status_code == 200:
            with open(local_zip_filename, "wb") as f:
                f.write(response.content)

            with zipfile.ZipFile(local_zip_filename, "r") as zip_ref:
                zip_ref.extractall(extracted_dir)

            print(f"Downloaded and extracted {local_zip_filename} to {extracted_dir}")
        else:
            print(
                f"Failed to download the zip file. Status code: {response.status_code}"
            )

        source_file = extracted_dir + "/0001.wav"
        destination_file = path + "audio2.mp3"
        ffmpeg.input(source_file).output(destination_file, format="mp3").run()
        # wav_file = AudioSegment.from_file(source_file, format="wav")
        # mp3_file = wav_file.export(destination_file, format="mp3")
        # mp3_file.close()

        # shutil.move(source_file, destination_file)

        print("DONE!")
