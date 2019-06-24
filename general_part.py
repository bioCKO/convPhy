import argparse
from scripts.general import *
from scripts.core.phyc import *
from scripts.core.phenotype_prediction import get_genotype_dict
from scripts.annotation.annotate_snp import annotate_snp

parser = argparse.ArgumentParser(description='search SNP ')
parser.add_argument("-i", "--input", required=True, help="path to dir with all input files")
parser.add_argument("-o", "--out_dir", default="./output_phyc/", help="path to dir_output")
parser.add_argument("-geno", "--genotype_prediction", default=False, type=bool)
parser.add_argument("-pheno", "--phenotype_prediction", default=False, type=bool)
parser.add_argument("-conphy", default=False, type=bool)
parser.add_argument("-p_value", default=False, type=bool)

args = parser.parse_args()

# input files
run_dir = os.path.join(os.path.abspath(args.input))
info_pos = os.path.join(run_dir, "info_pos.txt")
SNPs_in = os.path.join(run_dir, 'SNPs.txt')
phylip_in = os.path.join(run_dir, 'farhat.phy')
raxml_in = os.path.join(run_dir, "raxml_tree.nh")
R_in = os.path.join(run_dir, 'R_states')
S_in = os.path.join(run_dir, 'S_states')

# output files
out_dir = os.path.join(os.path.abspath(args.out_dir))
os.makedirs(out_dir, exist_ok=True)
os.chdir(run_dir)

# run genotype prediction
if not args.genotype_prediction:
    path_to_ancestor_phylip = run_raxml(out_dir, raxml_in, phylip_in)
path_to_ancestor_phylip = os.path.join(out_dir, 'raxml', 'RAxML_marginalAncestralStates.nh')

# run phenotype prediction
if not args.phenotype_prediction:
    run_phenotype_prediction(out_dir, phylip_in, path_to_ancestor_phylip, R_in, S_in)

with open(S_in) as children_S, open(R_in) as children_R, \
     open(path_to_ancestor_S_phenotype) as anc_S, open(path_to_ancestor_R_phenotype) as anc_R:    
    name_of_S = [line.strip() for line in children_S]
    name_of_R = [line.strip() for line in children_R]
    ancestor_S_phenotype = [line.strip() for line in anc_S]
    ancestor_R_phenotype = [line.strip() for line in anc_R]

path_to_ancestor_S_phenotype = os.path.join(out_dir, "phenotype_prediction", 'negative_phenotype.txt')
path_to_ancestor_R_phenotype = os.path.join(out_dir, "phenotype_prediction", 'positive_phenotype.txt')
genotype_dict = get_genotype_dict(phylip_in, path_to_ancestor_phylip)

# run convPhy
if not args.conphy:
    run_phyc(out_dir, name_of_R, name_of_S, ancestor_S_phenotype,
             ancestor_R_phenotype, info_pos, genotype_dict)

path_to_R_S = os.path.join(out_dir, "phyc", 'pos.txt')
with open(path_to_R_S) as f_in:
    R_S = [line.strip().split() for line in f_in]

# run permutation test
if not args.p_value:
    out_dir = os.path.join(args.out_dir, "p_value")
    run_p_value(out_dir, R_S, info_pos)

# annotation SNPs
snps_path = os.path.join(out_dir, "p_value", "p_value.txt")
path_to_snps_out_csv = os.path.join(out_dir, "p_value","annotated_snps.csv")
annotate_snp(snps_path, path_to_snps_out_csv)
