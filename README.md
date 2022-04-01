# regular orthophoto
docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME>

# DSM
docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME> --dtm --dem-resolution 2 --smrf-threshold 0.4 --smrf-window 24


# TODO: 
* edit `split_vis_nir.py` to split vis / tir based on number of channels in image, NOT based on image dimensions. 
* ^ or, multi criteria based on Nchannels and image dimensions 