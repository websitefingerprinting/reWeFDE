from statsmodels.distributions.empirical_distribution import ECDF
import argparse
import dill
import os
import numpy as np
def load_pkl(f):
	with open(f,'rb') as fi:
		info = dill.load(fi)
	return info 
def parse_args():
	"""
	Parse command line arguments.

	Returns
	-------
	Namespace
		a namespace containing the parsed command line arguments

	"""
	parser = argparse.ArgumentParser("Generate the x and y of ECDF.")
	parser.add_argument('-dir', 
						type=str, required=True)
	parser.add_argument('-o', '--output',
						type=str, required=False, default=None)
	return parser.parse_args()
if __name__ == '__main__':
	args = parse_args()
	inputdir = args.dir
	filename = inputdir.split("/")[-2]+"_ecdf.dat"
	if args.output is None:
		outputdir = os.path.join(os.path.dirname(inputdir),filename)
	else:
		outputdir = os.path.join(args.output,filename)
	info = load_pkl(inputdir)
	ecdf = ECDF(info)
	with open(outputdir,'w') as f:
		for x, y in zip(ecdf.x, ecdf.y):
			if x== -np.inf:
				x = 0
			f.write("{:.8f}\t{:.8f}\n".format(x,y))
	
	print("Output to {}".format(outputdir))
