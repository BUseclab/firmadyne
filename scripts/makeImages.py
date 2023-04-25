#!/usr/bin/env python3


import os,sys
import subprocess as sb
### You should change this to the directory where FirmSolo is installed
import traceback
import argparse


### Change these depending on where firmadyne is installed 
mkImageScript="/firmadyne/scripts/makeImage.sh"
work_dir = "/output/"


def read_pickle(file_path):
    with open(file_path,"rb") as f:
        result = pickle.load(f)
    return result


class Image:
    def __init__(self,image_id):
        self.id = image_id
        self.mode = "ups_subs"
        self.endianess = "mipsel"

    def get_image_info(self):
        info = cu.get_image_info(self.id, "all")
        
        return info
        
    def makeImage(self):
        print ("Creating fs for image {0}".format(self.id))
        try:
            cmd = "{0} {1} {2} {3}".format(mkImageScript,self.id,self.mode,self.endianess)
            res = sb.call(cmd,shell=True)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
    
    def find_endianess(self):
        
        info = self.get_image_info()
        arch,endianess,vermagic = info["arch"], info["endian"], info["vermagic"]
        
        if arch == "mips":
            if endianess == "little endian":
                self.endianess = "mipsel"
            else:
                self.endianess = "mipseb"
        elif arch == "arm":
            if "ARMv5" in vermagic:
                self.endianess = "armel"
            if "ARMv6" in vermagic:
                self.endianess = "armelv6"
            if "ARMv7" in vermagic:
                self.endianess = "armelv7"
        else:
            self.endianess = ""

        return

def main():
    parser = argparse.ArgumentParser(description='Create a Firmadyne image that supports loading kernel modules')
    parser.add_argument('-i', '--image_id',help='The ID of the image')
    parser.add_argument('-f', '--firmsolo_dir',help='Absolute path to FirmSolo')
    
    res = parser.parse_args()
    image = res.image_id
    firmsolo_dir = res.firmsolo_dir
    
    sys.path.append(firmsolo_dir)
    # Import custom utils
    globals()["cu"] = __import__("custom_utils")

    img = Image(image)
    img.find_endianess()
    img.makeImage()

if __name__ == "__main__":
    main()
