import pysam
import glob
import os

from time import time
from time import sleep
import subprocess
import multiprocessing as mp

import argparse


################### ---- Reference files ---- ####################

human_ref = "route/to/directory"
mitochondria_ref = "route/to/directory"


################### ---- Reference files ---- ####################

#

################### ---- option input ---- ####################

option = argparse.ArgumentParser(description="nanopore pipeline options")

option.add_argument("files", metavar="fast5files", nargs="+", help="Specify the fast5 files directly, i.e. excecute this script in the right folder and select files using <runname>")
option.add_argument("--outdir","-o", dest="outdir", help="specify output directory for analysis", default="poo")
option.add_argument("--type", "-t", dest="readtype", choices=["2D", "fw", "rev", "all"], help="Specify read type to be analyzed", default="2D")
option.add_argument("--correct", "-c", dest="readcorrection", choices=["Correct", "NoCorrect"], help="Specify wether reads should be corrected utilizing nanocorrect", default="NoCorrect")
option.add_argument("--mapping", "-m",  dest="mapping", choices=["lastal", "lastal-analyse", "graphmap-lin", "graphmap-cir"], help="Specify the read mapper", default="lastal")

option= vars(option.parse_args())

###### DIT MOET IK NOG AANPASSEN, ALS IK HET GOED DOE HEB IK DEZE PAAR REGELS NIET NODIG #####

outdir = option["outdir"]
mapping = option["mapping"]
readtype = option["readtype"]
readcorrection = option["readcorrection"]

################### ---- option input ---- ####################

#

################### ---- check input ---- ####################

#

def check_input():
	f5count = 0 
	for item in option["files"]:
		if not os.path.isfile(item):
			print "Fast5 files not properly supplied"+item
			return False
		else:
			f5count += 1 
	print f5count, "Fast5 files correctly specified"
			
	
	if not os.path.exists(option["outdir"]):
		os.makedirs(option["outdir"])
		return True
	else:
		print "output directory already exists, please try again with new output directory name" 
		return False

################### ---- check input ---- ####################

#

################### ---- main pipeline ---- ####################

def main_pipeline():

# fasta and fastq file extraction
	os.makedirs(outdir/Fasta_Fastq)
	poretools stats --type 
	poretools fastq	--type option["readtype"] > outdir/Fasta_Fastq/outdir_Fastq
	poretools fasta --type option["readtype"] > outdir/Fasta_Fastq/outdir_Fasta











################### ---- start phrases ---- ####################



print "checking argument input"

print "readtype = "+ readtype
print "mapping = "+mapping
print "readcorrection = "+ readcorrection

if __name__ == "__main__":
	if check_input():
		print "starting nanopore raw data analysis"
		main_pipeline()
	else:
		print("ERROR in command line input")



################### ---- start phrases ---- ####################



