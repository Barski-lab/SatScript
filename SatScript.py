#!/usr/bin/env python3

from optparse import OptionParser
import  os, sys, shutil

def getCMDline(macslog): #getting command line from a log file
    ifh=open(macslog,"r")
    for line in ifh:
        if "Command line:" in line:
            line.split(":")[1]
            break
    ifh.close()    
    return line.split(":")[1]

def parseMACSout(xlsfile): #parsing macs2 output NAME_peaks.xls file to return number of reads (total and used), number of islands and area covered by islands
    ifh= open(xlsfile, "r")
    islandsN=0
    islandsLen=0
    Istart=0
    
    for line in ifh:
        if "# total tags in treatment" in line: 
        
            ttags =line.split(":")[1].strip()
            break
    for line in ifh:
        if "# tags after filtering in treatment" in line: 
            ftags =line.split(":")[1].strip()
            break
        
    for line in ifh:
        if "#" in line: 
            continue
        
        if "start" in line:
            continue
        if Istart==int(line.strip().split()[1]):
            continue
        islandsN = islandsN+1
        Istart=int(line.strip().split()[1])
        islandsLen=islandsLen+int(line.strip().split()[2])-Istart
        
    result=[ttags,ftags,islandsN,islandsLen]
    ifh.close()    
    return  result






argv=sys.argv
parser = OptionParser()
parser.add_option("-b", "--bamfile", action="store", type="string",
                  dest="bamfile", help="aligned bam file", metavar="<file>")

(opt, args) = parser.parse_args(argv)
if len(argv) < 2:
    parser.print_help()
    sys.exit(1)

#parameters

Spoints=[25,50,75,90,95,98,99,99.5, 100]  #data points for which coverage will be calculated


bfilename=os.path.basename(opt.bamfile)
os.chdir(os.path.dirname(opt.bamfile))
    
soutput=[]
#getting BWs MACS command from log file and removing -t, -f and -w parameters
MACSlogfile=opt.bamfile.split(".")[0]+"_macs.log"
BwMacsCmd= getCMDline(MACSlogfile).strip().split()
t_ind=BwMacsCmd.index("-t")
n_ind=BwMacsCmd.index("-n")
f_ind=BwMacsCmd.index("-f")
BwMacsCmd[t_ind]=""
BwMacsCmd[t_ind+1]=""
BwMacsCmd[n_ind]=""
BwMacsCmd[n_ind+1]=""
BwMacsCmd[f_ind]=""
BwMacsCmd[f_ind+1]=""
BwMacsCmdline= " ".join(BwMacsCmd)
#print (BwMacsCmdline)


if not os.path.exists("./Saturation"):
    os.makedirs("./Saturation")
        
for spoint in Spoints:
    rsbamname=str(spoint*100)+"per" + bfilename
    cmd="macs2 randsample -t " + opt.bamfile +" -p " + str(spoint)+ " -o ./Saturation/" + rsbamname
    #print (cmd)
    os.system(cmd)
    
    cmd2="macs2 " + BwMacsCmdline + " -t ./Saturation/" + rsbamname + " -n ./Saturation/" + str(spoint*100)+"per"
    #print (cmd2)
    os.system(cmd2)
    
    result= parseMACSout("./Saturation/"+str(spoint*100)+"per_peaks.xls") 
    result.insert(0,str(spoint))
    soutput.append(result)
    
#print(soutput)
with open("Satur.txt", "w") as f:
    for lst in soutput:
        a=" ".join(map(str,lst))
        a=a+"\n"
        f.write (a)
        
shutil.rmtree("./Saturation")
#-b /wardrobe/RAW-DATA/uFF5830F-112C-0922-E5B5-C4569770AAF3/uFF5830F-112C-0922-E5B5-C4569770AAF3.bam
