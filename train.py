import glob, os
import random
import os.path
import time
from shutil import copyfile
from subprocess import call
import cv2
from xml.dom import minidom
from os.path import basename
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

#--------------------------------------------------------------------
xmlFolder = "/home/digits/datasets/palm_dataset/labels"
imgFolder = "/home/digits/datasets/palm_dataset/images"
saveYoloPath = "/home/digits/datasets/palm_dataset/yolo"
classList = { "palm":0 }

modelYOLO = "yolov3-tiny"  #yolov3 or yolov3-tiny
testRatio = 0.2
cfgFolder = "cfg.palm"
cfg_obj_names = "obj.names"
cfg_obj_data = "obj.data"

negative_images = True  #treate images with no xml files as negative images
numBatch = 24
numSubdivision = 3
darknetEcec = "/home/digits/works/darknet/darknet"

#---------------------------------------------------------------------

if not os.path.exists(saveYoloPath):
    os.makedirs(saveYoloPath)

def downloadPretrained(url):
    import wget
    print("Downloading the pretrained model darknet53.conv.74, please wait.")
    wget.download(url)

def transferYolo( xmlFilepath, imgFilepath, labelGrep=""):
    global imgFolder

    img_file, img_file_extension = os.path.splitext(imgFilepath)
    img_filename = basename(img_file)
    yoloFilename = os.path.join(saveYoloPath ,img_filename + ".txt")

    if(xmlFilepath is not None or negative_images is False):
        #print(imgFilepath)
        img = cv2.imread(imgFilepath)
        imgShape = img.shape
        #print (img.shape)
        img_h = imgShape[0]
        img_w = imgShape[1]

        labelXML = minidom.parse(xmlFilepath)
        labelName = []
        labelXmin = []
        labelYmin = []
        labelXmax = []
        labelYmax = []
        totalW = 0
        totalH = 0
        countLabels = 0

        tmpArrays = labelXML.getElementsByTagName("filename")
        for elem in tmpArrays:
            filenameImage = elem.firstChild.data

        tmpArrays = labelXML.getElementsByTagName("name")
        for elem in tmpArrays:
            labelName.append(str(elem.firstChild.data))

        tmpArrays = labelXML.getElementsByTagName("xmin")
        for elem in tmpArrays:
            labelXmin.append(int(elem.firstChild.data))

        tmpArrays = labelXML.getElementsByTagName("ymin")
        for elem in tmpArrays:
            labelYmin.append(int(elem.firstChild.data))

        tmpArrays = labelXML.getElementsByTagName("xmax")
        for elem in tmpArrays:
            labelXmax.append(int(elem.firstChild.data))

        tmpArrays = labelXML.getElementsByTagName("ymax")
        for elem in tmpArrays:
            labelYmax.append(int(elem.firstChild.data))


    with open(yoloFilename, 'a') as the_file:
        if(xmlFilepath is not None or negative_images is False):
            i = 0
            for className in labelName:
                if(className==labelGrep or labelGrep==""):
                    classID = classList[className]
                    x = (labelXmin[i] + (labelXmax[i]-labelXmin[i])/2) * 1.0 / img_w 
                    y = (labelYmin[i] + (labelYmax[i]-labelYmin[i])/2) * 1.0 / img_h
                    w = (labelXmax[i]-labelXmin[i]) * 1.0 / img_w
                    h = (labelYmax[i]-labelYmin[i]) * 1.0 / img_h

                    the_file.write(str(classID) + ' ' + str(x) + ' ' + str(y) + ' ' + str(w) + ' ' + str(h) + '\n')
                    i += 1

        else:
            the_file.write('')

    the_file.close()

#---------------------------------------------------------------
fileCount = 0

print("Step 1. Transfer VOC dataset to YOLO dataset.")
if(negative_images is True):
    print("If there is no xml with same names for the images, those images will be treated as negative images.")

