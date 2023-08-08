#!/usr/bin/python3

# brew install pygobject3 gst-python
# pip3 install numpy gobject PyGObject

'''
Examples:

python3 run.py 'rtspsrc location=rtspt://user:pass@camera.com:5540/Streaming/Channels/101 ! rtph264depay ! identity name=adjust ! fakesink'

Example output:
frames =  4399  per frame =  33290161.90725165  fps =  30.0389
frames =  4499  per frame =  33290024.964881085  fps =  30.039
frames =  4599  per frame =  33290086.495107632  fps =  30.039
'''

import sys
import logging
import numpy as np
import time
import os

import signal

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstApp", "1.0")
from gi.repository import Gst, GstApp, GObject, GLib



Gst.init(None)

last_pts = 0
last_real_pts = 0
class Main:
    def __init__(self):

        self.signed = None
        self.depth = None
        self.rate = None
        self.channels = None

        self.last_pts = None
        self.start_pts = None
        self.frames = 0

        self.start()

        signal.signal(signal.SIGTERM, self.signal_term_handler)


        src_element = self.pipeline.get_by_name('adjust')
        if src_element: 
            #print(src_element)
            #get the static source pad of the element
            srcpad = src_element.get_static_pad('src')
            
            #add the probe to the pad obtained in previous solution
            probeID = srcpad.add_probe(Gst.PadProbeType.BUFFER, self.calc_pts)
            
        # The MainLoop
        self.mainloop = GLib.MainLoop()


        # And off we go!

        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            self.quit()
            sys.exit(0)



    def signal_term_handler(self, signal, frame):
        print('got SIGTERM')
        self.quit()
        sys.exit(0)



    def quit(self):
        
        if self.start_pts != None:
            delta = self.last_pts - self.start_pts
            print("Last PTS = ", self.last_pts)
            print("delta = ", delta)
            print("frames = ", self.frames)
            print("per frame = ", (delta/(self.frames-1)))

        self.pipeline.set_state(Gst.State.NULL)

        self.bus.disconnect(self.on_message_handler_id)
        del self.on_message_handler_id
        self.bus.remove_signal_watch()
        print('done, deleting pipeline')
        del self.pipeline        
        sys.exit(0)

    def start(self):
        global average_list

        print(' '.join(sys.argv[1:]))

        self.pipeline = Gst.parse_launch(' '.join(sys.argv[1:]))
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.on_message_handler_id = self.bus.connect("message", self.on_message)


        self.pipeline.set_state(Gst.State.PLAYING)
        self.pipeline.get_state(Gst.CLOCK_TIME_NONE)


    def calc_pts(self, pad, info):
        global last_pts, last_real_pts, average_list

        pts = info.get_buffer().pts

        if self.start_pts == None and self.frames == 300:
            print("Logged start PTS = ",pts)
            self.start_pts = pts
            self.frames = 0

        self.last_pts = pts

        self.frames = self.frames + 1

        if self.frames % 100 == 0 and self.start_pts != None:
            delta = self.last_pts - self.start_pts
            per = (delta/(self.frames-1))
            print("frames = ",(self.frames-1)," pts per frame = ",per," fps = ", round((1000000000/per),4))

        return Gst.PadProbeReturn.OK


        #self.mainloop.quit()


    def do_on_message(self, bus, message):
        """
        Add extra message handling by overriding this in your
        subclass.  If this method returns True, no further message
        handling is performed.  If this method returns False,
        message handling continues with default cases or EOS, INFO,
        WARNING and ERROR messages.
        """
        return False

    def on_message(self, bus, message):
        if self.do_on_message(bus, message):
            pass
        elif message.type == Gst.MessageType.EOS:
            print("eos")
            print('setting to Null')
            self.pipeline.set_state(Gst.State.NULL)
            self.quit()
        elif message.type == Gst.MessageType.INFO:
            gerr, dbgmsg = message.parse_info()
            print("info (%s:%d '%s'): %s" % (gerr.domain, gerr.code, gerr.message, dbgmsg))
        elif message.type == Gst.MessageType.WARNING:
            gerr, dbgmsg = message.parse_warning()
            print("warning (%s:%d '%s'): %s" % (gerr.domain, gerr.code, gerr.message, dbgmsg))
        elif message.type == Gst.MessageType.ERROR:
            gerr, dbgmsg = message.parse_error()
            # FIXME:  this deadlocks.  shouldn't we be doing this?
            #self.pipeline.set_state(gst.STATE_NULL)
            self.quit()
            sys.exit("error (%s:%d '%s'): %s" % (gerr.domain, gerr.code, gerr.message, dbgmsg))

        elif message.type == Gst.MessageType.STATE_CHANGED:

            old, new, pending = message.parse_state_changed()
            if not message.src == self.pipeline:
                return

            self.state = new
            print("State changed from {0} to {1}".format(Gst.Element.state_get_name(old), Gst.Element.state_get_name(new)))


class Error(Exception):

    def __init__(self, message, detail=None):
        global last_detail

        self.message = message
        if detail:
            self.detail = detail
        else:
            self.detail = last_detail

        logging.debug('audio: Error %s %s', self.message, self.detail)

    def __str__(self):
        return '%s - %s' % (self.message, self.detail)



runner = Main()
