# Calculate FPS rate of an RTSP stream

This simple python script calculates the framerate of a RTSP stream based on the PTS field of it's frames.

Some camera manufacturers (Hikvision for example) state that their cameras produce output at 30fps. 
In reality, the FPS of a RTSP stream can be slightly different (30.039 or 29.97 fps for example).
This can produce stuttering when live streaming.

Usage:
```
python3 run.py 'rtspsrc location=rtspt://user:pass@camera.com:5540/Streaming/Channels/101 ! rtph264depay ! identity name=adjust ! fakesink'
```

Output:
```
frames =  2299  pts per frame =  33290094.903001305  fps =  30.039
frames =  2399  pts per frame =  33289677.256356817  fps =  30.0393
frames =  2499  pts per frame =  33289843.523809522  fps =  30.0392
frames =  2599  pts per frame =  33290053.84570989  fps =  30.039
frames =  2699  pts per frame =  33290112.12930715  fps =  30.0389
frames =  2799  pts per frame =  33290178.42300822  fps =  30.0389
```

The script outputs the FPS every 100 frames. The FPS is calculated based on the timestamp different of the first and the last frame received.
The first 300 frames are ignored, because the PTS can be unstable when connecting for the first time.

