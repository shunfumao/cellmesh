import unittest

class TestDB(unittest.TestCase):

  def test_get_all_cell_id_names(self):
    """
    usage: python -m unittest cellmesh.test.TestDB.test_get_all_cell_id_names
    """
    import os
    from cellmesh.db import get_all_cell_id_names
    
    PATH = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = os.path.join(PATH, 'data', 'cellmesh.db')
    print('database:\n' + DB_DIR)
    
    results = get_all_cell_id_names(
      db_dir=DB_DIR, 
      include_cell_components=True, 
      include_chromosomes=False, 
      include_cell_lines=False)
    print('first 5 (cell id, cell name):\n' + str(results[0:5]))
    return

  def test_get_all_genes(self):
    """
    usage: python -m unittest cellmesh.test.TestDB.test_get_all_genes
    """
    import os
    from cellmesh.db import get_all_genes
    
    PATH = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = os.path.join(PATH, 'data', 'cellmesh.db')
    print('database:\n' + DB_DIR)

    results = get_all_genes(
      db_dir=DB_DIR,
      species='human',
      uppercase_names=True)
    print('first 5 genes:\n' + str(results[0:5]))
    return

  def test_get_cell_genes_pmids(self):
    """
    usage: python -m unittest cellmesh.test.TestDB.test_get_cell_genes_pmids
    """
    import os
    from cellmesh.db import get_cell_genes_pmids
    
    PATH = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = os.path.join(PATH, 'data', 'cellmesh.db')
    print('database:\n' + DB_DIR)

    cell_id = 'D000069261'  # Podosomes
    results = get_cell_genes_pmids(
      cell=cell_id, 
      db_dir=DB_DIR, 
      species='human', 
      threshold=3, 
      uppercase_gene_names=True)
    print('cell \'Podosomes\' has \'human\'genes:\n' + str(results))
    return

  def test_get_metainfo(self):
    """
    usage: python -m unittest cellmesh.test.TestDB.test_get_metainfo
    """
    import os
    from cellmesh.db import get_metainfo
    
    PATH = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = os.path.join(PATH, 'data', 'cellmesh.db')
    print('database:\n' + DB_DIR)

    get_metainfo()
    return

  def test_write_csv(self):
    """
    usage: python -m unittest cellmesh.test.TestDB.test_write_csv
    """
    import os
    from cellmesh.db import write_csv 
    
    PATH = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = os.path.join(PATH, 'data', 'cellmesh.db')
    print('database:\n' + DB_DIR)

    write_csv(DB_DIR, 'mouse' )
    return

class TestQuery(unittest.TestCase):

  def test_calc_prob_one_query_one_cell(self):
    """
    usage: python -m unittest cellmesh.test.TestQuery.test_calc_prob_one_query_one_cell
    """
    from cellmesh.query import calc_prob_one_query_one_cell
    
    print('----- Input -----')
    genes = ['CD79A', 'MS4A1', 'CD79B']
    print('genes:')
    print(genes)

    cell_id = 'D001402'
    print('cell_id:')
    print(cell_id)

    cell_gene_count = [('CD79A', 187), ('MS4A1', 12), ('POLM', 4), ('CCR2', 10)]
    print('cell_gene_count:')
    print(cell_gene_count)

    overlapping_genes = ['CD79A', 'MS4A1']
    print('overlapping_genes:')
    print(overlapping_genes)

    params = {'alpha': None}
    print('params:')
    print(params)

    N_all_genes = 27322
    print('N_all_genes:')
    print(N_all_genes)

    args = (genes, cell_id, cell_gene_count, overlapping_genes, params, N_all_genes)
    print('\n----- Run calc_prob_one_query_one_cell -----\n')
    result = calc_prob_one_query_one_cell(args)

    print('----- Output -----')
    print('(cell_id, prob_score):')
    print(result)
    return

  def test_prob_test(self):
    """
    usage: python -m unittest cellmesh.test.TestQuery.test_prob_test
    """
    import os
    from cellmesh.query import prob_test
    
    PATH = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = os.path.join(PATH, 'data', 'cellmesh.db')
    print('database:\n' + DB_DIR)
    
    # Top 15 genes for B cell in Tabula Muris Droplet dataset
    query_genes = ['CD79A','MS4A1','CD79B','TNFRSF13C','BANK1',
                   'CR2','CD19','CD37','CD22','FCRL1',
                   'FCRLA','CD74','LTB','BLK','POU2AF1']

    query_params = {
      'n_proc': 1,  # num of proc >= 1
      'db_cnt_thre': 3,
      'alpha': None}

    cell_prob_vals = prob_test(
        genes=query_genes,
        params=query_params,
        db_dir=DB_DIR,
        species='mouse')
  
    for i in range(min(len(cell_prob_vals), 10)):
      t = cell_prob_vals[i]
      print("i=%d, id=%s, name=%s, prob=%f"%(i, t[0], t[1], t[2]))
      print("  overlapping genes:" + str(t[3]))
      print("  pmids wrt overlapping genes:" + str(t[4]))
      print('\n\n')

    return

if __name__ == '__main__':
  unittest.main()
