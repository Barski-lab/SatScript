#!/usr/bin/env python3
import os
import sys
import argparse
import tempfile
import shutil
from saturation.utils import (normalize_args, export_to_file, get_macs_command_line, parse_outputs, save_plot)


def get_parser():
    parser = argparse.ArgumentParser(description='SatScript', add_help=True)
    parser.add_argument("-b", "--bam",        type=str, help="Path to the BAM file",   required=True)
    parser.add_argument("-m", "--macs",       type=str, help="Path to the MACS2 log file", required=True)
    parser.add_argument("-o", "--output",     type=str, help="Output filename prefix", default="./")
    parser.add_argument("-s", "--suffix",     type=str, help="Output suffixes for reads, islands, surface, frip and saturation files", nargs=5,
                                              default=["reads.png", "islands.png", "surface.png", "frip.png", "saturation.txt"])
    parser.add_argument("-p", "--percentage", type=str, help="Target percentage", nargs="*", default=["25", "50", "75", "90", "95", "98", "99", "99.5", "100"])
    parser.add_argument("-t", "--temp",       type=str, help="Temp folder", default=".")
    parser.add_argument("-r", "--resolution", type=int, help="Output picture resolution, dpi", default=85)
    return parser


def export_results(args, output_data):

    percent = [line[0] for line in output_data]
    total_mapped = [line[1] for line in output_data]
    macs2_reads = [line[2] for line in output_data]
    islands = [line[3] for line in output_data]
    surface = [line[4] for line in output_data]
    frip_score = [line[5] for line in output_data]

    save_plot(filename=args.output + args.suffix[0],
              res_dpi=args.resolution,
              title="Reads",
              x_data=percent,
              y_data=[total_mapped, macs2_reads],
              labels=["Total mapped reads", "Reads used by MACS"],
              styles=["ro-", "bo-"],
              axis=["%", "reads"])

    save_plot(filename=args.output + args.suffix[1],
              res_dpi=args.resolution,
              title="Islands",
              x_data=percent,
              y_data=[islands],
              labels=["islands"],
              styles=["bo-"],
              axis=["%", "islands"])

    save_plot(filename=args.output + args.suffix[2],
              res_dpi=args.resolution,
              title="Surface",
              x_data=percent,
              y_data=[surface],
              labels=["surface"],
              styles=["bo-"],
              axis=["%", "surface, bp"])

    save_plot(filename=args.output + args.suffix[3],
              res_dpi=args.resolution,
              title="Fraction of Reads in Peaks",
              x_data=percent,
              y_data=[frip_score],
              labels=["FRIP Score"],
              styles=["bo-"],
              axis=["%", "FRIP Score"])

    export_to_file(args.output + args.suffix[4], "\n".join([" ".join(map(str, line)) for line in output_data]))


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)
    args = normalize_args(args, ["percentage", "suffix", "output", "resolution"])

    print(args)
    macs_command_line = get_macs_command_line(args.macs)
    temp_folder = tempfile.mkdtemp(prefix=os.path.join(args.temp, "tmp_"))
    try:
        output_data = []

        for target_percent in args.percentage:
            randsample_output = os.path.join(temp_folder, target_percent + ".bed")
            callpeak_output = os.path.join(temp_folder, target_percent)
            bedmap_output = os.path.join(temp_folder, target_percent + "_reads_at_peaks.txt")

            randsample_cmd = " ".join(["macs2", "randsample", "-t", args.bam, "-p", target_percent, "-o", randsample_output])
            print("Run:", randsample_cmd)
            os.system(randsample_cmd)

            callpeak_cmd = " ".join(["macs2", macs_command_line, "-t", randsample_output, "-n", callpeak_output])
            print("Run:", callpeak_cmd)
            os.system(callpeak_cmd)

            bedmap_cmd = " ".join(["bedmap --fraction-ref 1 --count", randsample_output, callpeak_output + "_peaks.broadPeak", "| paste -s -d+ - | bc > ", bedmap_output])
            print("Run:", bedmap_cmd)
            os.system(bedmap_cmd)

            result = parse_outputs(xlsfile=callpeak_output + "_peaks.xls",
                                   bedmap_output=bedmap_output,
                                   target_percent=target_percent)

            output_data.append(result)

        export_results(args, output_data)

    except Exception as err:
        print("Error", err)
        raise
    finally:
        shutil.rmtree(temp_folder)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))