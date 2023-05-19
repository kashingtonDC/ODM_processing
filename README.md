# The Drone Mapping Cookbook

Instructions and scripts to build and run drone orthomosaicking, DEM generation, and surface water analysis routines 
Dependencies: Docker, OpenDroneMap
Prepared by: Aakash Ahamed, PhD (aahamed@stanford.edu)

See https://docs.google.com/document/d/1sJUsGqfM-le45ZQSXb2bzMQYs-Av3KOQjwuVcgDYtqw/edit#heading=h.7qg37xdnkpx for the cookbook! 

Useful commands: 

# To orthmomosaic from list of vis or tir images 
`docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME>`

# To generate a DSM
`docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME> --dsm --dem-resolution 2 --smrf-threshold 0.4 --smrf-window 24`

# To generate a DTM
`docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME> --dtm --dem-resolution 2 --smrf-threshold 0.4 --smrf-window 24`

# To generate a DEM and DSM 
`docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME> --dtm --dem-resolution 2 --smrf-threshold 0.4 --smrf-window 24 && docker run -ti --rm -v /Users/aakashahamed/Desktop/datasets:/datasets opendronemap/odm --project-path /datasets <FOLDER_NAME> --dsm --dem-resolution 2 --smrf-threshold 0.4 --smrf-window 24`
