"""
NAME
ddk_whiski_wrapper.py



SYNOPSIS
python ddk_whiski_wrapper.py <mouse> <date> <site> <grab> <params_file>



DESCRIPTION
Wrapper script for Chris Rodgers' WhiskiWrap, which is itself a wrapper for
Nathan Clack's whisk. I use this to organize the inputs and outputs in a way
that I like and fits in with my workflow; all parameters are saved in a
parameters JSON file, and analysis metadata is saved in a format consistent
with the rest of my analyses.

<mouse>: 
    Name of the mouse in the video to be processed.

<date>: 
    Date of the session during which the video to process was acquired. Must be
    formatted <YYYY>-<MM>-<DD>, where <YYYY> stands for year, <MM> stands for
    month, and <DD> stands for day.  

<site>: 
    Name of the imaging site from which the movie to process was acquired.
    Should be formatted site<N>, where <N> is an integer site number.

<grab>: 
    Grab ID of the movie to process. Should be formatted grab<NN>, where <NN>
    stands for a 2-digit integer grab number.

<params_file>: 
    Path to a JSON file speicfying WhiskiWrap parameters. See EXAMPLES below on
    how to format. 



RETURNS
This function saves to secondary storage an hdf5 file containing the output of
whisk. It also creates a large number of temporary files used to parallelize
the input movie as well as a JSON metadata file including paths and sha1
checksums to input and output files, parameters, and any available version
information about software dependenies. 



SOFTWARE DEPENDENCIES
* WhiskiWrap, available at https://github.com/cxrodgers/WhiskiWrap/.git. Note that
   this package itself has a number of dependencies, including: 
        a) whisk, 
        b) tifffile, and
        c) my, another module available on cxrodgers' github.

* The module `utilities`, available at https://github.com/danieldkato/utilities.git



OTHER REQUIREMENTS
This code assumes that the raw data are organized as follows:
|-mouse/
    |-2P/
        |-<date> # must be formatted '<YYYY>-<MM>-<DD>'
            |-<site>/ # must be formatted 'site<N>'
                |-<grab>/ # must be formatted 'grab<MM>' 
                    |-video/
                        |-<whisker_video>.mp4 # can be named anything

There must be only one .mp4 in the video directory.  

Note this assumes that the input video depicts black whiskers on a white 
background. If this is not the case, first run ffmpeg on the input video
to invert the colors.

If running on a system where whisk or WhiskiWrap must be run from a conda
environment, the environment must be activated before running this script.



EXAMPLES
Example contents of a parameters JSON file could be: 

{
"pix_fmt":"gray",
"bufsize":10E8,
"duration":"None",
"start_frame_time":"None",
"start_frame_number":"None",
"write_stderr_to_screen":"False",
"tiffs_to_trace_directory":"",
"sensitive":"False",
"chunk_size":200,
"chunk_name_pattern":"chunk%08d.tif",
"stop_after_frame":"None",
"delete_tiffs":"True",
"timestamps_filename":"None",
"monitor_video":"None",
"monitor_video_kwargs":"None",
"write_monitor_ffmpeg_stderr_to_screen":"False",
"frame_func":"None",
"n_trace_processes":4,
"expectedrows":1000000,
"verbose":"True",
"skip_stitch":"False",
"face":"right"
}   


Last updated DDK 2019-11-23.







DOCUMENTATION TABLE OF CONTENTS:
I. OVERVIEW
II. USAGE
III. REQUIREMENTS
IV. INPUTS
V. OUTPUTS

last updated DDK 2019-09-18

################################################################################
I. OVERVIEW:

This script acts as a wrapper for Chris Rodgers' WhiskiWrap, which is itself a wrapper
for Nathan Clack's whisk. I use this to organize the inputs and outputs in a
way that I like and fits in with my workflow; all parameters are saved in a parameters 
JSON file, and analysis metadata is saved in a format consistent with the rest of my analyses.


################################################################################
II. USAGE:

To use this funciton, enter the following into the command line:

python ddk_whiski_wrapper.py <mouse> <date> <site> <grab> <params_file>


################################################################################
III. REQUIREMENTS:

1) WhiskiWrap, available at https://github.com/cxrodgers/WhiskiWrap/.git. Note that
   this package itself has a number of dependencies, including: 
        a) whisk, 
        b) tifffile, and
        c) my, another module available on cxrodgers' github.

2) The module `utilities`, available at https://github.com/danieldkato/utilities.git

This code assumes that the raw data are organized as follows:
|-mouse/
    |-2P/
        |-<date> # must be formatted '<YYYY>-<MM>-<DD>'
            |-<site>/ # must be formatted 'site<N>'
                |-<grab>/ # must be formatted 'grab<MM>' 
                    |-video/
                        |-<whisker_video>.mp4 # can be named anything

There must be only one .mp4 in the video directory.  

Note this assumes that the input video depicts black whiskers on a white 
background. If this is not the case, first run ffmpeg on the input video
to invert the colors.


################################################################################
IV. INPUTS:

1) mouse: string specifying the name of the mouse in the video to be processed.

2) date: string specifying the date of the session during which the video to
process was acquired. Must be formatted <YYYY>-<MM>-<DD>, where <YYYY> stands
for year, <MM> stands for month, and <DD> stands for day.  

3) site: string specifying the imaging site from which the movie to process was acquired. Should be formatted site<N>, where <n> is an integer site number.

4) grab: string specifying the grab ID of the movie to process. Should be formatted grab<NN>, where <NN> stands for a 2-digit integer grab number.

5) params_file: path to a JSON file speicfying WhiskiWrap parameters. Example
contents of a parameters file could be: 

{
"pix_fmt":"gray",
"bufsize":10E8,
"duration":"None",
"start_frame_time":"None",
"start_frame_number":"None",
"write_stderr_to_screen":"False",
"tiffs_to_trace_directory":"",
"sensitive":"False",
"chunk_size":200,
"chunk_name_pattern":"chunk%08d.tif",
"stop_after_frame":"None",
"delete_tiffs":"True",
"timestamps_filename":"None",
"monitor_video":"None",
"monitor_video_kwargs":"None",
"write_monitor_ffmpeg_stderr_to_screen":"False",
"frame_func":"None",
"n_trace_processes":4,
"expectedrows":1000000,
"verbose":"True",
"skip_stitch":"False",
"face":"right"
}   


################################################################################
V. OUTPUTS:

This function saves to secondary storage an hdf5 file containing the output of 
whisk. It also creates a large number of temporary files used to parallelize

################################################################################
"""
import WhiskiWrap
from sys import argv
import json 
import os
import subprocess
from utilities_ddk.python.Metadata import Metadata, write_metadata
from utilities_ddk.python.mouse_utils import find_raw_TIFF, create_dummy_file, find_max_dir_suffix 


