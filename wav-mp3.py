import json
import logging
from glob import glob 
from os import getcwd
from os.path import getsize, join, splitext, __file__
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

def convert_wav_mp3(logger):
   logger.info('Input Directory Path is: %s', getcwd())
   wav_file = glob(join(getcwd(), '*.wav'))
   logger.info('Input .WAV file name is: %s', wav_file)

   if wav_file:
      input_wav_filename = wav_file[0].split('/')[-1] # extract file name from the path
      clean_input_wav_filename = input_wav_filename.replace(' ', '_')
      input_wav_path = join(getcwd(), clean_input_wav_filename)
      logger.info('Clean Input .WAV Path: %s', input_wav_path)

      output_mp3_filename = splitext(clean_input_wav_filename)[0] + '.mp3'
      output_mp3_path = join(getcwd(), output_mp3_filename)

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

      with open('files-metadata.json', 'w') as f:
         json.dump(files_metadata, f)
         logger.info('.WAV + .MP3 File Metadata Information: %s', glob(join(getcwd(), '*.json')))

   else:
      logger.error('No .wav audio files found in the current directory.')

logger = logging.getLogger(__name__)
convert_wav_mp3(logger)