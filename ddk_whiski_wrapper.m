% ddk_whisk_wrapper.m
%% DOCUMENTATION TABLE OF CONTENTS:
% I. OVERVIEW
% II. REQUIREMENTS
% III. INPUTS
% IV. OUTPUTS

% last updated DDK 2017-10-

%% I. OVERVIEW:
% This script is a wrapper for Nathan Clack's `Whisk` whisker tracking
% software package. In addition to calling the whisk commands `trace` and
% `measure` from the command line, it saves some metadata like SHA1
% checksums of input and output files, date and time of analysis, analysis
% duration, and analysis computer host name.


%% II. REQUIREMENTS:
% 1) Nathan Clack's `Whisk` software package, available at https://openwiki.janelia.org/wiki/display/MyersLab/Whisker+Tracking+Downloads
% 2) The MATLAB toolbox JSONlab, available at https://www.mathworks.com/matlabcentral/fileexchange/33381-jsonlab--a-toolbox-to-encode-decode-json-files
% 3) 



%% Time all of this processing:
tic;  


%% Define path to inputs:
input_video_path = '/mnt/nas2/homes/dan/MultiSens/data/5036-2/2P/2017-09-27/site1/grab01/whiskvid/2017-09-26_ddk-1.avi'; % SPECIFY INPUT PATH HERE
[input_dir, raw_video_name, ext] = fileparts(input_video_path);
base = [input_dir filesep raw_video_name];
cd(input_dir);


%% Invert colors (assusing white foreground on black background):
inverted_movie_path = [base '_inverted.mp4'];
disp('Inverting raw movie...');
[err1, sysout1] = system(['ffmpeg -i ' input_video_path ' -vf lutyuv=y=negval -vcodec mpeg4 -q 2 ' inverted_movie_path]); 
disp('... done inverting raw movie.');


%% Create .whiskers file using whisk `trace` command:
whiskers_path = [base '.whiskers'];
disp('Tracing whiskers...');
[err2, sysout2] = system(['trace ' inverted_movie_path ' ' whiskers_path]);
disp('... done tracing whiskers.');


%% Create .measurements file using whisk `measure` command:
measurements_path = [base '.measurements'];
disp('Measuring whisker movement...');
[err3, sysout3] = system(['measure --face right ' whiskers_path ' ' measurements_path]);
disp('... done measuring whisker movement.');

duration = toc; % get duration


%% Write metadata:

% Inputs:
Metadata.inputs(1).path = input_video_path;

% Outputs:
Metadata.outputs(1).path = inverted_movie_path;
Metadata.outputs(2).path = whiskers_path;
Metadata.outputs(3).path = measurements_path;

% Add duration.
Metadata.processing_time = duration;

% Write:
metadata_path = [input_dir filesep 'whisk_metadata.json'];
writeMetadata(Metadata,metadata_path);