habanero_root = '/rigel/zi/users/dk2643/MultiSens/data'
farscape_root = '/mnt/farscape/homes/dan/MultiSens/data'



def transfer_whiski_output(output_path):
    output_dir = os.path.split(output_path)[0]
    farscape_output_dir = output_dir.replace(habanero_root, farscape_root) 
    farscape_output_parent = os.path.split(farscape_output_dir)
    cmd = 'scp -r ' + output_dir + 'dan@companion.bruno.zi.columbia.edu:' + farscape_output_parent  
    os.system(cmd2)



def main(*argv):

    argv = argv[0]
    mouse = argv[0]
    date = argv[1]
    site = argv[2]
    grab = argv[3]
    params_file_path = argv[4]
  
    # Find input video:
    raw_tiff_path = find_raw_TIFF(mouse, date, site, grab) # raw tiff path
    sep = os.path.sep
    fparts = raw_tiff_path.split(sep)
    grab_directory = sep.join(fparts[0:-2]) # grab directory
    vid_directory = os.path.join(grab_directory, 'video')  
    videos = [x for x in os.listdir(vid_directory) if '.mp4' in x] 

    # Make sure there is exactly one mp4 in directory:
    if len(videos) == 0:
        raise Exception('No whisker video found for mouse ' + mouse + ', session ' + date + ', site ' + site[-1] + ', grab ' + grab[-2:] + '. Please ensure that whisker video is saved in ' + vid_directory + '.')
    elif len(videos) > 1:
        raise Exception('More than one whisker video found for mouse ' + mouse + ', session ' + date + ', site ' + site[-1] + ', grab ' + grab[-2:] + '. Please ensure that only one whisker video is saved in ' + vid_directory + '.')

    # Generate output path:
    input_vid_name = videos[0]
    input_path = os.path.join(vid_directory, input_vid_name)
    max_whiski_dir = find_max_dir_suffix(vid_directory, 'whiski_output_')
    output_fname = input_vid_name[0:-4] + '_whiski_output.hdf5'
    output_dir = os.path.join(vid_directory, 'whiski_output_' + str(max_whiski_dir+1))
    output_path = os.path.join(output_dir, output_fname)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Get parameters from JSON file:
    with open(params_file_path) as data_file:
        params = json.load(data_file)

    # Do some JSOn-to-Python conversion:
    for p in params:
        if params[p] == 'None':
            params[p] = None
        elif params[p] == 'True':
            params[p] = True
        elif params[p] == 'False':
           params[p] = False

    # Auto-generate name of output file:
    #output_path = os.path.dirname(input_path) + os.path.sep + 'whiski_output.hdf5'

    # Create input_reader object:
    input_reader = WhiskiWrap.FFmpegReader(input_filename=input_path,
        pix_fmt=params["pix_fmt"],
        bufsize=int(params["bufsize"]),
        duration=params["duration"],
        start_frame_time=params["start_frame_time"],
        start_frame_number=params["start_frame_number"],
        write_stderr_to_screen=params["write_stderr_to_screen"])

    # Run WhiskiWrap:
    print("Running WhiskiWrap...")
    if not params['debug']: 
        WhiskiWrap.interleaved_read_trace_and_measure(input_reader=input_reader,
            tiffs_to_trace_directory=os.path.dirname(input_path),
            sensitive=params["sensitive"],
            chunk_size=params["chunk_size"],
            chunk_name_pattern=params["chunk_name_pattern"],
            stop_after_frame=params["stop_after_frame"],
            delete_tiffs=params["delete_tiffs"],
            timestamps_filename=params["timestamps_filename"],
            monitor_video=params["monitor_video"],
            monitor_video_kwargs=params["monitor_video_kwargs"],
            write_monitor_ffmpeg_stderr_to_screen=params["write_monitor_ffmpeg_stderr_to_screen"],
            h5_filename=output_path,
            frame_func=params["frame_func"],
            n_trace_processes=params["n_trace_processes"],
            expectedrows=params["expectedrows"],
            verbose=params["verbose"],
            skip_stitch=params["skip_stitch"],
            face=params["face"])
    # If running in debug mode, just create a dummy output file:
    else:
        create_dummy_file(output_path)

    # Create Metadata object:
    print("Getting metadata...")
    M = Metadata()
    M.add_input(input_path)
    M.add_output(output_path)
    M.dict["parameters"] = params
    metadata_path = os.path.dirname(input_path) + os.path.sep + 'whiski_wrap_metadata.json'
    write_metadata(M, metadata_path)


if __name__ == "__main__":
    main(argv[1:])
