import os
import sqlite3
import pdb

PATH = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(PATH, 'data', 'cellmesh.db')

SPECIES_MAP = {
  'mus_musculus': 10090,
  'mouse': 10090,
  'homo_sapiens': 9606,
  'human': 9606,
  'worm': 6239,
  'c_elegans': 6239
}

def get_metainfo(db_dir=DB_DIR):
  print('get_metainfo')
  conn = sqlite3.connect(db_dir)
  C = conn.cursor()

  # structure for sqlite_master
  # for row in conn.execute("pragma table_info('sqlite_master')").fetchall():
  #   print(row)
  
  # tables for cellmesh
  # results = conn.execute("SELECT name from sqlite_master WHERE type='table'").fetchall()
  # for row in results:
  #   print(row)

  tables = ['cell_gene', 'cell_name', 'gene_info']
  for table in tables:
    print("table %s has structure:"%table)
    for row in conn.execute("pragma table_info('%s')"%table).fetchall():
      print(row)

    print("examples:")
    if table=='cell_gene':
      results = conn.execute("SELECT * FROM %s WHERE count <5"%table)
    else:
      results = conn.execute("SELECT * FROM %s"%table)

    i = 0
    for row in results:
      if i==5: break
      print(row)
      i+=1

    print("")

  conn.close()
 
  return

def get_all_cell_id_names(
  db_dir=DB_DIR, 
  include_cell_components=True, 
  include_chromosomes=False, 
  include_cell_lines=False,
  ):
  """
  Get all (cell_id, cell_name) from the CellMeSH database.

  Input:
    db_dir:
      SQL database file. Default is cellmesh/data/cellmesh.db
    include_cell_components:
      False to filter cell types under cell components. Default is True. 
    include_chromosomes:
      False to filter cell types under chromosomes. Default is False.
    include_cell_lines:
      False to filte cell types under cell lines. Default is False.

  Output:
    results: a list of all unique cell ids + names - tuple (cell_id, cell_name)
  """
  conn = sqlite3.connect(db_dir)
  C = conn.cursor()
  C.execute('SELECT DISTINCT cellID, cellName FROM cell_name')
  results = C.fetchall()
  
  if not include_cell_components:
    with open(os.path.join(PATH, 'data', 'cell_component_ids.txt')) as f:
      cell_components = set(x.strip() for x in f.readlines())
      results = [x for x in results if x[0] not in cell_components]
  if not include_chromosomes:
    with open(os.path.join(PATH, 'data', 'chromosome_ids.txt')) as f:
      chromosomes = set(x.strip() for x in f.readlines())
      results = [x for x in results if x[0] not in chromosomes]
  if not include_cell_lines:
    with open(os.path.join(PATH, 'data', 'cell_line_ids.txt')) as f:
      cell_lines = set(x.strip() for x in f.readlines())
      results = [x for x in results if x[0] not in cell_lines]

  conn.close()
  return results

def get_all_genes(db_dir=DB_DIR, species='human', uppercase_names=True):
  """
  Get all gene symbols (specy specific) from the CellMeSH database.

  Input:
    db_dir:
      SQL database file. Default is cellmesh/data/cellmesh.db
    species:
      Specify the species of the genes. Default is human genes.
    uppercase_names:
      Whether to convert gene names to capital letters . Default is True.

  Output:
    results: a list of all unique gene symbols.
  """
  conn = sqlite3.connect(db_dir)
  C = conn.cursor()
  taxid = SPECIES_MAP[species]
  C.execute('SELECT DISTINCT gene FROM gene_info WHERE taxid=?', (taxid,))
  results = C.fetchall()
  conn.close()
  if uppercase_names:
    return [x[0].upper() for x in results]
  else:
    return [x[0] for x in results]

def get_cell_genes_pmids(
  cell, 
  db_dir=DB_DIR, 
  species='homo_sapiens', 
  threshold=3, 
  uppercase_gene_names=True,
  ):
  """
  Given a cell ID, this returns a list of all genes associated with that cell.
  The threshold is the minimum count for the gene to be included.

  Input:
    cell:
      MeSH Cell ID, whose co-occurring genes we hope to get
    db_dir:
      SQL database file. Default is cellmesh/data/cellmesh.db
    species:
      Specify the species of the genes. Default is 'homo_sapiens' (or 'human') genes. 
    threshold:
      Minimum count for the gene to be included (considered as co-occurring with cell).
      Default is 3.
    uppercase_gene_names:
      Whether to convert gene names to capital letters. Default is True.

  Output:
    results: a list of (gene, a string of related pmids seperated by ',', co-occurring count)

  For example,
    If cell='D000071182' (e.g. 'Autophagosomes'), we could get a list similar to below:
    [('ATG16L1', '29133525,27758042,27490928,27875067', 4),
     ('ATG9A', '27758042,27510922,27070082,29180427,28522593', 5),
     ...]
  """
  conn = sqlite3.connect(db_dir)
  C = conn.cursor()

  statement = 'SELECT gene, pmids, count FROM cell_gene WHERE cellID=? AND taxid=?'
  taxid = SPECIES_MAP[species]
  C.execute(statement, (cell, taxid))
  results = C.fetchall()
  results = [x for x in results if x[2] > threshold]
  conn.close()

  if uppercase_gene_names:
    results = [(x[0].upper(),) + x[1:] for x in results]
    
  return results

def write_csv(
  db_dir=DB_DIR,
  species='human'):
  '''
  Dump SQL db to a redundant csv file:
  -       -        -             <cell_id> ...
  -       -        -             <cell_name> ...
  <taxid> <geneid> <gene_symbol> <cnt>
  '''
  # get cell info
  conn = sqlite3.connect(db_dir)
  C = conn.cursor()
  C.execute('SELECT DISTINCT cellID, cellName FROM cell_name')
  cell_list = C.fetchall() # a list of (cell_id, cell_name)
  sorted(cell_list, key=lambda x: x[0])
  pdb.set_trace()

  # get gene info
  taxid = SPECIES_MAP[species]
  C.execute('SELECT DISTINCT taxid, geneID, gene FROM gene_info WHERE taxid=?', (taxid,))
  gene_list = C.fetchall() # a list of (taxid, geneID, gene)
  sorted(gene_list, key=lambda x: x[1])
  pdb.set_trace()

  # get gene, cell counts
  C.execute('SELECT gene, cellID, count FROM cell_gene WHERE taxid=?', (taxid,))
  g_c_list = C.fetchall() # a list of (gene/UPPER CASE, cell_id, count)
  g_c_dic = {}
  for gene, cellID, count in g_c_list:
    g_c_dic[(gene.upper(), cellID)] = count
  pdb.set_trace()

  # write
  with open('tmp.csv', 'w') as fo:
    hd = ',,,'
    for cell_id, _ in cell_list:
      hd += cell_id + ','
    hd += '\n'
    fo.write(hd)

    hd = ',,,'
    for _, cell_name in cell_list:
      hd += cell_name + ','
    hd += '\n'
    fo.write(hd)

    idx = 0
    for taxid, gene_id, gene in gene_list:
        gene = gene.upper()
        row = '%s,%s,%s,'%(taxid, gene_id, gene)
        
        print('%d / %d'%(idx, len(gene_list)))
        idx+=1
        
        for cell_id, _ in cell_list:
            count = g_c_dic.get((gene, cell_id), 0)
            if count > 0:
                row += '%s,'%str(count)
                # pdb.set_trace()
            else:
                row += '0,'
        row += '\n'
        fo.write(row)
    # pdb.set_trace() # end for
    print('csv written')

  return
