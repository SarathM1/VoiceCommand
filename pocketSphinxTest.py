
from os import environ, path
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *


MODELDIR = "./model"

HMDIR = path.join(MODELDIR, 'en-us/en-us')
LMDIR = path.join(MODELDIR, 'en-us/en-us.lm.bin')
DICTD = path.join(MODELDIR, 'en-us/cmudict-en-us.dict')

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
stream = open('hello.wav', 'rb')

while True:
  buf = stream.read(1024)
  if buf:
    decoder.process_raw(buf, False, False)
  else:
    break
decoder.end_utt()

hypothesis = decoder.hyp()
logmath = decoder.get_logmath()

try:
    print '\nBEST HYPOTHESIS: ', hypothesis.hypstr,"\tMODEL SCORE: ", hypothesis.best_score,"\tCONFIDENCE: ", logmath.exp(hypothesis.prob)

    print '\nBEST HYPOTHESIS SEGMENTS: ', [seg.word for seg in decoder.seg()]

    # Access N best decodings.

    print ('\nBEST 10 HYPOTHESIS:\n')
    for best, i in zip(decoder.nbest(), range(10)):
        print '\t',"HYPOTHESIS: ",best.hypstr, "\tSCORE: ",best.score

except AttributeError, e:
    print '\tError: ',e
    print '\t',"N.B: This error usually occurs when no sound is detected !!"
