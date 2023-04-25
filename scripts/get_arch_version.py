#!/usr/bin/env python3



import os, sys
import pickle


def get_arch(iid, scratch_dir):
    image_data = f"{scratch_dir}/{iid}/image_data"
    with open(image_data, "r") as f:
        lines = f.readlines()

    arch = lines[1].strip("\n")
    return arch

def read_fs_qemu_data(fl):
    result = []
    with open(fl, "rb") as f:
        temp = pickle.load(f)
    return temp[-1]

def read_qemu_data(iid, fs_out_dir):
    fs_data_file = f"{cu.loaded_mods_path}/{iid}/{iid}_ups_subs.pkl"
    qemu_data = read_fs_qemu_data(fs_data_file)
    return qemu_data

def main():
    iid = sys.argv[1]
    scratch_dir = sys.argv[2]
    fs_out_dir = sys.argv[3]
    fs_script_dir = sys.argv[4]
    
    sys.path.append(fs_script_dir)
    globals()["cu"] = __import__("custom_utils")

    qemu_data = read_qemu_data(iid, fs_out_dir)
    arch = get_arch(iid, scratch_dir)

    if "mips" in arch:
        print(arch)
    elif "armelv6" in arch:
        print(arch)
    else:
        if "versatile" in qemu_data["machine"]:
            print("armel")
            return
        if qemu_data["machine"] == "realview-pb-a8":
            print("armelv7_2")
        else:
            print("armelv7")

if __name__ == "__main__":
    main()
