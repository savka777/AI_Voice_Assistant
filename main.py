import sys
import speech_recognition as sr
from gtts import gTTS
import playsound
import os
import openai
import elevenlabs

recognizer = sr.Recognizer()
# Using an environment variable to access API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
elevenlabs.set_api_key(ELEVENLABS_API_KEY)

if not openai.api_key:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")


# Issue a prompt to the GPT to create Agent
# Define a default role for the agent if not specified
default_role = "You are a general-purpose assistant"
current_role = default_role

# Allow the user to set the role
def set_agent_role():
    global current_role
    print("Please describe the role for your GPT agent: ")
    role_description = input()
    current_role = role_description  # if role_description else default_role
    speak("I will be glad to help you with that.")


# Generate audio from Elevenlabs
# Generate audio from Elevenlabs
def speak(text):
    audio = elevenlabs.generate(
        text=text,
        voice="Natasha - Valley girl"
    )
    elevenlabs.save(audio, "response.mp3")
    elevenlabs.play(audio)
    os.remove("response.mp3")


# Generate audio from text (google text-to-speach API)
# def speak(text):
#     tts = gTTS(text=text, lang='en')
#     tts.save("response.mp3")
#     playsound.playsound("response.mp3")
#     os.remove("response.mp3")


def process_command(text):
    # Prepend the role of agent to text
    full_prompt = "{}\n\n{}".format(current_role, text)

    # Send the text to OpenAI's API
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",  # Choose the appropriate model
            prompt=full_prompt,
            max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"An error occurred: {e}"


run_once = True


def run_once_agent_role():
    global run_once
    if not run_once:
        return
    run_once = False
    set_agent_role()


# Running the voice assistant
while True:
    run_once_agent_role()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print("You said: " + text)

            # Check if the user said 'ok goodbye' to exit the program
            if 'ok goodbye' in text.lower():
                print('program exiting...')
                speak("Thank you, goodbye.")
                break

            response = process_command(text)
            speak(response)

        except sr.UnknownValueError:
            speak("I didn't get that, could you please repeat?")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            speak("I'm having trouble connecting to the server.")

sys.exit()
