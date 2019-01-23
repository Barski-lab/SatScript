#!/usr/bin/env python3
import os
import argparse
import matplotlib.pyplot as plt


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


def parse_outputs(xlsfile, bedmap_output, target_percent):
    ttags, ftags, islands_n, islands_len, frip_score, istart = 0, 0, 0, 0, 0, 0
    result = [float(target_percent)]
    for line in open_file(xlsfile):
        if "# total tags in treatment" in line:
            ttags = int(line.split(":")[1].strip())
        elif "# tags after filtering in treatment" in line:
            ftags = int(line.split(":")[1].strip())
        elif ("#" not in line) and ("start" not in line) and (istart != int(line.strip().split()[1])):
            islands_n = islands_n + 1
            istart = int(line.strip().split()[1])
            islands_len = islands_len + int(line.strip().split()[2]) - istart
    for line in open_file(bedmap_output):
        frip_score = float(line) / ttags * 100 if ttags != 0 else 0
    result.extend([ttags, ftags, islands_n, islands_len, frip_score])
    return result


def normalize_args(args, skip_list=[]):
    normalized_args = {}
    for key,value in args.__dict__.items():
        if key not in skip_list:
            normalized_args[key] = value if not value or os.path.isabs(value) else os.path.normpath(os.path.join(os.getcwd(), value))
        else:
            normalized_args[key]=value
    return argparse.Namespace (**normalized_args)


def save_plot(filename, x_data, y_data, styles, labels, axis, res_dpi=100, title="", padding=[5, 5], x_max=None, y_max=None):
    x_max = x_max if x_max else max(x_data)
    y_max = y_max if y_max else max([max(y_data_line) for y_data_line in y_data])
    x_pad = 0.01 * padding[0] * x_max
    y_pad = 0.01 * padding[1] * y_max

    handles = []
    for data_combined in zip(y_data, styles, labels):
        current_handle, = plt.plot(x_data, data_combined[0], data_combined[1], label=data_combined[2], mfc='none')
        handles.append(current_handle)

    plt.title(title)
    plt.xlabel(axis[0])
    plt.ylabel(axis[1])
    plt.legend(handles=handles)
    plt.axis([0 - x_pad, x_max + x_pad, 0 - y_pad, y_max + y_pad])
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 3))
    plt.savefig(filename, bbox_inches='tight', dpi=res_dpi)
    plt.close('all')



