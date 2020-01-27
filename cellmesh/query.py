#import pdb
import numpy as np
import multiprocessing

from cellmesh.db import \
  DB_DIR,\
  get_all_cell_id_names, \
  get_all_genes, \
  get_cell_genes_pmids

def calc_prob_one_query_one_cell(args):
  '''
  calc prob score for one query and one cell

  Input:
    genes: a ranked list of gene symbols, as query Q
    cell_id: MeSH cell id of a candidate cell C (wrt a column in DB)
    cell_gene_count: list of (gene symbol, cnt wrt C)
    overlapping_genes: set of gene symbols occurring in Q and C
      currently not used
    params: contains config params of prob_test. see prob_test() for description
    N_all_genes: total number of genes in DB
  Output:
    a tuple of cell id of MeSH cell C and P(Q|C) (Q for query)
  '''
  genes, cell_id, cell_gene_count, overlapping_genes, params, N_all_genes = args

  alpha = params.get("alpha", None)

  col_sum = sum([x[1] for x in cell_gene_count])
  if col_sum==0:
    return (cell_id, -np.inf)

  #dic with key as gene symbol and val as (rank/0-based, normed weight)
  cell_gene_count = sorted(cell_gene_count, key=lambda x: -x[1])
  N = len(cell_gene_count)
  db_col = {}
  for rank in range(N):
    g, cnt = cell_gene_count[rank]
    weight = float(cnt) / col_sum
    db_col[g] = (rank, weight)

  #query genes: g(0), g(1), ..., g(M-1)
  #       rank:    0,    1, ..., M-1
  M = len(genes)
  q_list = [(genes[i], i) for i in range(M)]

  ES_ML = 0 #enrichment score, maximum likelihood

  for g, rank_Q in q_list:
    if g in db_col:
      weight_D = db_col[g][1]
      step = np.log(weight_D)

      if alpha is not None:
        alpha_val = np.log(alpha)
        step += alpha_val
    else:
      step = -np.log(N_all_genes - N) if N_all_genes!=N else 0

      if alpha is not None:
        alpha_val = np.log(1-alpha)
        step += alpha_val
    ES_ML += step

  return (cell_id, ES_ML) 

def prob_test_default_params():
  params = {}
  params["n_proc"] = 1
  params["db_cnt_thre"] = 0
  params["alpha"] = None
  return params

def prob_test(
  genes, 
  params=None,
  db_dir=DB_DIR,
  species='homo_sapiens'):
  '''
  This is the Maximum Likelihood query test on the tf-idf matrix.

  Input:
    genes: a ranked list of gene symbols
    params: None or contains config params of prob_test
      {
        "n_proc":
          number of processes for parallel processing,
        "db_cnt_thre":
          a gene g is considered to co-occur with a cell c if db(g, c) > db_cnt_thre
        "alpha":
          None to disable, or (0,1), controls sampling probability of a query gene from a candidate cell
      }
    db_dir:
      SQL database file. Default is cellmesh/data/cellmesh.db
    species:
      Specify the species of the genes. Default is homo_sapiens (or human) genes.

  Output:
    cell_prob_vals:
      a list of 5-tuples:
        (MeSH ID, 
         MeSH cell type,
         prob val (in log),
         list of overlapping genes,
         dic with key as overlapping gene and val as list of related pmids) 
      in descending order wrt prob val.
  '''
  genes = [x.upper() for x in genes]
  all_cells = get_all_cell_id_names(db_dir=db_dir)
  all_genes = get_all_genes(db_dir=db_dir, species=species)
  N_all_genes = len(all_genes)

  genes_set = set(genes)

  #----- algo configuration
  if params is None:
    params = prob_test_default_params()

  #----- prepare info for per (cell_id, cell_name, prob=n/a, overlapping_genes, pmids)
  cell_prob_vals = {}
  args_list = []
  for cell_id, cell_name in all_cells:
    #a set of (gene_symbol, its pmids connected by ",", cnt val) wrt candidate cell_id
    genes_pmids_count = set(
      get_cell_genes_pmids(
        cell_id,
        db_dir=db_dir,
        species=species,
        threshold=params["db_cnt_thre"],
        uppercase_gene_names=True))
    cell_genes = [x[0] for x in genes_pmids_count]
    overlapping_genes = genes_set.intersection(cell_genes)
    if len(overlapping_genes) == 0:
      continue

    pmids = {}
    for gene, pmid, _ in genes_pmids_count:
      if gene in overlapping_genes:
        pmids[gene] = pmid.split(',')

    overlapping_genes = list(overlapping_genes)
    cell_prob_vals[cell_id] = [cell_name, -np.inf, overlapping_genes, pmids]

    cell_gene_count = [(x[0], x[2]) for x in genes_pmids_count]
    args = (
      genes,
      cell_id,
      cell_gene_count,
      overlapping_genes,
      params,
      N_all_genes
      )
    args_list.append(args)

  #----- calc prob scores, in parallel if possible
  n_proc = params["n_proc"]
  res = []
  if n_proc==1:
    for args in args_list:
      r = calc_prob_one_query_one_cell(args)
      res.append(r)
  else:
    p = multiprocessing.Pool(n_proc)
    res = p.map(calc_prob_one_query_one_cell, args_list)
  for cell_id, prob in res:
    cell_prob_vals[cell_id][1] = prob
    cell_prob_vals[cell_id] = tuple(cell_prob_vals[cell_id])

  #----- wrap up outputs -----
  cell_prob_vals = list(cell_prob_vals.items())
  cell_prob_vals.sort(key=lambda x: -x[1][1]) #descending order
  # merge items
  cell_prob_vals = [(x[0],) + x[1] for x in cell_prob_vals]

  return cell_prob_vals