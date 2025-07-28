import json
import librosa

filename = r"C:\Users\lenovo\Desktop\hezhe.mp3"
y, sr = librosa.load(filename)

onset_env = librosa.onset.onset_strength(y=y, sr=sr)

onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)

onset_times = librosa.frames_to_time(onsets, sr=sr)

print("Onsets detected at: ", onset_times)

data = {"filename": filename, "onset_times": onset_times.tolist()}

try:
    with open("chuli.json", "r") as f:
        existing_data = json.load(f)
except FileNotFoundError:
    existing_data = []

existing_data.append(data)

with open("chuli.json", "w") as f:
    json.dump(existing_data, f)