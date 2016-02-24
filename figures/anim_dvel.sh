#!/bin/bash

avconv -i frames/%04d.png -b 1M anim_dvel.mp4 -y
avconv -i frames/%04d.png -b 1M anim_dvel.ogg -y
