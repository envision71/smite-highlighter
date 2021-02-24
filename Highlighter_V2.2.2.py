import sys, getopt
from moviepy.editor import*
import cv2 as cv
import numpy as np
import time
from time import sleep
import datetime
from datetime import date
import errno, os
from tqdm import tqdm
from skimage.measure import compare_ssim

class ROI:
    def __init__(self, name,roi=[0]):
        self.name = name
        #Region of intrest to capture
        self.roi = roi
        #Toggle for it can trigger a clip
        self.toggle = False

class aClip:
    def __init__(self,start,end,tags,matchID):
        self.tags=tags
        self.start=start
        self.end=end
        self.matchID=matchID

    def getStart(self):
        return self.start
    def getEnd(self):
        return self.end
    def setEnd(self,time):
        self.end=time

    def getTags(self):
        return self.tags
    def addTag(self,tag):
        self.tags.append(tag)
    def setmatchID(self,matchID):
        self.matchID = matchID
    def getmatchID(self):
        return self.matchID
        
        
    
today = date.today()        



def highlighter(inputfile, outputpath):
    #check if the provided mp4 is a valid mp4 file
    if((os.path.isfile(inputfile) == False) or  (inputfile.endswith('.mp4'))==False):
        print('inputfile is not a valid mp4 file')
        exit()
    #check for output folders. If it does not exist create
    if((os.path.isfile(outputpath) == False) or
       (os.path.isfile(outputpath+'/Matches')== False) or
       (os.path.isfile(outputpath+'/Kills')==False) or
       (os.path.isfile(outputpath+'/Deaths')==False) or
       (os.path.isfile(outputpath+'/Assists')==False)):
        try:
            os.makedirs(outputpath)
            os.makedirs(outputpath+'/Matches')
            os.makedirs(outputpath+'/Kills')
            os.makedirs(outputpath+'/Deaths')
            os.makedirs(outputpath+'/Assists')
        except OSError as e:
            if e.errno != errno.EEXIST:
                print(e.errno)
                print('could not make output file directory')
                exit()
    #Video you want highlighted
    video=inputfile
    output=outputpath
    cap = cv.VideoCapture(video)
    #get fps and max amount of frames
    fps = int(cap.get(cv.CAP_PROP_FPS))
    maxFrame=int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    #Params used for moviepy
    widthOG = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    heightOG =int( cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    clip = VideoFileClip(video)
    #Amount of seconds you want to capture before and after
    Seconds_Before_Kill =12
    Seconds_After_Kill =12

    #get the date in month-day-year
    date = today.strftime('%m-%d-%Y')
    #Used later to check if the current clip starts during the prevous
    check=0
    inMatch = False
    #Get the 1st frame of the video to use as a base line
    cir,compare = cap.read()
    #Resize and grayscale for less pixel data tp speed up slightly
    compare = cv.resize(compare,(900,600),fx=0,fy=0,
           interpolation=cv.INTER_CUBIC)
    compare=cv.cvtColor(compare,cv.COLOR_RGB2GRAY)

    #base images to use as compaisions later on
    loadingF = cv.imread('loadcard.jpg', cv.IMREAD_GRAYSCALE)
    loadingF = loadingF[550:590,0:600]
    godpickF = cv.imread('godpick.png',cv.IMREAD_GRAYSCALE)
    defeatF = cv.imread('defeatF.png',cv.IMREAD_GRAYSCALE)
    victoryF = cv.imread('victoryF.png',cv.IMREAD_GRAYSCALE)
    #This is the ROI's
    Kills = ROI('Kills')
    Kills.roi = compare[490:500,25:35]
    Deaths = ROI('Deaths')
    Deaths.roi=compare[490:500,60:70]
    Assists=ROI('Assists')
    Assists.roi=compare[490:500,95:105]
    ROIarray=[Kills,Deaths,Assists]
    #Resize so theres a bit more pixels to work with
    width = int(Kills.roi.shape[1]*500/100)
    height = int(Kills.roi.shape[0]*500/100)
    dsize = (width, height)
    Kills.roi=cv.resize(Kills.roi,dsize)
    Deaths.roi=cv.resize(Deaths.roi,dsize)
    Assists.roi=cv.resize(Assists.roi,dsize)
    font = cv.FONT_HERSHEY_SIMPLEX
    #Initalize empty clip array outside of loop
    clipsArray= []
    KillsArray=[]
    DeathsArray=[]
    AssistsArray=[]
    MatchArray=[]
    pbar=tqdm(total=maxFrame)

    #Loop while video is open
    while (cap.isOpened()):
        pbar.update(1)
        #Read the video
        ret,frameOG=cap.read()
        preview=0

        #If video is over release the feed and write the highlight video
        if not ret:
            cv.destroyAllWindows()
            cap.release()
            GamesArray=[]
            if len(MatchArray)>0:
                #go over the match array to create match videos
                for idx, val in enumerate(MatchArray):
                    clip1=clip.subclip(val.getStart(),val.getEnd())
                    GamesArray.append(clip1)
                    Match_clip=concatenate_videoclips(GamesArray)
                    Match_clip.write_videofile("{0}/Matches/Match{1}-{2}.mp4".format(output,date,idx))
                    clip1.close()
                    del GamesArray[-1]
            if len(clipsArray) >0:        
                #go over clips array and create vids according to the tags
                for idx, val in enumerate(clipsArray):
                    clip1=clip.subclip(val.getStart(),val.getEnd())
                    if('Kills' in val.getTags()):
                        clip1.write_videofile('{0}/Kills/{1}_{2}_{3}.mp4'.format(output,date,val.getmatchID(),idx))
                    if('Deaths' in val.getTags()):
                        clip1.write_videofile('{0}/Deaths/{1}_{2}_{3}.mp4'.format(output,date,val.getmatchID(),idx))            
                    if('Assists' in val.getTags()):
                        clip1.write_videofile('{0}/Assists/{1}_{2}_{3}.mp4'.format(output,date,val.getmatchID(),idx))

                       
            print("end of file")
            break
        
        #Get the frame number
        frameNum=int(cap.get(cv.CAP_PROP_POS_FRAMES))
        #Resize the frame
        frame = cv.resize(frameOG,(900,600),fx=0,fy=0,
           interpolation=cv.INTER_CUBIC)
        #and turn it to grayscale
        frame=cv.cvtColor(frame,cv.COLOR_RGB2GRAY)



        #godpicksROI = frame[120:400,220:400]
        #(godpickscore,diff) = compare_ssim(godpickF,godpicksROI,full=True)

        #compare the loading frame to the loading image
        #if its above .7 then set inMatch flag to true
        loadingROI= frame[550:590,0:600]
        (loadingframesscore,diff) = compare_ssim(loadingF,loadingROI,full=True)
        if(loadingframesscore>0.7 and inMatch==False):
            inMatch=True
            start=int((frameNum/fps))
            gameClip = aClip(start,0,'game',len(MatchArray))
            MatchArray.append(gameClip)

        #compare theend screens to frame.
        #if its above 0.9 then set the inMatch flag to false   
        victoryROI=frame[200:325,250:650]
        defeatROI=frame[200:325,250:650]
        (victoryScore,diff) = compare_ssim(victoryF,victoryROI,full=True)
        (defeatScore,diff) = compare_ssim(defeatF,defeatROI,full=True)
        if((defeatScore>0.9 or victoryScore>0.9) and inMatch==True):
            inMatch=False
            end= int((frameNum/fps))
            MatchArray[-1].end=end
        #Set the scoreKills (% of how diffrant the images are) to 1 by default
        scoreKills=1.1
        #The previews
        score=1.0
        for idx, val in enumerate(ROIarray):
            if((frameNum%(fps*1)==0)and inMatch==True):
                size=val.roi.shape[1]
                x=(25*(idx+1))+(10*idx)
                preview=frame[490:500,x:x+10]
                preview=cv.resize(preview,dsize)
                #Threshold so we end with a pure black and white image
                ret,preview = cv.threshold(preview,120,255,cv.THRESH_BINARY)
                (score,diff) = compare_ssim(preview,val.roi,full=True)
        
                val.roi=preview                  
                #If the score is between a range then make a clip of it
                if(score<0.6 and score >0.4):
                    placeholderTags=[val.name]
                    #To make a clip using moviepy it needs a start and end time NOT FRAME
                    #To get a time divide the current frame number divided by fps
        
                    #start would be the current frame number/fps -the time set before a kill
                    start=int((frameNum/fps)-(Seconds_Before_Kill))
                    #end would be the current frame number/fps -the time set after a kill
                    end= int((frameNum/fps)+(Seconds_After_Kill))
                    #If the start time minus the start of the previous clip
                    #is less than or equal to a clips duration then remove the
                    #previous clip and use that start time as the start time.
                    #This is to combine clips that would capture the same events.
                    #(start-1) because its checking for the diff every 1 seconds
                    if ((start-1)-check)<=(Seconds_Before_Kill+Seconds_After_Kill):
                        start=check
                        if len(clipsArray) != 0:
                            #print(clipsArray[-1].getTags())
                            #holdingTags = clipsArray[-1].getTags()
                            #print(holdingTags)
                            placeholderTags = placeholderTags + clipsArray[-1].getTags()
                            del clipsArray[-1]
                    else:check=start
                    #If the clip start time would be negative set it to 0
                    if start<0: start = 0
                    if end>(maxFrame/fps):end = int(maxFrame/fps)
                    #Create clip and add it to the clip array
                    clip1 = aClip(start,end,placeholderTags,len(MatchArray))
                    
                    clipsArray.append(clip1)



        #Show the frame
        #cv.imshow('frame', frame)
        
           

        #Stop running if q is pressed
        if cv.waitKey(1) & 0xFF == ord('q'):
            cv.destroyAllWindows()
            cap.release()
            finalArray=[]
            GamesArray=[]
            if len(MatchArray)>0:
                #go over the match array to create match videos
                for idx, val in enumerate(MatchArray):
                    clip1=clip.subclip(val.getStart(),val.getEnd())
                    GamesArray.append(clip1)
                    Match_clip=concatenate_videoclips(GamesArray)
                    Match_clip.write_videofile("{0}/Matches/Match{1}-{2}.mp4".format(output,date,idx))
                    clip1.close()
                    del GamesArray[-1]
            if len(clipsArray) >0:               
                #go over clips array and create vids according to the tags
                for idx, val in enumerate(clipsArray):
                    clip1=clip.subclip(val.getStart(),val.getEnd())
                    if('Kills' in val.getTags()):
                        clip1.write_videofile('{0}/Kills/{1}_{2}_{3}.mp4'.format(output,date,val.getmatchID(),idx))
                    if('Deaths' in val.getTags()):
                        clip1.write_videofile('{0}/Deaths/{1}_{2}_{3}.mp4'.format(output,date,val.getmatchID(),idx))            
                    if('Assists' in val.getTags()):
                        clip1.write_videofile('{0}/Assists/{1}_{2}_{3}.mp4'.format(output,date,val.getmatchID(),idx))
                       
            print("q was pressed")
            break

def main(argv): 
    inputfile = ''
    outputpath= ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
      print ('test.py -i <inputfile path> -o <outputfile path>')
      sys.exit(2)
    if len(opts) <=1:
        print('test.py -i <inputfile path"> -o <outputfile path> (put the paths in quotes)')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -i <inputfile path> -o <outputfile path>')
            sys.exit()
        elif opt in ("-i", "--ifile"):           
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputpath = arg
    print( 'Input file is ', inputfile)
    print( 'Output file is ', outputpath)
    highlighter(inputfile,outputpath); 

if __name__=="__main__": 
    main(sys.argv[1:]) 

