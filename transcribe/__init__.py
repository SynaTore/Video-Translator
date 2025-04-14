import requests;
import time;

class Transcribe:

    def __init__(self, api_key: str, service_region: str, storage_acc_name: str, container_name: str, azure_translator: str) -> None:

        self.api_key = api_key;
        self.upload_endpoint     = 'https://api.assemblyai.com/v2/upload'
        self.transcribe_endpoint = 'https://api.assemblyai.com/v2/transcript'
        self.polling_endpoint    = 'https://api.assemblyai.com/v2/transcript/'
        self.azure_api_url = f"https://{service_region}.api.cognitive.microsoft.com/speechtotext/v3.1/transcriptions"
        self.azure_api_container_url = f"https://{storage_acc_name}.blob.core.windows.net/{container_name}/audio1.mp3"
        self.azure_api_container_url2 = f"https://{storage_acc_name}.blob.core.windows.net/{container_name}/audio2.mp3"
        self.azure_translator = azure_translator
        self.region = service_region

        self.headers = self.__headers_for_request()
        self.azure_headers = self.__azure_headers_for_request()

    def transcribe(self, audio_file: str):

        audio_uplod = self.__upload_audio(audio_file);

        transcribe  = self.__request_transcribe(audio_uplod)

        self.__wait_for_completion(transcribe);

        return self.__get_text(transcribe);

    def transcribe_long(self, language: str, option):

        if (option == 1) :

            # audio_uplod = self.__upload_audio(audio_file);

            transcribe_url  = self.__request_transcribe_long(language, option)

            self.__wait_for_completion_long(transcribe_url[0]);

            return self.__get_text_long(transcribe_url[1]);

        # else :
        #     transcribe_url  = self.__request_transcribe_long(language, option)

        #     self.__wait_for_completion_long(transcribe_url[0]);

        #     return self.__get_subtitle(transcribe_url[1]);

    def translate_long(self, transcribe, target_language):
        header = {
          'Ocp-Apim-Subscription-Key': self.azure_translator,
          'Ocp-Apim-Subscription-Region': self.region,
          "Content-Type": "application/json"
        }
        
        url = f'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={target_language}&from=en'
        
        ppayload = [{"Text": transcribe}]
        
        res = requests.post(url, headers=header, json=ppayload);

        if (res.status_code != 200):
            print ("Error in the translation")
            exit (0)
        else :
            print ("translation done")
        return (res.json()[0]['translations'][0]['text'])

    def __upload_audio(self, audio_file):

       
       
        header_for_request = self.__headers_for_request()
        upload_request = requests.post(url=self.upload_endpoint, 
                                       headers= header_for_request,
                                       data= self.__read_file(audio_file));

        return upload_request.json();



    def __request_transcribe(self, upload: any):
        
        headers_for_request = self.__headers_for_request();
        
        transcript_request  = {
            'audio_url': upload['upload_url']
        }

        transcript_response = requests.post(url=self.transcribe_endpoint,
                                            json=transcript_request,
                                            headers=headers_for_request);
        return transcript_response.json();
    
    def __request_transcribe_long(self, language: str, option):
        if option == 1 :
            data = {
                "contentUrls": [
                    self.azure_api_container_url
                ],
                "locale": language,
                "displayName": "My Transcription",
                "model": None
            }
        else :
            data = {
                "contentUrls": [
                    self.azure_api_container_url2
                ],
                # "wordLevelTimestampsEnabled": "true",
                # "contentContainerUrl": self.azure_api_container_url2,
                "locale": language,
                "displayName": "My Transcription",
                "model": None
            }

        response = requests.post(f"https://{self.region}.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions", headers=self.azure_headers, json=data)
        if response.status_code == 201:
            print("Transcription request was successful.")
            api_url = (response.json()['self'], response.json()['links']['files'])
        else:
            print("Transcription request failed with status code:", response.json())
            exit (0)
        return api_url

    def __get_text(self, trascript_response: any):

        polling_endpoint    = self.__get_polling_endpoint(trascript_response);
        headers_for_request = self.__headers_for_request();

        paragraphs_response = requests.get(polling_endpoint + "/paragraphs", headers=headers_for_request)
        paragraphs_response = paragraphs_response.json()

        paragraphs = []

        for para in paragraphs_response['paragraphs']:
            paragraphs.append(para)

        return paragraphs[0]['text']

    def __get_subtitle(self, api_url: str):
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }

        response = requests.get(api_url, headers=headers)

        # # Check the response status
        if response.status_code == 200:
            print("GET request was successful.")
            contentUrl = response.json()['values'][0]['links']['contentUrl']
        else:
            print("GET request failed with status code:", response.status_code)
            exit (0)

        content = requests.get(contentUrl)
        return (content.json()['recognizedPhrases'])     

    def __get_text_long(self, api_url: str):
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }

        response = requests.get(api_url, headers=headers)

        # # Check the response status
        if response.status_code == 200:
            print("GET request was successful.")
            print (response.json())
            contentUrl = response.json()['values'][0]['links']['contentUrl']
        else:
            print("GET request failed with status code:", response.status_code)
            exit (0)

        content = requests.get(contentUrl)
    
        return (content.json()['combinedRecognizedPhrases'][0]['display'])

    def __read_file(self, filename: str, chunk_size=5242880):

        
        with open(filename, "rb") as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data



    def __headers_for_request(self):

        return {
               "authorization": self.api_key,
               "content-type": "application/json"
        }
    
    def __azure_headers_for_request(self):

        return {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def __wait_for_completion(self, transcription_response: any):
        
        polling_endpoint = self.__get_polling_endpoint(transcription_response)
        headers_for_request = self.__headers_for_request()

        while True:
            polling_response = requests.get(polling_endpoint, headers=headers_for_request)
            polling_response = polling_response.json()

            if polling_response['status'] == 'completed':
                break

            time.sleep(5)

    def __wait_for_completion_long(self, api_url: str):
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }

        response = requests.get(api_url, headers=headers)
        while (response.json()['status'] != 'Succeeded') :
            time.sleep(5)
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                print("Check status request successful")
                print("Response JSON:", response.json()['status'])
            else:
                print("Check status request faild", response)
                exit (0)
            if (response.json()['status'] == 'Failed'):
                print (response.json())
                exit (0)



    def __get_polling_endpoint(self, transcript_response: any):

          polling_endpoint  =  self.polling_endpoint
          polling_endpoint +=  transcript_response['id']

          return polling_endpoint