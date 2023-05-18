# The Drone Pilot's Cookbook

Instructions and scripts to build and run drone orthomosaicking, DEM generation, and analysis software
Dependencies: Docker, OpenDroneMap
Prepared by: Aakash Ahamed


# To orthmomosaic from list of vis or tir images 
`docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME>`

# To generate a DSM
`docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME> --dsm --dem-resolution 2 --smrf-threshold 0.4 --smrf-window 24`

# To generate a DTM
`docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME> --dtm --dem-resolution 2 --smrf-threshold 0.4 --smrf-window 24`

# To generate a DEM and DSM 
`docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME> --dtm --dem-resolution 2 --smrf-threshold 0.4 --smrf-window 24 && docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME> --dsm --dem-resolution 2 --smrf-threshold 0.4 --smrf-window 24`
