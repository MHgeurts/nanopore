import pysam
import glob
import os
import sys
import shutil

# from time import time
import subprocess
import argparse



#------------------------- subprocess directories ------------------------#

poretools = "/usr/local/bin/poretools" 
nanocorrectssss = "/usr/local/bin/nanocorrect" 


#------------------------- Reference files -------------------------#

human_ref = "route/to/directory"
mitochondria_ref = "route/to/directory"


#------------------------- option input -------------------------#

option = argparse.ArgumentParser(description="nanopore pipeline options")

option.add_argument("--inputdir", "-i", dest="indir", help="Specify the directory containing the fast5 files for analyzation directly")
option.add_argument("--name", "-name", dest="name", help="Specify the runname")
option.add_argument("--outdir","-o", dest="outdir", help="specify output directory for analysis", default="poo")
option.add_argument("--type", "-t", dest="readtype", choices=["2D", "fw", "rev", "all"], help="Specify read type to be analyzed", default="2D")
option.add_argument("--correct", "-c", dest="readcorrection", choices=["Correct", "NoCorrect"], help="Specify wether reads should be corrected utilizing nanocorrect", default="NoCorrect")
option.add_argument("--mapping", "-m",  dest="mapping", choices=["lastal", "lastal-analyse", "graphmap-lin", "graphmap-cir"], help="Specify the read mapper", default="lastal")
option = vars(option.parse_args())

###### DIT MOET IK NOG AANPASSEN, ALS IK HET GOED DOE HEB IK DEZE PAAR REGELS NIET NODIG #####

outdir = option["outdir"]
mapping = option["mapping"]
readtype = option["readtype"]
readcorrection = option["readcorrection"]
fast5dir = option["indir"] 

#------------------------- check input -------------------------#


def check_input():
	f5count = 0 
	dircount = 0
	if len(glob.glob1(option["indir"], "*.fast5")) == 0:
		print "No fast5 files in input directory, please specify correct input directory"
		return False
	else:
		print len(glob.glob1(option["indir"], "*.fast5")), "fast5 files in input directory specified for analysis"
	
	while os.path.exists(option["outdir"]):
		dircount +=1
		option["outdir"] = option["outdir"]+"."+str(dircount)
		print "output directory already exists and will be respecified"
	else:
		print "output directory:"+option["outdir"]
		os.makedirs(option["outdir"])
		return True 

#------------------------- read correction -------------------------#

def correction():
	subprocess.call(["git", "clone", "https://github.com/jts/nanocorrect"])
	subprocess.call(["make", "-f", "nanocorrect-overlap.make", "INPUT=../"+fastafile, "NAME="+option["name"]], cwd="nanocorrect")
	subprocess.call(["python", "nanocorrect.py", option["name"], "all"], stdout=open(option["outdir"]+"/Fasta_fastQ"+"/corrected"+option["name"]+".fasta", "w+"), cwd="nanocorrect")
	shutil.rmtree("nanocorrect")
	
	return True
	

#------------------------- main pipeline -------------------------#

def main_pipeline():
# fasta and fastq file extraction
	os.makedirs(option["outdir"]+"/Fasta_fastQ")
	fastafile = option["outdir"]+"/Fasta_fastQ"+"/"+option["name"]+".fasta"
	subprocess.call(["poretools","stats","--type", option["readtype"] , "fast5/"])
	subprocess.call(["poretools","fasta","--type", option["readtype"] , "fast5/"], stdout=open(fastafile, "w+"))
	subprocess.call(["poretools","fastq","--type", option["readtype"] , "fast5/"], stdout=open(option["outdir"]+"/Fasta_fastQ"+"/"+option["name"]+".fastq", "w+"))
	
	
	if option["readcorrection"] == "NoCorrect":
		pass
	else:
		correction()
		# make sure the corrected file is used in subsequent analysis
		fastafile = option["outdir"]+"/Fasta_fastQ"+"/corrected_"+option["name"]+".fasta"


	

	
	
	


#------------------------- start phrases -------------------------#

if __name__ == "__main__":
	print "checking argument input"
	if check_input():
		main_pipeline()
		
	else: 
		print("ERROR in command line input")



#------------------------- start phrases -------------------------#






