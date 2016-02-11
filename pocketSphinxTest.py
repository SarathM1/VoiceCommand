
from os import environ, path


from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *


BASE_PATH = './'
HMDIR = path.join(BASE_PATH, "hmm")
LMDIR = path.join(BASE_PATH, "lm/cmusphinx-5.0-en-us.lm.dmp")
DICTD = path.join(BASE_PATH, "dict/cmu07a.dic")

# Create a decoder with certain model
config = Decoder.default_config()
config.set_string('-hmm', HMDIR)
config.set_string('-lm', LMDIR)
config.set_string('-dict', DICTD)
config.set_string('-logfn', '/dev/null')

# Decode streaming data.
decoder = Decoder(config)
"""
print ("Pronunciation for word 'hello' is ", decoder.lookup_word("hello"))
print ("Pronunciation for word 'abcdf' is ", decoder.lookup_word("abcdf"))
"""
decoder.start_utt()
stream = open('cards2.wav', 'rb')
while True:
  buf = stream.read(1024)
  if buf:
    decoder.process_raw(buf, False, False)
  else:
    break
decoder.end_utt()

hypothesis = decoder.hyp()
logmath = decoder.get_logmath()
print ('Best hypothesis: ', hypothesis.hypstr, " model score: ", hypothesis.best_score, " confidence: ", logmath.exp(hypothesis.prob))

print ('Best hypothesis segments: ', [seg.word for seg in decoder.seg()])

# Access N best decodings.

print ('Best 10 hypothesis: ')
for best, i in zip(decoder.nbest(), range(10)):
    print (best.hypstr, best.score)
