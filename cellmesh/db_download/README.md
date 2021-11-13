# CellMeSH 

### Contents <a id='contents'></a>

* <a href='#intro'>Introduction</a>
* <a href='#db_sql'>Download CellMeSH database (SQL format)</a>
* <a href='#db_excel'>Download CellMeSH database (Excel format)</a>
* <a href='#use_db'>Usage of CellMeSH database</a>  

---

### Introduction <a id='intro'></a>

Here we provide CellMeSH dabase in SQL format and Excel format for downloading.

The database is conceptually a collection of tables, each of which is for one species and has rows as genes and columns as cell types,
and each pair of gene and cell type refers to a list of publications each of which is indexed with the gene and the cell type.

---

### Download CellMeSH database (SQL format)  <a id='db_sql'></a>

You can download the CellMeSH database in SQL format from [cellmesh.db.gz](https://github.com/shunfumao/cellmesh/blob/master/cellmesh/db_download/cellmesh.db.gz).

The database in SQL format has three tables:

[1] Table 'cell\_name': contains columns of 'cellID' (text), 'cellName' (text) and 'cellIndex' (integer). 'cellID' refers to the MeSH ontology ID, 'cellName' refers to the MeSH cell type, and 'cellIndex' refers to the index of the cell type among the total 570 MeSH cell types. For example, we can have a row ('D001078', 'APUD Cells', 40), meaning the cell type 'APUD Cells' has MeSH ontology ID 'D001078' and is the 40th cell type in MeSH ontology.

[2] Table 'gene\_info': contains columns of 'gene' (text), 'geneID' (integer), 'totalCounts' (integer) and 'taxid' (text). 'gene' refers to gene symbol, 'geneID' refers to the NCBI gene ID, 'totalCounts' refers to the number of publications where the gene occurs, and 'taxid' refers to species. For example, we can have a row ('ND6', 6775063, 500, '63221'), meaning the gene 'ND6' has NCBI gene ID 6775063 and taxid '63221' (Homo sapiens neanderthalensis), and has been indexed in 500 publications.

[3] Table 'cell\_gene': contains columns of 'cellID' (text), 'gene' (text), 'count' (integer), 'tfidf' (real), 'pmids' (text) and 'taxid' (text). Here 'cellID' and 'gene' and 'taxid' have same meaning as in tables 'cell\_name' and 'gene\_info'. 'pmids' (and 'count') refers to the list (and number) of publications where the gene and the cell co-occur, 'tfidf' is the weight adjustment for the 'count'. For example, we can have a row ('D000050', 'XKR3', 1, 0.2, '16431037', '9606'), meaning that the gene 'XKR3' (with taxid '9606') and the cell type with MeSH ID 'D000050' co-occur in one publication with PMID '16431037', and the adjust weight is 0.2.


---

### Setup <a id='setup'></a>

CellMeSH has been tested under Ubuntu 16.04. Please follow the below three steps to setup:

###### Step 1
Download CellMeSH.
```
$ git clone https://github.com/shunfumao/cellmesh.git
```

###### Step 2
At the root directory of CellMeSH, run setup.py
```
$ python setup.py install
```

###### Step 3
Verification. The following bash and Python codes will help you see the CellMeSH database address in Python site-packages, if setup is successful.

```
$ cd ~/  # try any location other than the cellmesh root dir
$ python
>>> from cellmesh.db import DB_DIR
>>> print(DB_DIR)
```

---

### Usage of CellMeSH Database <a id='use_db'></a>

The CellMeSH database is constructed by linking the cell type and gene information from the indexed literature resources of MEDLINE Medical Subject Headings (MeSH) terms and Gene2pubmed. It currently supports the species of human, mouse, and worm, and shall work best for human and mouse datasets.

###### Example 1
Check the cell type information from CellMeSH database. 
```
import os
from cellmesh.db import get_all_cell_id_names
    
db_file='/home/user/cellmesh/cellmesh/data/cellmesh.db'  # assume db stored here

results = get_all_cell_id_names(db_dir=db_file)
```
The results will contain a list of (MeSH cell type ID, MeSH cell type).

To see how the results look like, please try:
```
$ python -m unittest cellmesh.test.TestDB.test_get_all_cell_id_names
```

The full example is in [cellmesh_root_dir]/cellmesh/test.py (test_get_all_cell_id_names). 

###### Example 2
Check the cell type information from CellMeSH database. 
```
import os
from cellmesh.db import get_all_genes
    
db_file='/home/user/cellmesh/cellmesh/data/cellmesh.db'  # assume db stored here

results = get_all_genes(
  db_dir=db_file,
  species='human')
```
The results will contain a list of specy-specific (e.g. here human) genes.

To see how the results look like, please try:
```
$ python -m unittest cellmesh.test.TestDB.test_get_all_genes
```

The full example is in [cellmesh_root_dir]/cellmesh/test.py (test_get_all_genes). 

###### Example 3
Check the co-occurring genes (and pubmed articles) for a particular cell type in the CellMeSH database. 
```
import os
from cellmesh.db import get_all_genes_pmids
    
db_file='/home/user/cellmesh/cellmesh/data/cellmesh.db'  # assume db stored here

cell_id = 'D000069261'  # Podosomes
results = get_cell_genes_pmids(
  cell=cell_id, 
  db_dir=db_file, 
  species='human')
```
The results will contain a list of (gene co-occuring with the cell, pubmed article ids where the cell and gene co-occur, count of such pubmed articles).

To see how the results look like, please try:
```
$ python -m unittest cellmesh.test.TestDB.test_get_cell_genes_pmids
```

The full example is in [cellmesh_root_dir]/cellmesh/test.py (test_get_cell_genes_pmids). 


### Usage of Probabilistic Query Method<a id='use_prob'></a>
The Probabilistic Query Method is based on maximum likelihood estimation. It tries to estimate the probability of seeing the marker genes if the candidate cell is the true one. It can be independently used with other databases. 

###### Example 1
Calculate the probabilistic query score. 

In this example, the query cell has 3 marker genes. From the database (may not be CellMeSH database), we know the id (can be anything, depending on the database and how you'll use the id) and co-occurring genes of a candidate cell. We also know the number of all possible genes (e.g. 27322). We can feed these information into calc_prob_one_query_one_cell function, and get a score to see how likely this particular candidate cell is with the query cell.
```
from cellmesh.query import calc_prob_one_query_one_cell

query_genes = ['CD79A', 'MS4A1', 'CD79B']
cell_id = 'D001402'
cell_gene_count = [('CD79A', 187), ('MS4A1', 12), ('POLM', 4), ('CCR2', 10)]
overlapping_genes = ['CD79A', 'MS4A1']  # between query_genes and cell_gene_count (e.g. co-occurring genes of the candidate cell)
params = {'alpha': None}  # 0 to 1, default is None (e.g. 0.5)
N_all_genes = 27322

args = (query_genes, cell_id, cell_gene_count, overlapping_genes, params, N_all_genes)
result = calc_prob_one_query_one_cell(args)
```
The results will contain (cell_id, score).

To see how the results look like, please try:
```
$ python -m unittest cellmesh.test.TestQuery.test_calc_prob_one_query_one_cell
```

The full example is in [cellmesh_root_dir]/cellmesh/test.py (test_calc_prob_one_query_one_cell). 


### Usage of Probabilistic Query Method + CellMeSH DB <a id='use_both'></a>

The probabilistic query and CellMeSH DB can be used together, which achieved best performance in our experiments.

###### Example 1
We have 15 marker genes of a query cell (which is B cell). The below codes illustrate how we can use the probabilistic query method (prob_test) to query the CellMeSH database (db_file) for its most likely cell types. 

We need to set some parameters. Particularly, the 'n_proc' indicates the number of processes to speedup computation via Python multiprocessing, and the species with respect to the dataset.

```
import os
from cellmesh.query import prob_test

db_file='/home/user/cellmesh/cellmesh/data/cellmesh.db'  # assume db stored here

# Top 15 genes for B cell in Tabula Muris Droplet dataset
query_genes = ['CD79A','MS4A1','CD79B','TNFRSF13C','BANK1', 'CR2','CD19','CD37','CD22','FCRL1', 'FCRLA','CD74','LTB','BLK','POU2AF1']

query_params = {
 'n_proc': 1,  # num of proc >= 1
 'db_cnt_thre': 3,
 'alpha': None}

cell_prob_vals = prob_test(
  genes=query_genes,
  params=query_params,
  db_dir=db_file,
  species='mouse')
```
The result will contain a list of (MeSH cell ID, MeSH cell type, log likelihood score, a list of overlapping genes, a dic with key as overlapping gene and value as a list of corresponding pubmed article ids), ranked in descending order with respect to the log likelihood score.

To see how the results look like, please try:
```
python -m unittest cellmesh.test.TestQuery.test_prob_test
```
The full example is in [cellmesh_root_dir]/cellmesh/test.py (test_calc_prob_one_query_one_cell). 
