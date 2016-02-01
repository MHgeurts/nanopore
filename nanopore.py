# import pysam
import fileinput
import glob
import os
import sys
import shutil

import subprocess
import argparse



#------------------------- subprocess directories ------------------------#

poretools = "/usr/local/bin/poretools" 
nanocorrectssss = "/usr/local/bin/nanocorrect" 


#------------------------- Reference files -------------------------#

human_ref = "/data/references/human_GATK_GRCh37/GRCh37_gatk.fasta"
mitochondria_ref = "route/to/directory"


#------------------------- option input -------------------------#

option = argparse.ArgumentParser(description="nanopore pipeline options")

option.add_argument("--indir", "-i", 	dest="indir", help="Specify the directory containing the fast5 files for analyzation directly")
option.add_argument("--outdir","-o", 	dest="outdir", help="specify output directory for analysis", default="poo")
option.add_argument("--type", "-t", 	dest="readtype", choices=["2D", "all"], help="Specify read type to be analyzed", default="all")
option.add_argument("--correct", "-c", 	dest="readcorrection", choices=["Correct", "NoCorrect"], help="Specify wether reads should be corrected utilizing nanocorrect", default="NoCorrect")
option.add_argument("--mapping", "-m",  	dest="mapping", choices=["lastal", "graphmap-lin", "graphmap-cir"], help="Specify the read mapper", default="lastal")
option.add_argument("-ref" , "-r", 	dest="refference", help="specify refference genome for mapping", default="human_ref")

option = vars(option.parse_args())
outdir = option["outdir"]
mapping = option["mapping"]
readtype = option["readtype"]
readcorrection = option["readcorrection"]
reference = option["refference"]


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
	subprocess.call(["make", "-f", "nanocorrect-overlap.make", "INPUT=../"+fastafile, "NAME="+option["outdir"]], cwd="nanocorrect")
	subprocess.call(["python", "nanocorrect.py", option["outdir"], "all"], stdout=open(option["outdir"]+"/Fasta_fastQ"+"/corrected"+option["outdir"]+".fasta", "w+"), cwd="nanocorrect")
	shutil.rmtree("nanocorrect")
	
	return True
	

#------------------------- main pipeline -------------------------#