for file in os.listdir(imgFolder):
    filename, file_extension = os.path.splitext(file)
    file_extension = file_extension.lower()

    if(file_extension == ".jpg" or file_extension==".png" or file_extension==".jpeg" or file_extension==".bmp"):
        imgfile = os.path.join(imgFolder ,file)
        xmlfile = os.path.join(xmlFolder ,filename + ".xml")

        if(os.path.isfile(xmlfile)):
            #print("id:{}".format(fileCount))
            #print("processing {}".format(imgfile))
            #print("processing {}".format(xmlfile))
            fileCount += 1

            transferYolo( xmlfile, imgfile, "")
            copyfile(imgfile, os.path.join(saveYoloPath ,file))

        elif(negative_images is True):
            transferYolo( None, imgfile, "")
            copyfile(imgfile, os.path.join(saveYoloPath ,file))

print("        {} images transered.".format(fileCount))
# step2 ---------------------------------------------------------------
fileList = []
outputTrainFile = cfgFolder + "/train.txt"
outputTestFile = cfgFolder + "/test.txt"

print("Step 2. Create YOLO cfg folder and split dataset to train and test datasets.")
if not os.path.exists(cfgFolder):
    os.makedirs(cfgFolder)

for file in os.listdir(saveYoloPath):
    filename, file_extension = os.path.splitext(file)
    file_extension = file_extension.lower()

    if(file_extension == ".jpg" or file_extension==".jpeg" or file_extension==".png" or file_extension==".bmp"):
        fileList.append(os.path.join(saveYoloPath ,file))

testCount = int(len(fileList) * testRatio)
trainCount = len(fileList) - testCount

a = range(len(fileList))
test_data = random.sample(a, testCount)
#train_data = random.sample(a, trainCount)
train_data = [x for x in a if x not in test_data]

with open(outputTrainFile, 'a') as the_file:
    for i in train_data:
        the_file.write(fileList[i] + "\n")

the_file.close()

with open(outputTestFile, 'a') as the_file:
    for i in test_data:
        the_file.write(fileList[i] + "\n")

the_file.close()

print("        Train dataset:{} images".format(len(train_data)))
print("        Test dataset:{} images".format(len(test_data)))

# step2 -------------------------------------------

print("Step 3. Generate data & names files under "+cfgFolder+ " folder, and update YOLO config file.")

classes = len(classList)

if not os.path.exists(os.path.join(cfgFolder ,"weights")):
    os.makedirs(os.path.join(cfgFolder ,"weights"))
    print("all weights will generated in here: " + os.path.join(cfgFolder ,"weights"))

with open(os.path.join(cfgFolder ,cfg_obj_data), 'w') as the_file:
    the_file.write("classes= " + str(classes) + "\n")
    the_file.write("train  = " + os.path.join(cfgFolder ,"train.txt") + "\n")
    the_file.write("valid  = " + os.path.join(cfgFolder ,"test.txt") + "\n")
    the_file.write("names = " + os.path.join(cfgFolder ,"obj.names") + "\n")
    the_file.write("backup = " + os.path.join(cfgFolder ,"weights"))

the_file.close()

with open(os.path.join(cfgFolder ,cfg_obj_names), 'w') as the_file:
    for className in classList:
        the_file.write(className + "\n")

the_file.close()

# step4 ----------------------------------------------------

print("Step 4. Start to train the YOLO model.")

if not os.path.exists("darknet53.conv.74"):
    downloadPretrained("https://pjreddie.com/media/files/darknet53.conv.74")

classNum = len(classList)
filterNum = (classNum + 5) * 3

if(modelYOLO == "yolov3"):
    fileCFG = "yolov3.cfg"

else:
    fileCFG = "yolov3-tiny.cfg"

with open(os.path.join("cfg",fileCFG)) as file:
    file_content = file.read()

file.close

file_updated = file_content.replace("{BATCH}", str(numBatch))
file_updated = file_updated.replace("{SUBDIVISIONS}", str(numSubdivision))
file_updated = file_updated.replace("{FILTERS}", str(filterNum))
file_updated = file_updated.replace("{CLASSES}", str(classNum))

file = open(os.path.join(cfgFolder,fileCFG), "w")
file.write(file_updated)
file.close

executeCmd = darknetEcec + " detector train " + os.path.join(cfgFolder,"obj.data") + " " \
    + os.path.join(cfgFolder,fileCFG) + " darknet53.conv.74"

print("        please copy and paste to run the darknet training command below:")
print("          " + executeCmd)
print("")
print("        after training, you can find all the weights files here:" + os.path.join(cfgFolder ,"weights"))

time.sleep(3)
#call(executeCmd.split())
