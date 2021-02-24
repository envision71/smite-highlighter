# smite-highlighter
Creates mp4 files everytime the K/D/A changes and whole matches for the game smite

## How it works
A MP4 file is passed in. The video's resolution is converted to 900 by 600 pixels and turned to grayscale. By comparing hardcoded ROI's (regions of intrests) of the video to ROI's of comparison images, supplied from the directory, it finds when a game starts, ends, and changes in K/D/A. 

### Match Identification
When the loading screen cards are identified it signals that a match has started and enables clip creation. It will start recording from that point until the victory or defeat screen is identified.

### Clip Creation
Changes in the K/D/A HUD trigger the creation of a MP4 clip. Duration of clips are hard coded as of now to be 12 seconds before and after a change is detected. If another change is detected whithin the 12 seconds after the event that created the clip, the clip is extend by another 12 seconds. 

This was created using video files that are 1920 by 1080. Locations of ROI's will have to be ajusted base on your videos resolution and sample images.

## Usage
In a command prompt navigate to where the Highlighter_V2.2.2.py and comparison images are located. Enter
```Shell
  Highlighter_V2.2.2.py -i "<input file path>" -o "<output file directory>"
  ``` 
The quotes around file paths are necessary. Input file path is the location of the video you want to highlight and output path is where you want the clips and matches to be outputted.

While it looks over the video you can see what frame it is on out of how many, how long it has been working, when it expects to finish, and how many frames per a second it is going.
```Shell
 0%|                                                                          | 791/1675777 [00:10<6:12:42, 74.90it/s]
 ```
 Once it reaches 100% it starts to make all the clips and match videos.
