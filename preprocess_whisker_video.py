from sys import argv
import os
import mouse_utils

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
    raw_tiff_path = mouse_utils.find_raw_TIFF(mouse, date, site, grab) # raw tiff path
    sep = os.path.sep
    fparts = raw_tiff_path.split(sep)
    grab_directory = sep.join(fparts[0:-2]) # grab directory
    vid_directory = os.path.join(grab_directory, 'video')  
    videos = [x for x in os.listdir(vid_directory) if '.avi' in x] 

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

    # Execute command through command line:
    os.system(cmd)


if __name__ == "__main__":
    preprocess_whisker_video(argv[1:])
