# CellMeSH 

### Contents <a id='contents'></a>

* <a href='#intro'>Introduction</a>
* <a href='#db_sql'>Download CellMeSH database (SQL format)</a>
* <a href='#db_sql_use'>Usage of CellMeSH database (SQL format)</a>
* <a href='#db_excel'>Download CellMeSH database (Excel format)</a>  

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

### Usage of CellMeSH Database <a id='db_sql_use'></a>

The CellMeSH database is constructed by linking the cell type and gene information from the indexed literature resources of MEDLINE Medical Subject Headings (MeSH) terms and Gene2pubmed. It currently supports the species of human, mouse, and worm, and shall work best for human and mouse datasets.

Before using the database, make sure to install CellMeSH as described [here](https://github.com/shunfumao/cellmesh#setup).

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

---

### Download CellMeSH database (Excel format)  <a id='db_excel'></a>

You can download the CellMeSH database in Excel format for human from [cellmesh_human.xlsx](https://github.com/shunfumao/cellmesh/blob/master/cellmesh/db_download/cellmesh_human.xlsx) and for mouse from [cellmesh_mouse.xlsx](https://github.com/shunfumao/cellmesh/blob/master/cellmesh/db_download/cellmesh_mouse.xlsx).

Each excel file contains a table where rows are genes and columns are cell types, and each pair of gene and cell type is the number of publications the gene and the cell type co-occur. The excel files contain information that is part of the SQL format database.



