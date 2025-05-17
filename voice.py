import os
import tempfile
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from dotenv import load_dotenv
from groq import Groq
import io
import base64

# Load environment variables
load_dotenv()


class VoiceSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def listen(self):
        """Capture audio from microphone and convert to text"""
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

            try:
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except sr.UnknownValueError:
                return "Could not understand audio"
            except sr.RequestError as e:
                return f"Error with speech recognition service: {e}"

    def speak(self, text):
        """Convert text to speech and play it"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
                tts = gTTS(text=text, lang='en')
                tts.save(fp.name)
                fp.close()
                playsound(fp.name)
                os.unlink(fp.name)  # Delete the temporary file
        except Exception as e:
            print(f"Error in text-to-speech: {e}")

    def voice_chat(self, prompt):
        """Handle voice conversation with Groq API"""
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in voice chat: {str(e)}"


def get_voice_system():
    """Factory function to get voice system instance"""
    return VoiceSystem()

