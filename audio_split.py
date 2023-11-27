from pydub import AudioSegment
import os

def convert_to_milliseconds(time):
    hours, minutes, seconds = (["0", "0"] + time.split(":"))[-3:]
    hours = int(hours)
    minutes = int(minutes)
    seconds = float(seconds)
    return int(3600000 * hours + 60000 * minutes + 1000 * seconds)

timestamp_array = ["00:00:34" , "00:00:43", "00:00:57","00:01:06","00:01:28","00:01:31","00:02:05","00:02:14","00:02:17","00:02:27","00:02:29","00:02:38","00:03:41","00:03:50","00:04:04","00:04:13","00:04:48","00:04:57","00:05:00","00:05:09","00:05:44","00:05:53","00:05:55","00:06:03","00:07:10","00:07:18","00:07:56","00:08:04","00:08:47","00:08:55","00:09:30","00:09:39","00:09:41","00:09:49","00:10:24","00:10:33","00:11:11","00:11:19","00:11:54","00:12:03","00:13:18","00:13:27","00:14:26","00:14:33","00:15:19","00:15:27","00:16:13","00:16:21","00:17:08","00:17:16","00:18:00","00:18:09","00:18:46","00:18:54","00:19:31","00:19:40","00:20:26","00:20:34","00:20:37","00:20:46","00:21:12","00:21:22","00:21:58","00:22:06","00:22:41","00:22:49","00:23:32","00:23:41","00:24:16","00:24:25","00:25:01","00:25:09","00:25:44","00:25:53","00:26:20","00:26:28","00:27:05","00:27:14","00:27:50","00:27:58","00:28:37","00:28:45","00:29:21","00:29:29","00:29:54","00:30:02","00:30:51","00:31:00","00:31:38","00:31:46","00:32:22","00:32:29","00:33:08","00:33:16","00:33:51","00:34:00","00:34:43","00:34:52","00:35:37","00:35:45","00:36:20","00:36:29","00:37:06","00:37:14","00:37:49","00:37:58","00:38:32","00:38:41"]
split_times = []
for i in timestamp_array:
    split_times.append(convert_to_milliseconds(i))

audio = AudioSegment.from_file("./Recording.mp3", format="mp3")
start_time = 0

for i, split_time in enumerate(split_times):
    segment = audio[start_time:split_time]
    if i % 2 == 0:
        segment_name = "off_segment_{}.mp3".format(i+1)
    else:
        segment_name = "on_segment_{}.mp3".format(i+1)
    segment.export(segment_name, format="mp3")
    start_time = split_time

segment = audio[start_time:]
segment.export("off_segment_{}.mp3".format(len(split_times)), format="mp3")

audio_files_directory = os.getcwd()
pattern_on = 'on_'
pattern_off = 'off_'

combined_audio_on = AudioSegment.silent(duration=0)
combined_audio_off = AudioSegment.silent(duration=0)

for filename in os.listdir(audio_files_directory):
    if filename.startswith(pattern_on):
        audio = AudioSegment.from_file(os.path.join(audio_files_directory, filename))
        combined_audio_on += audio
    elif filename.startswith(pattern_off):
        audio = AudioSegment.from_file(os.path.join(audio_files_directory, filename))
        combined_audio_off += audio

combined_audio_on.export('combined_audio_on.mp3', format='mp3')
combined_audio_off.export('combined_audio_off.mp3', format='mp3')


def split_into_one_second_clips(audio_file_path, output_directory):
    audio = AudioSegment.from_file(audio_file_path, format="mp3")
    clip_duration = 1000
    os.makedirs(output_directory, exist_ok=True)
    for i in range(0, len(audio), clip_duration):
        clip = audio[i:i + clip_duration]
        clip.export(os.path.join(output_directory, f"clip_{i//clip_duration}.mp3"), format="mp3")

split_into_one_second_clips('combined_audio_on.mp3', "on")
split_into_one_second_clips('combined_audio_off.mp3', "off")
