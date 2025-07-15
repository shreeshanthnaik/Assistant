import os
import json
import requests
import datetime
import wikipedia
import platform

# === 🔑 CONFIG ===
WEATHER_API_KEY = "your_openweathermap_api_key"
GEMINI_API_KEY = "your_gemini_api_key"
LAB_PATH = os.path.expanduser("~/Assistant-lab")
CONFIG_PATH = os.path.expanduser("~/.Assistant-cli")
USER_FILE = os.path.join(CONFIG_PATH, "user.json")

# === 📁 Setup ===
os.makedirs(LAB_PATH, exist_ok=True)
os.makedirs(CONFIG_PATH, exist_ok=True)

# === 💬 Speak + Print ===
def speak(msg):
    assistant = get_assistant_name()
    print(f"🤖 {assistant}: {msg}", flush=True)
    try:
        if platform.system() == "Windows":
            import subprocess
            subprocess.run([
                "powershell", "-Command",
                f'Add-Type -AssemblyName System.Speech; '
                f'$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                f'$synth.Speak("{msg}")'
            ], capture_output=True, text=True)
        else:
            os.system(f'espeak "{msg}" 2>/dev/null')
    except:
        pass

# === 🎙 Input
def takeCommand():
    return input("👤 You: ").strip().lower()

# === 👤 User Config
def get_user():
    if os.path.exists(USER_FILE):
        with open(USER_FILE) as f:
            return json.load(f)["name"]
    name = input("👤 What's your name, friend? ").strip()
    assistant = input("🛠️ What would you like to call me? (Give me a cute name!): ").strip()
    with open(USER_FILE, "w") as f:
        json.dump({"name": name, "assistant": assistant}, f)
    speak(f"Hello {name}! It's nice to meet you. I'm {assistant}, your little helper! 💫")
    return name

def get_assistant_name():
    if os.path.exists(USER_FILE):
        with open(USER_FILE) as f:
            return json.load(f).get("assistant", "Buddy")
    return "Buddy"

# === 🌦 Weather
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("main"):
            temp = res["main"]["temp"]
            desc = res["weather"][0]["description"]
            speak(f"{city.capitalize()} is {desc}, {temp}°C. Don’t forget your jacket if you're heading out! 🧥")
        else:
            speak("Hmm... I couldn’t find that city. Want to try another one?")
    except:
        speak("Oops! I had trouble checking the weather. Maybe try again in a bit?")

# === 📚 Wikipedia
def wiki_info(topic):
    try:
        result = wikipedia.summary(topic, sentences=2)
        speak(result)
    except:
        speak("I looked around, but couldn’t find much on that. Got another topic?")

# === 🌐 Gemini AI
def ask_gemini(prompt):
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        speak(response.text)
    except Exception:
        speak("Uh-oh! I couldn’t connect to Gemini. Make sure it's installed and the API key is valid!")

# === 💾 Notes
def save_note(msg):
    with open(os.path.join(LAB_PATH, "notes.txt"), "a") as f:
        f.write(f"{datetime.datetime.now()}: {msg}\n")
    speak("Got it! I saved your note. 📝")

def show_notes():
    path = os.path.join(LAB_PATH, "notes.txt")
    if os.path.exists(path):
        speak("Here are your notes:")
        with open(path) as f:
            print(f.read())
    else:
        speak("Hmm... no notes yet. You can start one with 'note <text>'")

# === 📰 Hacker News
def get_news():
    try:
        r = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        ids = r.json()[:5]
        speak("Here are some top tech stories today:")
        for i in ids:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{i}.json").json()
            print("📰", item.get("title", "No title"))
    except:
        speak("Couldn’t fetch the news right now. Internet gremlins maybe? 🐛")

# === 📜 Help
def show_help():
    print(f"""
🛠️ {get_assistant_name()}'s Command List:
  weather <city>         - Get the weather report
  wikipedia <topic>      - Quick summary from Wikipedia
  ai <question>          - Ask me anything!
  news                   - Latest tech news
  note <text>            - Jot down a quick note
  show notes             - Show your notes
  whoami                 - Remind me who you are
  help                   - Show this list again
  exit / quit / bye      - Say goodbye 😢
""")

# === 🎬 MAIN LOOP
if __name__ == "__main__":
    name = get_user()
    speak(f"Hey {name}, great to see you again! What can I do for you today? 😊")

    while True:
        cmd = takeCommand()

        if cmd.startswith("weather"):
            get_weather(cmd.replace("weather", "").strip())

        elif cmd.startswith("wikipedia"):
            wiki_info(cmd.replace("wikipedia", "").strip())

        elif cmd.startswith("ai "):
            ask_gemini(cmd.replace("ai", "").strip())

        elif cmd == "news":
            get_news()

        elif cmd.startswith("note "):
            save_note(cmd.replace("note", "").strip())

        elif cmd == "show notes":
            show_notes()

        elif cmd == "whoami":
            speak(f"You’re my buddy, {name} 💖")

        elif cmd == "help":
            show_help()

        elif cmd in ["exit", "quit", "bye"]:
            speak("Aww, you're leaving? Okay, talk to you soon! 👋")
            break

        else:
            speak("Hmm, I didn’t get that. Try saying 'help' to see what I can do!")
