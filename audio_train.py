import librosa
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment

def extract_mfcc(file_path, n_mfcc=20):
    audio, sample_rate = librosa.load(file_path, sr=None)
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=n_mfcc)
    return mfccs.mean(axis=1)

def load_data_from_folder(folder_path, label):
    features = []
    labels = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.mp3'):
            mfccs = extract_mfcc(os.path.join(folder_path, filename))
            features.append(mfccs)
            labels.append(label)
    return features, labels

path_on = 'on'
path_off = 'off'

features_on, labels_on = load_data_from_folder(path_on, 1)
features_off, labels_off = load_data_from_folder(path_off, 0)

X = np.array(features_on + features_off)
y = np.array(labels_on + labels_off)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)


def predict_folder_accuracy(folder_path, label):
    features, labels = load_data_from_folder(folder_path, label)
    predictions = clf.predict(features)
    accuracy = accuracy_score(labels, predictions)
    print(f"Accuracy for {folder_path}: {accuracy}")

# predict_folder_accuracy(path_on, 1)
# predict_folder_accuracy(path_off, 0)

def process_video(video_path, model, extract_mfcc, output_path):
    video_clip = VideoFileClip(video_path)
    audio_path = "temp_audio.wav"
    video_clip.audio.write_audiofile(audio_path)

    audio = AudioSegment.from_file(audio_path)
    predictions = []
    for i in range(0, len(audio), 1000):  
        clip = audio[i:i + 1000]
        clip.export("temp_clip.wav", format="wav")
        mfccs = extract_mfcc("temp_clip.wav")
        mfccs_reshaped = mfccs.reshape(1, -1)
        prediction = model.predict(mfccs_reshaped)[0]
        predictions.append(prediction)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    current_frame = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_second = int(current_frame // fps)
        if current_second < len(predictions):
            label = predictions[current_second]
            classname = "On" if label == 1 else "Off"
            color = (0, 255, 0) if label == 1 else (255, 0, 0)
            cv2.putText(frame, f'Class: {classname}', (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 3, color, 2)
        print("Progress:", current_frame / frame_count * 100, "%")
        out.write(frame)
        current_frame += 1

    cap.release()
    out.release()

    original_audio = AudioFileClip(audio_path)
    annotated_video = VideoFileClip(output_path, audio=False)
    final_video = annotated_video.set_audio(original_audio)
    final_video.write_videofile(output_path.replace(".mp4", "_with_audio.mp4"), codec="libx264", audio_codec="aac")



    # Clean up temporary files
    os.remove(audio_path)
    os.remove("temp_clip.wav")

process_video("video_small.mp4", clf, extract_mfcc, "annotated_video.mp4")