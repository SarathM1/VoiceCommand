import pyaudio
import wave
import os

# Import sometimes fails first time around because of a Cython issue.
try:
    import pocketsphinx
except ValueError:
    import pocketsphinx

# Paths
BASE_PATH = '/home/sm/Documents/scribe'
HMDIR = os.path.join(BASE_PATH, "hmm")
LMDIR = os.path.join(BASE_PATH, "lm/cmusphinx-5.0-en-us.lm.dmp")
DICTD = os.path.join(BASE_PATH, "dict/cmu07a.dic")

# Options
FORMAT = pyaudio.paInt16 # Should not be changed, as this format is best for speech recognition.
CHANNELS = 1
RATE = 16000 # Speech recognition only works well with this rate.  Don't change unless your microphone demands it.
CHUNK = 128 # The size of each audio chunk coming from the input device.
RECORD_SECONDS = 2 # Number of seconds to record, can be changed.
WAVE_OUTPUT_FILENAME = "record.wav" # Where to save the recording from the microphone.

def record_audio(wav_file):
    """
    Stream audio from an input device and save it.
    """
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        #input_device_index=device
    )

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
    print ('Best hypothesis: ', hypothesis.hypstr, " model score: ", hypothesis.best_score, " confidence: ", logmath.exp(hypothesis.prob))

    print ('Best hypothesis segments: ', [seg.word for seg in speech_rec.seg()])

    # Access N best decodings.

    print ('Best 10 hypothesis: ')
    for best, i in zip(speech_rec.nbest(), range(10)):
        print (best.hypstr, best.score)

# Run the thing!
if __name__ == '__main__':
    record_audio(WAVE_OUTPUT_FILENAME)
    result = recognize(WAVE_OUTPUT_FILENAME)