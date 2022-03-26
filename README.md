# regular orthophoto
docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets project2

# DSM
docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets NYE_vis --dsm


# TODO: 
* edit `split_vis_nir.py` to split vis / tir based on number of channels in image, NOT based on image dimensions. 
* ^ or, multi criteria based on Nchannels and image dimensions 