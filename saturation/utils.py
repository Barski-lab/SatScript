#!/usr/bin/env python3
import os
import argparse


def open_file(filename):
    lines = []
    with open(filename, 'r') as infile:
        for line in infile:
            if line.strip():
                lines.append(line.strip())
    return lines


def export_to_file (output_filename, data):
    with open(output_filename, 'w') as output_file:
        output_file.write(data)


def get_macs_command_line(macs_log, exclude_args=["-t", "-n", "-f"]):
    skip = False
    macs_command = []
    for item in list(filter(lambda line: "Command line:" in line, open_file(macs_log)))[0].split(":")[1].strip().split():
        if item in exclude_args and not skip:
            skip = True
        elif skip:
            skip = False
        else:
            macs_command.append(item)
    return " ".join(macs_command)


def parse_macs_log(xlsfile, target_percent):
    ttags, ftags, islands_n, islands_len, istart = 0, 0, 0, 0, 0
    result = [target_percent]
    for line in open_file(xlsfile):
        if "# total tags in treatment" in line:
            ttags = line.split(":")[1].strip()
        elif "# tags after filtering in treatment" in line:
            ftags = line.split(":")[1].strip()
        elif ("#" not in line) and ("start" not in line) and (istart != int(line.strip().split()[1])):
            islands_n = islands_n + 1
            istart = int(line.strip().split()[1])
            islands_len = islands_len + int(line.strip().split()[2]) - istart
    result.extend([ttags, ftags, islands_n, islands_len])
    return result


def normalize_args(args, skip_list=[]):
    normalized_args = {}
    for key,value in args.__dict__.items():
        if key not in skip_list:
            normalized_args[key] = value if not value or os.path.isabs(value) else os.path.normpath(os.path.join(os.getcwd(), value))
        else:
            normalized_args[key]=value
    return argparse.Namespace (**normalized_args)
