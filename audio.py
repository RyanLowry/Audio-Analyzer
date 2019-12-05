import pyaudio
import numpy
import math
import struct
from collections import deque

class PlaybackAudio():
    def __init__(self):
        #4096 - (chunk / channels)
        self.CHUNK = 8192
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self.queue = deque()
        self.audio = pyaudio.PyAudio()
        self.key_notes = {
		"C":["4","16","28","40","52","64","76","88"],
		"CS":["5","17","29","41","53","65","77","89"],
		"D":["6","18","30","42","54","66","78","90"],
		"DS":["7","19","31","43","55","67","79","91"],
		"E":["8","20","32","44","56","68","80","92"],
		"F":["9","21","33","45","57","69","81","93"],
		"FS":["10","22","34","46","58","70","82","94"],
		"G":["11","23","35","47","59","71","83","95"],
		"GS":["12","24","36","48","60","72","84","96"],
		"A":["1","13","25","37","49","61","73","85"],
		"AS":["2","14","26","38","50","62","74","86"],
		"B":["3","15","27","39","51","63","75","87"]
	    }
        self.curr_note = ""
        self.curr_freq = 0
        self.curr_amp = 0



    def callback(self,in_data,frame,time,flag):
        self.queue.append(in_data)
        return (in_data, pyaudio.paContinue)

    def get_items(self):
        return (self.curr_note,self.curr_amp,self.curr_freq)
    

    def record_audio(self):
        self.stream = self.audio.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK,
                        stream_callback = self.callback)

        frequencies = []
        amplitudes = []

        while self.stream.is_active():
            if self.queue:
                # data values, both fft and raw data
                data = self.queue.popleft()
                data = struct.unpack('{n}h'.format(n=self.CHUNK * 2), data)
                data = numpy.array(data)
                fft = numpy.fft.fft(data)

                #Amplitude, returning in decibles
                linear_RMS = numpy.sqrt(numpy.mean(data ** 2))
                log_RMS = 20 * math.log10(linear_RMS)
                amplitudes.append(log_RMS)
                self.curr_amp = log_RMS
                #TODO: figure out why frequency is sometimes doubled/tripled
                #Frequency, returning in hertz
                fft_freq = numpy.fft.fftfreq(len(data))
                ind = numpy.argmax(abs(fft))
                freq = fft_freq[ind]
                pitch = abs(freq * self.RATE * 2)
                frequencies.append(pitch)
                self.curr_freq = pitch
                #Note, returning letter note
                if pitch != 0:
                    note_num = 12 * (numpy.log2(pitch / 440)) + 49
                    rounded = round(note_num)
                    for note in self.key_notes.keys():
                        for i in self.key_notes[note]:
                            if rounded == int(i):
                                self.curr_note = note

    def stop_recording(self):
        self.stream.stop_stream()
        self.stream.close()