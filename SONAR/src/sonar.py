#!/usr/bin/env python
import pandas as pd
from optparse import OptionParser
import networkx as nx
import numpy as np
import multiprocessing as mp
import os
import sys
#sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
#from SONAR.get_PPI_feature_mat_NewRBPlist_v4 import get_PPI_features
#from SONAR.generate_RCS_score_table import get_scores_for_allprot_via_cvTesting_oversampled
from SONAR.src.get_PPI_feature_mat_NewRBPlist_v4 import get_PPI_features
from SONAR.src.generate_RCS_score_table import get_scores_for_allprot_via_cvTesting_oversampled
def main(options):
    G=nx.read_edgelist(options.Edgelist)
    f=open(options.RBPlist)
    RBP_set=set(f.read().split('\n'))
    f.close()
    prot_set=set(G.nodes())
    pool=mp.Pool(processes=options.processes)
    print "We are extracting PPI features..."
    result=[pool.apply_async(get_PPI_features, args=(prot, G, RBP_set,)) for prot in prot_set]
    results=[p.get() for p in result]
    PPI_feature_table=pd.DataFrame(results).set_index('Protein_name')
    PPI_feature_table.to_csv(options.PPI_feature_table, index=True, sep='\t')
    print "Feature table, done!"
    Xy_df=PPI_feature_table[['primary_RBP_ratio', 'secondary_RBP_ratio', 'tertiary_RBP_ratio', 'RBP_flag']]
    Score_df=pd.DataFrame(index=Xy_df.index)
    Score_df['sum_of_scores']=0
    Score_df['counts']=0
    Score_df['RBP_flag']=Xy_df['RBP_flag']
    print "We are constructing SONAR and calculate RCS scores..."
    avg_Score_df=get_scores_for_allprot_via_cvTesting_oversampled(Xy_df, 'RBP_flag', Score_df)
    avg_Score_df.to_csv(options.outfile, sep='\t', index=True)
    print "Score table, done!"
    print "The program has finished successfully."

#if __name__=='__main__':
def call_main():
    usage="""\n./dist/run_SONAR -e filename -r filename [-p num_processes] [--outfile_feature_table feature_table_filename] [-o score_table_filename] [-R num_repeats]""" 
    description="""Run SONAR with your PPI network edge list and RBP annotation list. This program will give you the RCS score table which contains the classification scores for all the proteins appearing in the PPI network. The immediate result (feature table generated in the process) will also be presented."""
    parser= OptionParser(usage=usage, description=description)
    #parser.add_option("-h", "--help", action="help")
    parser.add_option('-e', '--Edge_list', dest='Edgelist', help='The file that store the PPI network in the format of edge-list. Please refer to the format of the edge-list file in folder Demo', metavar='FILE')
    parser.add_option('-r', '--RBP_list', dest='RBPlist', help='A text file that store', metavar='FILE')
    parser.add_option('-p', '--processes', dest='processes', type='int', default=4, help='The number of processes you wanna start for this program', metavar='num_processes')
    parser.add_option('--outfile_feature_table', dest='PPI_feature_table', help='', default='./PPI_feature_table.xls', metavar='FILE')
    parser.add_option('-o', '--outfile', dest='outfile', default='./SONAR_score_table.txt', help='The output of the program which contains the SONAR scores for each proteins', metavar='FILE')
    parser.add_option('-R', '--Repeats', dest='repeats', help='The times to repeat when caluculating the SONAR scores.', type='int', default=10, metavar='INT') 
#    parser.add_option('', '', dest='', help='', metavar='')
    (options, args)=parser.parse_args()
    if not options.Edgelist:
        parser.error("-e/--Edge_list must be specified.")
    if not options.RBPlist:
        parser.error("-r/--RBP_list must be specified.")    
 
    print("Start SONAR program!\nThis program may take several hours, please be patient.")
    main(options)

if __name__=='__main__':
    call_main()