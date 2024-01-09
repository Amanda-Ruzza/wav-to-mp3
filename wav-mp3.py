import json
import logging
from os import getcwd
from os.path import getsize, join, abspath, splitext, dirname, __file__
# import numpy as np #numpy makes the iterations through the audio samples 100x's faster than regular math/looping in Python
from pedalboard.io import AudioFile

logging.basicConfig(
   level=logging.INFO,
   format='%(asctime)s - %(levelname)s - %(message)s',
   handlers=[
       logging.FileHandler('wav-mp3.log'),
       logging.StreamHandler()
   ]
)

# get script directory location 
script_dir = dirname(abspath(__file__)) # replace this with the GCP Storage Bucket URL
logging.info('Script Directory Path: %s', script_dir)
# construct input path
input_wav_filename = '4 MMM.wav'
input_wav_path = join(script_dir, input_wav_filename)

# clean possible spaces in the WAV file name
# if ' ' in input_wav_filename:
clean_input_wav_filename = input_wav_filename.replace(' ', '_')
# else:
#    clean_wav_name = input_wav_filename
input_wav_path = join(script_dir, clean_input_wav_filename)

logging.info('Clean Input WAV Path: %s', input_wav_path)
# add .WAV extension back to the clean name
# clean_wav_name, _ = splitext(clean_wav_name)

# join original path with the cleaned file name
# clean_input_wav_path = abspath(join(script_dir, clean_wav_name + '.wav'))
# logging.info('Clean Input WAV Path: %s', clean_input_wav_path)

output_mp3_filename = splitext(clean_input_wav_filename)[0] + '.mp3'
output_mp3_path = join(script_dir, output_mp3_filename)

wav_metadata = {}
mp3_metadata = {}
files_metadata = {
   'wav': wav_metadata,
   'mp3': mp3_metadata
}
# chunking the audio to process it in chunks, as a way to handle large files
chunk_size = 500_000

# Nesting infile(raw) and outfile(mp3-manipulated) context managers together
with AudioFile(input_wav_filename) as f:
    # get wav metadata
    samplerate = f.samplerate
    channels = f.num_channels

    wav_metadata['filesize_in_mb'] = (lambda byte: round(byte/ (1024 ** 2), 2)) (getsize('4 MMM.wav')) # returns file size in bytes, and converts it into MB. 
    wav_metadata['sample_rate'] = f.samplerate
    wav_metadata['stereo'] = (lambda stereo: stereo == 2) (f.num_channels)
    wav_metadata['duration_in_minutes'] = (lambda sec: round(sec /60, 2)) (f.duration)
    wav_metadata['frames'] = f.frames 
    wav_metadata['bit_depth'] = f.file_dtype

    with AudioFile(output_mp3_filename, 'w', samplerate=samplerate, num_channels=channels) as o:
       while f.tell() < f.frames: #as long as there's more audio coming in
          audio = f.read(chunk_size) # this will process the audio file in 4MB chunks of data
          o.write(audio)

# get mp3 metadata
with AudioFile(output_mp3_filename) as o:
    mp3_metadata['filesize_in_mb'] = (lambda byte: round(byte/ (1024 ** 2), 2)) (getsize('4_MMM.mp3')) # returns file size in bytes, and converts it into MB. 
    mp3_metadata['sample_rate'] = o.samplerate
    mp3_metadata['stereo'] = (lambda stereo: stereo == 2) (o.num_channels)
    mp3_metadata['duration_in_minutes'] = (lambda sec: round(sec /60, 2)) (o.duration)
    mp3_metadata['frames'] = o.frames 
    mp3_metadata['bit_depth'] = o.file_dtype

#TODO: create a variable, so I'm not hardcoding the file. Remember that this will be 'imported' from the GCP Bucket

with open('files-metadata.json', 'w') as f:
  json.dump(files_metadata, f)
 