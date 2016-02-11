import pyaudio
import wave
import os

# Import sometimes fails first time around because of a Cython issue.
try:
    import pocketsphinx
except ValueError:
    import pocketsphinx

###############################################################################
"""
Error Handler to handle ALSA errors which can be ignored. To ignore, replace print 
statement with pass    
"""
from ctypes import *
import pyaudio

# Define our error handler type
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  #print 'messages are yummy'
  pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

asound = cdll.LoadLibrary('libasound.so')
# Set error handler
asound.snd_lib_error_set_handler(c_error_handler)
###############################################################################


# Paths
MODELDIR = "./model"

HMDIR = os.path.join(MODELDIR, 'en-us/en-us')
LMDIR = os.path.join(MODELDIR, 'en-us/en-us.lm.bin')
DICTD = os.path.join(MODELDIR, 'en-us/cmudict-en-us.dict')

# Options
FORMAT = pyaudio.paInt16 # Should not be changed, as this format is best for speech recognition.
CHANNELS = 1
RATE = 16000 # Speech recognition only works well with this rate.  Don't change unless your microphone demands it.
CHUNK = 128 # The size of each audio chunk coming from the input device.
RECORD_SECONDS = 5 # Number of seconds to record, can be changed.
WAVE_OUTPUT_FILENAME = "record.wav" # Where to save the recording from the microphone.

def record_audio(wav_file):
    """
    Stream audio from an input device and save it.

    To remove the following Error uninstall bluez-alsa:
        "bt_audio_service_open: connect() failed: Connection refused (111)"
    """
    
    p = pyaudio.PyAudio()
    
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()

    p.terminate()

    wf = wave.open(wav_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def recognize(wav_file):
    """
    Run speech recognition on a given file.
    """
    # Create a decoder with certain model
    config = pocketsphinx.Decoder.default_config()
    config.set_string('-hmm', HMDIR)
    config.set_string('-lm', LMDIR)
    config.set_string('-dict', DICTD)
    config.set_string('-logfn', '/dev/null')

    # Decode streaming data.
    speech_rec = pocketsphinx.Decoder(config)
    print "\nPronunciation for word 'hello' is ", speech_rec.lookup_word("hello")

    speech_rec.start_utt()
    stream = open(wav_file, 'rb')
    while True:
      buf = stream.read(1024)
      if buf:
        speech_rec.process_raw(buf, False, False)
      else:
        break
    speech_rec.end_utt()

    hypothesis = speech_rec.hyp()
    logmath = speech_rec.get_logmath()
    try:
        print '\nBEST HYPOTHESIS: ', hypothesis.hypstr,"\tMODEL SCORE: ", hypothesis.best_score,"\tCONFIDENCE: ", logmath.exp(hypothesis.prob)

        print '\nBEST HYPOTHESIS SEGMENTS: ', [seg.word for seg in speech_rec.seg()]

        # Access N best decodings.

        print ('\nBEST 10 HYPOTHESIS:\n')
        for best, i in zip(speech_rec.nbest(), range(10)):
            print '\t',"HYPOTHESIS: ",best.hypstr, "\tSCORE: ",best.score

    except AttributeError, e:
        print '\tError: ',e
        print '\t',"N.B: This error usually occurs when no sound is detected !!"

# Run the thing!
if __name__ == '__main__':
    record_audio(WAVE_OUTPUT_FILENAME)
    result = recognize(WAVE_OUTPUT_FILENAME)