#!/usr/bin/env python3
import os
import sys
import argparse
import tempfile
import shutil


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


def get_parser():
    parser = argparse.ArgumentParser(description='SatScript', add_help=True)
    parser.add_argument("-b", "--bam",        type=str, help="Path to the BAM file",   required=True)
    parser.add_argument("-m", "--macs",       type=str, help="Path to the MACS2 file", required=True)
    parser.add_argument("-f", "--file",       type=str, help="Output filename. If not absolute, resolve relative to the current directory", default="Satur.txt")
    parser.add_argument("-p", "--percentage", type=str, help="Target percentage", nargs="*", default=["25", "50", "75", "90", "95", "98", "99", "99.5", "100"])
    parser.add_argument("-t", "--temp",       type=str, help="Temp folder", default=".")
    return parser


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)
    args = normalize_args(args, ["percentage"])

    macs_command_line = get_macs_command_line(args.macs)
    temp_folder = tempfile.mkdtemp(prefix=os.path.join(args.temp, "tmp_"))
    try:
        output_data = []
        for target_percent in args.percentage:
            rand_sample_output = os.path.join(temp_folder, target_percent + ".bam")
            call_peak_output = os.path.join(temp_folder, target_percent)
            os.system(" ".join(["macs2", "randsample", "-t", args.bam, "-p", target_percent, "-o", rand_sample_output]))
            os.system(" ".join(["macs2", macs_command_line, "-t", rand_sample_output, "-n", call_peak_output]))
            result = parse_macs_log(call_peak_output + "_peaks.xls", target_percent)
            output_data.append(result)
        output_data = "\n".join([" ".join(map(str, line)) for line in output_data])
        export_to_file(args.file, output_data)
    except Exception as err:
        print("Error", err)
        raise
    finally:
        shutil.rmtree(temp_folder)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))