def main_pipeline():
	#initial run analysis
	os.makedirs(option["outdir"]+"/run_logs")
	subprocess.call(["poretools","stats","--type", option["readtype"] ,option["indir"]])
	subprocess.call(["poretools","stats","--type", option["readtype"] ,option["indir"]], stdout=open(option["outdir"]+"/run_logs"+"/run_stats.txt", "w+"))
	#subprocess.call(["poretools","hist",option["indir"]], stdout=open(option["outdir"]+"/run_logs"+"/read_distribution.pdf", "w+"))
	#subprocess.call(["poretools",option["indir"]], stdout=open(option["outdir"]+"/run_logs"+"/occupancy.pdf", "w+"))

	#create file structure for nanook
	os.makedirs(option["outdir"]+"/Fasta")
	os.makedirs(option["outdir"]+"/fasta")
	os.makedirs(option["outdir"]+"/fasta"+"/Template")
	os.makedirs(option["outdir"]+"/fasta"+"/Complement")
	os.makedirs(option["outdir"]+"/fasta"+"/2D")
	os.makedirs(option["outdir"]+"/mapping")
	if option["readtype"] == "2D":
		subprocess.call(["poretools","fasta","--type", "2D" , option["indir"]], stdout=open(option["outdir"]+"/Fasta"+"/all_2d.fasta", "w+"))
		subprocess.call(["nanook_split_fasta", "-i", option["outdir"]+"/Fasta"+"/all_2d.fasta", "-o", option["outdir"]+"/fasta"+"/2D"])
	else:
		subprocess.call(["poretools","fasta","--type", "2D" , option["indir"]], stdout=open(option["outdir"]+"/Fasta"+"/all_2d.fasta", "w+"))
		subprocess.call(["poretools","fasta","--type", "fwd" , option["indir"]], stdout=open(option["outdir"]+"/Fasta"+"/all_template.fasta", "w+"))
		subprocess.call(["poretools","fasta","--type", "rev" , option["indir"]], stdout=open(option["outdir"]+"/Fasta"+"/all_complement.fasta", "w+"))
		subprocess.call(["nanook_split_fasta", "-i", option["outdir"]+"/Fasta"+"/all_2d.fasta", "-o", option["outdir"]+"/fasta"+"/2D"])
		subprocess.call(["nanook_split_fasta", "-i", option["outdir"]+"/Fasta"+"/all_template.fasta", "-o", option["outdir"]+"/fasta"+"/Template"])
		subprocess.call(["nanook_split_fasta", "-i", option["outdir"]+"/Fasta"+"/all_complement.fasta", "-o", option["outdir"]+"/fasta"+"/Complement"])
	subprocess.call(["nanook", "align", "-s", option["outdir"], "-r" ,human_ref])
	subprocess.call(["nanook", "analyse", "-s", option["outdir"], "-r" ,human_ref])
	two_d = glob.glob(option["outdir"]+"/last"+"/2D"+"/*.maf")
	with open(option["outdir"]+"/last"+"/merged_2D_last.maf", "w+") as files_1:
		lines = fileinput.input(two_d)
		files_1.writelines(lines)
	complement = glob.glob(option["outdir"]+"/last"+"/Complement"+"/*.maf")
	with open(option["outdir"]+"/last"+"/merged_complement_last.maf", "w+") as files_1:
		lines = fileinput.input(complement)
		files_1.writelines(lines)
	template= glob.glob(option["outdir"]+"/last"+"/Template"+"/*.maf")
	with open(option["outdir"]+"/last"+"/merged_template_last.maf", "w+") as files_1:
		lines = fileinput.input(template)
		files_1.writelines(lines)
	merged = glob.glob(option["outdir"]+"/last"+"/*.maf")
	with open(option["outdir"]+"/mapping"+"/merged_lastal.maf", "w+") as files_1:
		lines=fileinput.input(merged)
		files_1.writelines(lines)
	os.makedirs(option["outdir"]+"/nanook_data_files")
	os.makedirs(option["outdir"]+"/analysis_graphs")
	shutil.move(option["outdir"]+"/logs", option["outdir"]+"/nanook_data_files")
	shutil.move(option["outdir"]+"/last", option["outdir"]+"/mapping")
	shutil.move(option["outdir"]+"/latex", option["outdir"]+"/analysis_graphs")
	shutil.move(option["outdir"]+"/graphs", option["outdir"]+"/analysis_graphs")
	shutil.move(option["outdir"]+"/analysis", option["outdir"]+"/nanook_data_files")
	shutil.rmtree(option["outdir"]+"/fasta")

	#
	
	os.makedirs(option["outdir"]+"/bam_sam")
	subprocess.call(["maf-convert", "sam", option["outdir"]+"/mapping"+"/merged_lastal.maf"], stdout=open(option["outdir"]+"/bam_sam"+"/sam_files.sam", "w+"))
	subprocess.call(["samtools", "view", "-t", human_ref+".fai", "-h", "-bS", option["outdir"]+"/bam_sam"+"/sam_files.sam" ], stdout=open(option["outdir"]+"/bam_sam"+"/bam_files.bam", "w+"))
	subprocess.call(["samtools", "sort", option["outdir"]+"/bam_sam"+"/bam_files.bam", option["outdir"]+"/bam_sam"+"/bam_files.sorted"])
	subprocess.call(["samtools", "index", option["outdir"]+"/bam_sam"+"/bam_files.sorted.bam"])
	
	
	
	

	

	
	#if option["readcorrection"] == "NoCorrect":
	#	if option["mapping"] == "lastal":
			#create datastructure expected by nanook-analysis
	#		pass
	#else:
	#	correction()
		# make sure the corrected file is used in subsequent analysis
	#	fastafile = option["outdir"]+"/fasta"+"/corrected_"+option["outdir"]+".fasta"

	
	
	

#------------------------- start phrases -------------------------#

if __name__ == "__main__":
	print "checking argument input"
	if check_input():
		main_pipeline()
		
	else: 
		print("ERROR in command line input")



#------------------------- start phrases -------------------------#






