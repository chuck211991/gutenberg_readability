from settings import FEATURE_CSV, PICKLE_FILE
import csv
import pickle
from nltk import cluster
from nltk.cluster import euclidean_distance
from numpy import array
from score.get_gold_standard import *
from process.index import all_functions
import itertools
import sys

def cluster_things(keys_to_use, gold_standard="normal", make_pickle=False):
	# Open the CSV file
	vectors = []
	gold_filter = []
	with open(FEATURE_CSV, 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			row_values = []
			gold_filter += [int(row['book_id'])]
			for key in row:
				if key != 'book_id' and key in keys_to_use:
					row_values += [float(row[key])]
			vectors += [row_values]
	gold_clusters = []
	if gold_standard == "normal":
		gold_clusters = get_gold_standard(gold_filter)
	else:
		gold_clusters = get_kincaid_cluster(gold_filter)
	vectors = [array(f) for f in vectors]
	clusterer = cluster.KMeansClusterer(len(gold_clusters), euclidean_distance)
	clusters = clusterer.cluster(vectors, True) 
	if make_pickle == True:
		pickle.dump(clusterer, open(PICKLE_FILE, 'w'))

	# Attempt to classify the things again, so we know which vector they belong to
	results = []
	for i in range(0, len(gold_clusters)):
		results += [[]]
	with open(FEATURE_CSV, 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			row_values = []
			for key in row:
				if key != 'book_id' and key in keys_to_use:
					row_values += [float(row[key])]
			results[clusterer.classify([array(f) for f in row_values])] += [row]

	book_ids = []
	for i, c in enumerate(results):
		t = []
		for row in c:
			t += [int(row['book_id'])]
		book_ids += [t]
	# Open the source files and find the correct things
	return score_clusters(gold_clusters, book_ids)


def score_clusters(guess, gold):
	def find_matches(source, destination):
		source_matches = []
		for cluster in source:
			best_match = 0
			best_match_set = []
			cluster_size = len(cluster)
			for d_cluster in destination:
				intersection = list(set(cluster) & set(d_cluster))
				intersection_c = float(len(intersection))/cluster_size
				if intersection_c > best_match:
					best_match = intersection_c
					best_match_set = intersection
			source_matches += [best_match]
		return float(sum(source_matches))/len(source_matches), source_matches
	precision, p_matches = find_matches(guess, gold)
	recall, f_matches = find_matches(gold, guess)
	f_score = 2*(precision*recall)/(precision+recall)
	return f_score, recall, precision

# Stolen from http://stackoverflow.com/questions/464864/python-code-to-pick-out-all-possible-combinations-from-a-list
from itertools import chain, combinations
def all_subsets(ss):
  return chain(*map(lambda x: combinations(ss, x), range(0, len(ss)+1)))

if __name__ == "__main__":
	for combo in all_subsets(all_functions.keys()):
		if len(combo) == 0:
			continue
		try:
			f_score, recall, precision = cluster_things(combo, 'kincaid')
			print "%s,%s,%s,%s" % (f_score, recall, precision, "+".join(combo))
			sys.stdout.flush()
		except Exception as ex:
			#print "Caught exception {}".format(ex)
			pass
