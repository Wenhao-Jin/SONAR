#!/bin/bash
sonar -p 16 -r ./RBP_merged_list.txt -e ./BioPlex_interactionList_v4_edgelist.txt --outfile_feature_table=BioPlex_PPI_feature_table.xls -o SONAR_score_table_BioPlex_human.xls 
