#!/usr/bin/env python3
import os
import sys
import argparse
import tempfile
import shutil
from saturation.utils import (normalize_args, export_to_file, get_macs_command_line, parse_macs_log)


def get_parser():
    parser = argparse.ArgumentParser(description='SatScript', add_help=True)
    parser.add_argument("-b", "--bam",        type=str, help="Path to the BAM file",   required=True)
    parser.add_argument("-m", "--macs",       type=str, help="Path to the MACS2 log file", required=True)
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