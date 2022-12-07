import time

from pygame import mixer

from sound import Sound
mixer.init()
s = Sound("sources/sounds/land2-43790.mp3")
while True:
    s.play()
    time.sleep(1)