#!/usr/bin/env python3

import os,sys,pickle
import subprocess
import traceback

extra_bad_modules = []

def get_subs(image):
    pickle_file = f"{cu.loaded_mods_path}{image}/{image}_ups_subs.pkl"
    subs = []
    
    try:
        info = cu.read_pickle(pickle_file)
        subs = info[1]
    except:
        print(traceback.format_exc())

    return subs

def get_bad_modules(bad_mod_path):

    with open(bad_mod_path,"rb") as f:
        bad_mods = pickle.load(f)

    return bad_mods


def find_mod(mod,image_dir,m_type):
    
    result = ""
    try:
        res = subprocess.check_output("find {0} -name {1}".format(image_dir,mod),shell=True)
    except Exception as e:
        print(e)
        print("Could not find the module...",mod)
    
    output = res.decode("utf-8").split("\n")
    print (output)
    print("\n")
    if len(output) > 1 and m_type == "custom":
        for mod in output:
            if "upstream" in mod:
                continue
            result = mod
            break
    else:
        result = output[0]

    return result

def sub_mods(distrib_path, upstream_path):
    try:
        cmd = "sudo cp {0} {1}".format(upstream_path, distrib_path)
        res = subprocess.call(cmd,shell=True)
    except Exception as e:
        print(e)
        print("Could not substitute module",mod)

def delete_modules(bad_mods, image_dir,m_type):

    for mod in bad_mods:
        mod_path = find_mod(mod,image_dir,m_type)
        if mod_path == "":
            continue
        print("Bad module",mod_path,"Type",m_type)
        try:
            res = subprocess.call("sudo rm "+ mod_path,shell=True)
        except Exception as e:
            print(e)
            print("Could not delete module",mod_path)

if __name__ == "__main__":
    image = sys.argv[1]
    image_dir = sys.argv[2]
    firmsolo_dir = sys.argv[3]

    sys.path.append(firmsolo_dir)
    # Import the custom utils
    globals()["cu"] = __import__("custom_utils")

    upstream_dir = image_dir + "/upstream/"
    
    print("Image", image, "Image dir", image_dir)
    bad_custom_mod_path =f"{cu.loaded_mods_path}{image}/crashed_modules_ups_subs.pkl"
    bad_upstream_mod_path = f"{cu.loaded_mods_path}{image}/crashed_modules_upstream_ups_subs.pkl"
    timedout_custom_mod_path = f"{cu.loaded_mods_path}{image}/timed_out.pkl"
    timedout_upstream_mod_path = f"{cu.loaded_mods_path}/timed_out_upstream.pkl"
    bad_mods_shipped = []
    bad_mods_native = []
    bad_mods = []
    
    try:
        bad_mods_shipped = get_bad_modules(bad_custom_mod_path)
    except:
        print ("No bad shipped modules yet")
    
    try:
        bad_mods_native = get_bad_modules(bad_upstream_mod_path)
    except:
        print ("No bad native modules yet")
    
    try:
        timedout_shipped = get_bad_modules(timedout_custom_mod_path)
        bad_mods_shipped += timedout_shipped
    except:
        print ("No timed out shipped modules yet")
    
    try:
        timedout_mods_native = get_bad_modules(timedout_upstream_mod_path)
        bad_mods_native += timedout_mods_native
    except:
        print ("No timedout native modules yet")

    print ("Distributed crashed modules")
    print (bad_mods_shipped)
    delete_modules(bad_mods_shipped, image_dir, "custom")

    print ("Upstream crashed modules")
    print (bad_mods_native)
    delete_modules(bad_mods_native,upstream_dir,"upstream")
    
    
    subs = get_subs(image)
    for sub in subs:
        tmp1 = sub[0].split("/")
        del tmp1[0]
        sub[0] = "/".join(tmp1)
        tmp2 = sub[1].split("/")
        del tmp2[0]
        sub[1] = "/".join(tmp2)
        custom_path = image_dir + sub[0]
        upstream_path = image_dir + sub[1].replace("/home/","/upstream/")
        module = sub[2]
        print("Substituting module",module)
        sub_mods(custom_path,upstream_path)

