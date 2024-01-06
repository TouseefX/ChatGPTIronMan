import platform
import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
import requests
import openai
import cv2
from pyzbar import pyzbar
from google.cloud import vision
from bs4 import BeautifulSoup
from pytube import YouTube
import os

# Set up OpenAI and Google Cloud Vision API credentials
openai.api_key = "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"
vision_client = vision.ImageAnnotatorClient.from_service_account_json('ornate-bebop-396517-3927990b0f16.json')

# Initialize the speech recognition and text-to-speech engines
r = sr.Recognizer()
engine = pyttsx3.init()

# Function to convert text to speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen for user input from microphone
def get_user_input_from_microphone():
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            user_input = r.recognize_google(audio)
            print("You said: " + user_input)
            return user_input
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Could you please repeat?")
            return get_user_input_from_microphone()

# Function to get user input from text
def get_user_input_from_text():
    user_input = input("Enter your message: ")
    return user_input

# Function to interact with ChatGPT
def chat_with_gpt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Function to open a web browser
def open_browser():
    if platform.system() == "Darwin":  # macOS
        subprocess.call(("open", "-a", "Safari"))
    elif platform.system() == "Windows":
        subprocess.Popen("C:\ProgramFiles\Google\Chrome\Application\chrome.exe")
    else:
        speak("Sorry, this feature is not supported on your operating system.")

# Function to search websites
def search_websites(query):
    query = query.replace("search", "").strip()
    url = "https://www.google.com/search?q=" + query
    webbrowser.open(url)

# Function to search on Google
def search_google(query):
    query = query.replace("google", "").strip()
    url = "https://www.google.com/search?q=" + query
    webbrowser.open(url)

# Function to search on YouTube
def search_youtube(query):
    query = query.replace("search youtube", "").strip()
    url = "https://www.youtube.com/results?search_query=" + query
    webbrowser.open(url)

# Function to play music from YouTube using PyTube
def play_music(url):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(output_path="temp/")
        file_path = "temp/" + audio_stream.default_filename
        os.system("start " + file_path)
        speak("Playing music.")
    except Exception as e:
        speak("Sorry, I couldn't play the music. Please try again.")

# Function to scan QR codes
def scan_qr_code():
    speak("Please provide the image URL or path.")
    user_input = get_user_input_from_text()
    try:
        response = requests.get(user_input)
        file_path = "image.jpg"
        file = open(file_path, "wb")
        file.write(response.content)
        file.close()
        speak("Scanning QR code.")
        image = cv2.imread(file_path)
        barcodes = pyzbar.decode(image)
        if len(barcodes) > 0:
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                speak("QR code contains: " + barcode_data)
        else:
            speak("Sorry, no QR code found.")
    except Exception as e:
        speak("Sorry, I couldn't scan the QR code. Please try again.")

# Function to enhance image quality
def enhance_image_quality(image_path):
    image = cv2.imread(image_path)
    enhanced_image = cv2.detailEnhance(image, sigma_s=10, sigma_r=0.15)
    cv2.imwrite("enhanced_image.jpg", enhanced_image)
    cv2.imshow("Original Image", image)
    cv2.imshow("Enhanced Image", enhanced_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Function to perform image recognition using Google Cloud Vision API (Google Lens)
def perform_image_recognition(image_path):
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = visionImage(content=content)
    response = vision_client.label_detection(image=image)
    labels = response.label_annotations

    if labels:
        speak("Google Lens found the following labels:")
        for label in labels:
            speak(label.description)
    else:
        speak("Sorry, Google Lens could not identify any labels in the image.")

# Function to retrieve movie information from HDHub4u.tv
def get_movie_info(movie_name):
    search_url = f"https://hdhub4u.tv/?s={movie_name.replace(' ', '+')}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the first movie result
    movie_link = soup.find('a', {'rel': 'bookmark'})['href']
    
    # Open the movie link in a web browser
    webbrowser.open(movie_link)

# Main program loop
while True:
    user_input = get_user_input_from_microphone()
    
    if "open browser" in user_input:
        speak("Opening web browser.")
        open_browser()
    elif "search" in user_input:
        search_websites(user_input)
    elif "google" in user_input:
        search_google(user_input)
    elif "search youtube" in user_input:
        search_youtube(user_input)
    elif "play music" in user_input:
        speak("Please provide the YouTube URL.")
        url = get_user_input_from_text()
        play_music(url)
    elif "scan QR code" in user_input:
        scan_qr_code()
    elif "enhance image" in user_input:
        speak("Please provide the image URL or path.")
        image_path = get_user_input_from_text()
        enhance_image_quality(image_path)
    elif "image recognition" in user_input:
        speak("Please provide the image URL or path.")
        image_path = get_user_input_from_text()
        perform_image_recognition(image_path)
    elif "get movie info" in user_input:
        speak("Please provide the movie name.")
        movie_name = get_user_input_from_text()
        get_movie_info(movie_name)
    elif "quit" in user_input:
        speak("Goodbye!")
        break
    else:
        prompt = user_input
        response = chat_with_gpt(prompt)
        speak(response)