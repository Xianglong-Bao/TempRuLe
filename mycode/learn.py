import time
import argparse
import json
import numpy as np
from datetime import datetime
from joblib import Parallel, delayed

from grapher import Grapher
from temporal_walk import Temporal_Walk
from rule_learning import Rule_Learner, rules_statistics


parser = argparse.ArgumentParser()
parser.add_argument("--dataset", "-d", default="", type=str)
parser.add_argument("--rule_lengths", "-l", default="3", type=int, nargs="+")
parser.add_argument("--num_walks", "-n", default="100", type=int)
parser.add_argument("--transition_distr", default="unif", type=str)
parser.add_argument("--num_processes", "-p", default=1, type=int)
parser.add_argument("--seed", "-s", default=None, type=int)
parsed = vars(parser.parse_args())

dataset = parsed["dataset"]
rule_lengths = parsed["rule_lengths"]
rule_lengths = [rule_lengths] if (type(rule_lengths) == int) else rule_lengths
num_walks = parsed["num_walks"]
transition_distr = parsed["transition_distr"]
num_processes = parsed["num_processes"]
seed = parsed["seed"]

dataset_dir = "../data/" + dataset + "/"
data = Grapher(dataset_dir)
temporal_walk = Temporal_Walk(data.train_idx, data.inv_relation_id, transition_distr)
rl = Rule_Learner(temporal_walk.edges, data.id2relation, data.inv_relation_id, dataset)
all_relations = sorted(temporal_walk.edges)  # Learn for all relations
dt_save_delta_stats = datetime.now()
dt_save_delta_stats = dt_save_delta_stats.strftime("%Y%m%d%H%M%S")

def learn_rules(i, num_relations):
    """
    Learn rules (multiprocessing possible).

    Parameters:
        i (int): process number
        num_relations (int): minimum number of relations for each process

    Returns:
        rl.rules_dict (dict): rules dictionary
    """

    if seed:
        np.random.seed(seed)

    num_rest_relations = len(all_relations) - (i + 1) * num_relations
    if num_rest_relations >= num_relations:
        relations_idx = range(i * num_relations, (i + 1) * num_relations)
    else:
        relations_idx = range(i * num_relations, len(all_relations))

    num_rules = [0]
    delta_stats = {0.25: [1, 1], 0.5: [1, 1], 0.75: [1, 1], 1: [1, 1]}

    for k in relations_idx:
        rel = all_relations[k]
        for length in rule_lengths:
            it_start = time.time()
            for _ in range(num_walks):
                N = sum([stats[1] for stats in delta_stats.values()])
                ucb_values = {delta: (stats[0] / stats[1] if stats[1] > 0 else 0) + 1 * np.sqrt(
                    np.log(N) / (stats[1] if stats[1] > 0 else 1)) for delta, stats in
                              delta_stats.items()}
                total_ucb = sum(ucb_values.values())
                probabilities = {delta: ucb / total_ucb for delta, ucb in ucb_values.items()}
                delta_now = np.random.choice(list(probabilities.keys()), p=list(probabilities.values()))
                delta_list = delta_stats.keys()
                walk_successful, walk = temporal_walk.sample_walk(length + 1, rel, delta_now, delta_list)
                delta_stats[delta_now][1] += 1
                if walk_successful:
                    rl.create_rule(walk)
                    delta_stats[delta_now][0] += 1
            it_end = time.time()
            it_time = round(it_end - it_start, 6)
            num_rules.append(sum([len(v) for k, v in rl.rules_dict.items()]) // 2)
            num_new_rules = num_rules[-1] - num_rules[-2]
            print(
                "Process {0}: relation {1}/{2}, length {3}: {4} sec, {5} rules".format(
                    i,
                    k - relations_idx[0] + 1,
                    len(relations_idx),
                    length,
                    it_time,
                    num_new_rules,
                )
            )
        delta_stats = {delta: [1, 1] for delta in delta_stats}
    return rl.rules_dict


start = time.time()
num_relations = len(all_relations) // num_processes
output = Parallel(n_jobs=num_processes)(
    delayed(learn_rules)(i, num_relations) for i in range(num_processes)
)
end = time.time()

all_rules = output[0]
for i in range(1, num_processes):
    all_rules.update(output[i])


total_time = round(end - start, 6)
print("Learning finished in {} seconds.".format(total_time))

rl.rules_dict = all_rules

count_temporal_patterns = {}
count_temporal_patterns["0"] = 0
count_temporal_patterns["01"] = 0
count_temporal_patterns["10"] = 0
count_temporal_patterns["012"] = 0
count_temporal_patterns["021"] = 0
count_temporal_patterns["102"] = 0
count_temporal_patterns["120"] = 0
count_temporal_patterns["201"] = 0
count_temporal_patterns["210"] = 0
for head_rel, rules in rl.rules_dict.items():
    for rule in rules:
        if rule['body_timestamp_order'] == [0]:
            count_temporal_patterns["0"] += 1
        elif rule['body_timestamp_order'] == [0, 1]:
            count_temporal_patterns["01"] += 1
        elif rule['body_timestamp_order'] == [1, 0]:
            count_temporal_patterns["10"] += 1
        elif rule['body_timestamp_order'] == [0, 1, 2]:
            count_temporal_patterns["012"] += 1
        elif rule['body_timestamp_order'] == [0, 2, 1]:
            count_temporal_patterns["021"] += 1
        elif rule['body_timestamp_order'] == [1, 0, 2]:
            count_temporal_patterns["102"] += 1
        elif rule['body_timestamp_order'] == [1, 2, 0]:
            count_temporal_patterns["120"] += 1
        elif rule['body_timestamp_order'] == [2, 0, 1]:
            count_temporal_patterns["201"] += 1
        elif rule['body_timestamp_order'] == [2, 1, 0]:
            count_temporal_patterns["210"] += 1
print("Count temporal patterns: " + str(count_temporal_patterns))
rl.sort_rules_dict()
dt = datetime.now()
dt = dt.strftime("%Y%m%d%H%M%S")
rl.save_rules(dt, rule_lengths, num_walks, transition_distr, seed)
rl.save_rules_verbalized(dt, rule_lengths, num_walks, transition_distr, seed)
rules_statistics(rl.rules_dict)
