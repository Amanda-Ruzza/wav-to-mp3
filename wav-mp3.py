import json
from os.path import getsize
import numpy as np #numpy makes the iterations through the audio samples 100x's faster than regular math/looping in Python
from pedalboard.io import AudioFile

wav_metadata = {}
mp3_metadata = {}
files_metadata = {
   'wav': wav_metadata,
   'mp3': mp3_metadata
}
# chunking the audio to process it in chunks, as a way to handle large files
chunk_size = 500_000

# Nesting infile(raw) and outfile(mp3-manipulated) context managers together
with AudioFile('4 MMM.wav') as f:
    # get wav metadata
    samplerate = f.samplerate
    channels = f.num_channels

    wav_metadata['filesize_in_mb'] = (lambda byte: round(byte/ (1024 ** 2), 2)) (getsize('4 MMM.wav')) # returns file size in bytes, and converts it into MB. 
    wav_metadata['sample_rate'] = f.samplerate
    wav_metadata['stereo'] = (lambda stereo: stereo == 2) (f.num_channels)
    wav_metadata['duration_in_minutes'] = (lambda sec: round(sec /60, 2)) (f.duration)
    wav_metadata['frames'] = f.frames 
    wav_metadata['bit_depth'] = f.file_dtype

    with AudioFile('4_MMM.mp3', 'w', samplerate=samplerate, num_channels=channels) as o:
       while f.tell() < f.frames: #as long as there's more audio coming in
          audio = f.read(chunk_size) # this will process the audio file in 4MB chunks of data
          o.write(audio)

# get mp3 metadata
with AudioFile('4_MMM.mp3') as o:
    mp3_metadata['filesize_in_mb'] = (lambda byte: round(byte/ (1024 ** 2), 2)) (getsize('4_MMM.mp3')) # returns file size in bytes, and converts it into MB. 
    mp3_metadata['sample_rate'] = o.samplerate
    mp3_metadata['stereo'] = (lambda stereo: stereo == 2) (o.num_channels)
    mp3_metadata['duration_in_minutes'] = (lambda sec: round(sec /60, 2)) (o.duration)
    mp3_metadata['frames'] = o.frames 
    mp3_metadata['bit_depth'] = o.file_dtype

# context manager to get the metadata
#TODO: create a variable, so I'm not hardcoding the file. Remember that this will be 'imported' from the GCP Bucket

with open('files-metadata.json', 'w') as f:
  json.dump(files_metadata, f)



# TODO: use the same method from the WAV to get the mp3 metadata  