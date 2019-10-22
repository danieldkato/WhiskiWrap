"""
preprocess_whisker_video.py

DOCUMENTATION TABLE OF CONTENTS:
I. OVERVIEW
II. USAGE
III. REQUIREMENTS
IV. INPUTS
V. OUTPUTS

last updated DDK 2019-09-18

################################################################################
I. OVERVIEW:

This script acts as a wrapper for ffmpeg, which I use to invert, crop, and
re-format raw whisker video from .avi to .mp4 to prepare it to run through
WhiskiWrap. I use this wrapper to organize the inputs and outputs in a way that
I like and fits in with my workflow; all parameters are saved in a parameters
JSON file, and analysis metadata is saved in a format consistent with the rest
of my analyses.


################################################################################
II. USAGE:

To use this funciton, enter the following into the command line:

python preprocess_whisker_video.py <mouse> <date> <site> <grab> <params_file> <w> <h> <x> <y>


################################################################################
III. REQUIREMENTS:

1) The module `utilities`, available at https://github.com/danieldkato/utilities.git

This code assumes that the raw data are organized as follows:
|-mouse/
    |-2P/
        |-<date> # must be formatted '<YYYY>-<MM>-<DD>'
            |-<site>/ # must be formatted 'site<N>'
                |-<grab>/ # must be formatted 'grab<MM>' 
                    |-video/
                        |-<whisker_video>.avi # can be named anything

There must be only one .avi in the video directory.  

Note this assumes that the input video depicts white whiskers on a black
background. This is how I acquire my raw video, which must be inverted in order
to be compatible with whisk. 


################################################################################
IV. INPUTS:

1) mouse: string specifying the name of the mouse in the video to be processed.

2) date: string specifying the date of the session during which the video to
process was acquired. Must be formatted <YYYY>-<MM>-<DD>, where <YYYY> stands
for year, <MM> stands for month, and <DD> stands for day.  

3) site: string specifying the imaging site from which the movie to process was acquired. Should be formatted site<N>, where <n> is an integer site number.

4) grab: string specifying the grab ID of the movie to process. Should be formatted grab<NN>, where <NN> stands for a 2-digit integer grab number.

5) w: the desired width of the cropped output video, in pixels   

6) h: the desired height of the cropped output video, in pixels   

7) x: the x-coordinate, in pixels, of the upper-left hand corner of the area to
include in the output movie.     

8) y: the y-coordinate, in pixels, of the upper-left hand corner of the area to
include in the output movie.     


################################################################################
V. OUTPUTS:

This function calls ffmpeg to invert the input video (i.e., switch black and
white), crop it, and convert it from a.avi to a .mp4 (necessary to work with
WhiskiWrap). 


################################################################################
"""

from sys import argv
import os
from utilities_ddk.python.mouse_utils import find_raw_TIFF
 
def preprocess_whisker_video(*argv):
    # Read input arguments:
    argv = argv[0]

    mouse = argv[0]
    date = argv[1]
    site = argv[2]
    grab = argv[3]
    w = argv[4]
    h = argv[5]
    x = argv[6]
    y = argv[7]
  
    # Find input video:
    raw_tiff_path = find_raw_TIFF(mouse, date, site, grab) # raw tiff path
    sep = os.path.sep
    fparts = raw_tiff_path.split(sep)
    grab_directory = sep.join(fparts[0:-2]) # grab directory
    vid_directory = os.path.join(grab_directory, 'video')  
    videos = [v for v in os.listdir(vid_directory) if '.avi' in v] 

    # Make sure there is exactly one whisker video in directory:
    if len(videos) == 0:
        raise Exception('No whisker video found for mouse ' + mouse + ', session ' + date + ', site ' + site[-1] + ', grab ' + grab[-2:] + '. Please ensure that whisker video is saved in ' + vid_directory + '.')
    elif len(videos) > 1:
        raise Exception('More than one whisker video found for mouse ' + mouse + ', session ' + date + ', site ' + site[-1] + ', grab ' + grab[-2:] + '. Please ensure that only one whisker video is saved in ' + vid_directory + '.')

    # Generate output video path:
    input_vid_name = videos[0]
    input_vid_path = os.path.join(vid_directory, input_vid_name)
    output_vid_name = input_vid_name[0:-4] + '.mp4'
    output_vid_path = os.path.join(vid_directory, output_vid_name)
    print('output_vid_path = ' + output_vid_path)
   
    # Generate command:
    cmd = 'ffmpeg -i ' + input_vid_path + ' -vf "lutyuv=y=negval,crop=' + w + ':' + h + ':' + x + ':' + y + '" -vcodec mpeg4 -q 2 ' + output_vid_path  
    print('w = ' + w)
    print('h = ' + h)
    print('x = ' + x)
    print('y = ' + y)
    print('cmd = ' + cmd)

    # Execute command through command line:
    os.system(cmd)


if __name__ == "__main__":
    preprocess_whisker_video(argv[1:])
