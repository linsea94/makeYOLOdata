import os

#-------------------------------------------------------------
classes = 5

#Same with you defined in 1_labels_to_yolo_format.py
classList = {"person_in_bike":0, "person":1, "bicycle": 2, "car":3, "motorcycle":4}
cfgFolder = "/home/amr-server/yolo_ws/src/YOLO_data/YOLO_parkinglot_1000/cfg"

#-------------------------------------------------------------

cfg_obj_names = "obj.names"
cfg_obj_data = "obj.data"

pathCFG = os.path.join(cfgFolder, "weights")
if not os.path.exists(pathCFG):
    os.makedirs(pathCFG)
    print("all weights will generated in here: ", pathCFG)


with open(os.path.join(cfgFolder, cfg_obj_data), 'w') as the_file:
    the_file.write("classes= " + str(classes) + "\n")
    the_file.write("train  = " + os.path.join(cfgFolder ,"train.txt") + "\n")
    the_file.write("valid  = " + os.path.join(cfgFolder ,"test.txt") + "\n")
    the_file.write("names = " + os.path.join(cfgFolder ,"obj.names") + "\n")
    the_file.write("backup = " + os.path.join(cfgFolder ,"weights") + "/")

the_file.close()

print("and cfg folder: " + pathCFG + " ,is ready for training.")

with open(os.path.join(cfgFolder ,cfg_obj_names), 'w') as the_file:
    for className in classList:
        the_file.write(className + "\n")

the_file.close()

