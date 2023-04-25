#!/usr/bin/env python3


import os,sys
import subprocess
import traceback



if __name__ == "__main__":

    ### Get the firmadyne dir, the image kernel, mips version, and the image dir

    firmadyne = sys.argv[1]
    kern_path = sys.argv[2]
    arch = sys.argv[3]
    image_dir = sys.argv[4]
    scratch_dir = sys.argv[5]
        
    binaries_path = firmadyne + "/firmsolo_binaries/"
    binaries_path_old = firmadyne + "/binaries/"

    kernel = kern_path.split("/")[-1]
    
    res = ""
    
    cmd0 = 'file {0}/bin/busybox | grep "rel2"'.format(image_dir)
    try:
        res = subprocess.check_output(cmd0,shell=True).decode("utf-8")
    except:
        pass
    
    print("Arch", arch, "Kernel", kernel)
    
    if arch == "mipseb" or arch == "mipsel":
        if res == "":
            vers = "I"
        else:
            vers = "II"
    
        if vers == "I":
            if arch == "mipsel":
                version = "r1_mipsel"
            else:
                version= "r1_mips"
        else:
            if arch == "mipsel":
                version = "r2_mipsel"
            else:
                version= "r2_mips"
        
    if kernel < "linux-2.6.32":
        if "armel" not in arch:
            fl = "mips_old"
        else:
            fl = "armel"
    else:
        if "armel" not in arch:
            fl = "mips_new"
        else:
            fl = "armel"
    
    if "armel" not in arch:
        print("Saving MIPS data to image dir")
        with open(image_dir + "../image_data","w") as f:
            f.write(vers+"\n")
            f.write(arch+"\n")
            f.write(kernel+"\n")
    if "armel" in arch:
        print("Saving ARM data to image dir")
        with open(image_dir + "../image_data","w") as f:
            f.write("None\n")
            f.write(arch+"\n")
            f.write(kernel+"\n")
    
    if "armel" not in arch:
        cmd1 = "cp {0}/console/{3}/console_{1} {2}/firmadyne/console".format(binaries_path,version,image_dir,fl)

        print("Console",cmd1)
        subprocess.run(cmd1,shell=True)

        cmd2 = "cp {0}/libnvram/{3}/libnvram.so_{1} {2}/firmadyne/libnvram.so".format(binaries_path,version,image_dir,fl)

        print("Libnvram",cmd2)
        subprocess.run(cmd2,shell=True)
    else:
        if arch == "armelv6":
            binaries_path = binaries_path_old
            fl = "armel"

        cmd1 = "cp {0}/console.{2} {1}/firmadyne/console".format(binaries_path,image_dir,fl)

        print("Console",cmd1)
        subprocess.run(cmd1,shell=True)

        cmd2 = "cp {0}/libnvram.so.{2} {1}/firmadyne/libnvram.so".format(binaries_path,image_dir,fl)

        print("Libnvram",cmd2)
        subprocess.run(cmd2,shell=True)
