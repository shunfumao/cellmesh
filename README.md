# CellMesSH 

### Contents <a id='contents'></a>

* <a href='#intro'>Introduction</a>
* <a href='#pub'>Publication</a>
* <a href='#setup'>Setup</a>
* <a href='#use_db'>Usage of CellMeSH Database</a>  
* <a href='#use_prob'>Usage of Probabilistic Query Method</a>  
* <a href='#use_both'>Usage of Probabilistic Query Method + CellMeSH DB</a>  

---

### Introduction <a id='intro'></a>

CellMeSH is a framework to identify the cell types of the query cells based on their marker genes.

CellMeSH has three parts: 
  (1) [webserver](http://uncurl-app.yjzhang.com:8888/db_query)
  (2) a novel database
  (3) a probabilistic method to query the database.

In this Github site, we aim to open source its database and the probabilistic query method, in order to assist the community efforts on automating the cell type identification.

CellMeSH has also been integrated into [the Uncurl-App project](http://uncurl-app.yjzhang.com:8888), with the optimized codes [here](https://github.com/yjzhang/cellmesh).

---

### Publication <a id='pub'></a>

If you find CellMeSH is helpful, we appreciate your citation of its intial [version](https://) first:

Shunfu Mao, Yue Zhang, Georg Seelig, and Sreeram Kannan. CellMeSH: Probabilistic Cell-Type Identification Using Indexed Literature.

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
from cellmesh.db import get_all_genes
    
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