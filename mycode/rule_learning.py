from datetime import datetime
import os
import json
import itertools
import numpy as np
from collections import Counter


class Rule_Learner(object):
    def __init__(self, edges, id2relation, inv_relation_id, dataset):
        """
        Initialize rule learner object.

        Parameters:
            edges (dict): edges for each relation
            id2relation (dict): mapping of index to relation
            inv_relation_id (dict): mapping of relation to inverse relation
            dataset (str): dataset name

        Returns:
            None
        """

        self.edges = edges
        self.id2relation = id2relation
        self.inv_relation_id = inv_relation_id

        self.found_rules = []
        self.rules_dict = dict()
        self.output_dir = "../output/" + dataset + "/"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def create_rule(self, walk):
        """
        Create a rule given a CP temporal random walk.

        Parameters:
            walk (dict): cyclic temporal random walk
                         {"entities": list, "relations": list, "timestamps": list}

        Returns:
            rule (dict): created rule
        """

        rule = dict()
        rule["head_rel"] = int(walk["relations"][0])
        rule["body_rels"] = [
            self.inv_relation_id[x] for x in walk["relations"][1:][::-1]
        ]
        rule["var_constraints"] = self.define_var_constraints(
            walk["entities"][1:][::-1]
        )

        walk["timestamps"][1:] = walk["timestamps"][-1:0:-1]

        timestamps = walk["timestamps"]
        body_timestamps = timestamps[1:]
        body_timestamps_order_dict = {}
        body_timestamps_num_counts = {}
        processed_timestamps_num_counts = {}
        ordered_indexes = []
        iteration = 0
        for ts in body_timestamps:
            if ts not in body_timestamps_num_counts:
                body_timestamps_num_counts[ts] = 0
            else:
                body_timestamps_num_counts[ts] += 1
        sorted_timestamps_list = sorted(body_timestamps)

        for index, value in enumerate(sorted_timestamps_list):
            if value not in body_timestamps_order_dict:
                body_timestamps_order_dict[value] = index
                processed_timestamps_num_counts[value] = 0
        for i in range (len(body_timestamps)):
            if body_timestamps_num_counts[body_timestamps[i]] == 0:
                ordered_indexes.append(body_timestamps_order_dict[body_timestamps[i]])
            else:
                if processed_timestamps_num_counts[body_timestamps[i]] == 0:
                    ordered_indexes.append(body_timestamps_order_dict[body_timestamps[i]])
                    processed_timestamps_num_counts[body_timestamps[i]] += 1
                else:
                    ordered_indexes.append(body_timestamps_order_dict[body_timestamps[i]] + processed_timestamps_num_counts[body_timestamps[i]])
                    processed_timestamps_num_counts[body_timestamps[i]] += 1

        rule["body_timestamp_order"] = ordered_indexes


        if rule not in self.found_rules:
            self.found_rules.append(rule.copy())
            (
                rule["conf"],
                rule["rule_supp"],
                rule["body_supp"],
            ) = self.estimate_confidence(rule)

            if rule["conf"]:
                self.update_rules_dict(rule)

    def define_var_constraints(self, entities):
        """
        Define variable constraints, i.e., state the indices of reoccurring entities in a walk.

        Parameters:
            entities (list): entities in the temporal walk

        Returns:
            var_constraints (list): list of indices for reoccurring entities
        """

        var_constraints = []
        for ent in set(entities):
            all_idx = [idx for idx, x in enumerate(entities) if x == ent]
            var_constraints.append(all_idx)
        var_constraints = [x for x in var_constraints if len(x) > 1]

        return sorted(var_constraints)

    def estimate_confidence(self, rule, num_samples=500):
        """
        Estimate the confidence of the rule by sampling bodies and checking the rule support.

        Parameters:
            rule (dict): rule

            num_samples (int): number of samples

        Returns:
            confidence (float): confidence of the rule, rule_support/body_support
            rule_support (int): rule support
            body_support (int): body support
        """

        all_bodies = []
        for _ in range(num_samples):

            sample_successful, body_ents_tss = self.sample_body(
                rule["body_rels"], rule["var_constraints"], rule["body_timestamp_order"]
            )
            if sample_successful:
                all_bodies.append(body_ents_tss)

        all_bodies.sort()
        unique_bodies = list(x for x, _ in itertools.groupby(all_bodies))
        body_support = len(unique_bodies)

        confidence, rule_support = 0, 0
        if body_support:
            rule_support = self.calculate_rule_support(unique_bodies, rule["head_rel"])
            confidence = round(rule_support / body_support, 6)

        return confidence, rule_support, body_support

    def sample_body(self, body_rels, var_constraints, body_timestamp_order):
        """
        Sample a walk according to the rule body and body_timestamp_order.

        Parameters:
            body_rels (list): relations in the rule body
            var_constraints (list): variable constraints for the entities
            body_timestamp_order (list): the order of the timestamps in the body

        Returns:
            sample_successful (bool): if a body has been successfully sampled
            body_ents_tss (list): entities and timestamps (alternately entity and timestamp)
                                  of the sampled body
        """

        sample_successful = True
        body_ents_tss = []
        cur_rel = body_rels[0]
        rel_edges = self.edges[cur_rel]
        next_edge = rel_edges[np.random.choice(len(rel_edges))]
        cur_ts = next_edge[3]
        ts_1 = next_edge[3]
        cur_node = next_edge[2]
        body_ents_tss.append(next_edge[0])
        body_ents_tss.append(cur_ts)
        body_ents_tss.append(cur_node)
        iteration = 0

        for cur_rel in body_rels[1:]:
            next_edges = self.edges[cur_rel]
            if len(body_timestamp_order) == 2:
                if body_timestamp_order[0] < body_timestamp_order[1]:
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] >= ts_1)
                else:
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] <= ts_1)
            elif len(body_timestamp_order) == 3:
                if body_timestamp_order == [0, 1, 2]:
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] >= cur_ts)
                    iteration += 1
                elif body_timestamp_order == [2, 1, 0]:
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] <= cur_ts)
                    iteration += 1
                elif body_timestamp_order == [0, 2, 1] and iteration == 0: 
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] >= ts_1)
                    iteration += 1
                elif body_timestamp_order == [0, 2, 1] and iteration == 1:
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] <= ts_2) * (next_edges[:, 3] >= ts_1)
                    iteration += 1
                elif body_timestamp_order == [1, 0, 2] and iteration == 0:
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] <= ts_1)
                    iteration += 1
                elif body_timestamp_order == [1, 0, 2] and iteration == 1:
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] >= ts_1)
                    iteration += 1
                elif body_timestamp_order == [1, 2, 0] and iteration == 0:
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] >= ts_1)
                    iteration += 1
                elif body_timestamp_order == [1, 2, 0] and iteration == 1:
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] <= ts_1)
                    iteration += 1
                elif body_timestamp_order == [2, 0, 1] and iteration == 0:
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] <= ts_1)
                    iteration += 1
                elif body_timestamp_order == [2, 0, 1] and iteration == 1:
                    mask = (next_edges[:, 0] == cur_node) * (next_edges[:, 3] >= ts_2) * (next_edges[:, 3] <= ts_1)
                    iteration += 1
            filtered_edges = next_edges[mask]

            if len(filtered_edges):
                next_edge = filtered_edges[np.random.choice(len(filtered_edges))]
                cur_ts = next_edge[3]
                if iteration == 1:
                    ts_2 = cur_ts
                cur_node = next_edge[2]
                body_ents_tss.append(cur_ts)
                body_ents_tss.append(cur_node)
            else:
                sample_successful = False
                break

        if sample_successful and var_constraints:
            # Check variable constraints
            body_var_constraints = self.define_var_constraints(body_ents_tss[::2])
            if body_var_constraints != var_constraints:
                sample_successful = False

        return sample_successful, body_ents_tss

    def calculate_rule_support(self, unique_bodies, head_rel):
        """
        Calculate the rule support.

        Parameters:
            unique_bodies (list): bodies from self.sample_body
            head_rel (int): head relation

        Returns:
            rule_support (int): rule support
        """

        rule_support = 0
        head_rel_edges = self.edges[head_rel]
        for body in unique_bodies:
            mask = (
                (head_rel_edges[:, 0] == body[0])
                * (head_rel_edges[:, 2] == body[-1])
                * (head_rel_edges[:, 3] > body[-2])
            )

            if True in mask:
                rule_support += 1

        return rule_support

    def update_rules_dict(self, rule):
        """
        Update the rules if a new rule has been found.

        Parameters:
            rule (dict): generated rule from self.create_rule

        Returns:
            None
        """

        try:
            self.rules_dict[rule["head_rel"]].append(rule)
        except KeyError:
            self.rules_dict[rule["head_rel"]] = [rule]

    def sort_rules_dict(self):
        """
        Sort the found rules for each head relation by decreasing confidence.

        Parameters:
            None

        Returns:
            None
        """

        for rel in self.rules_dict:
            self.rules_dict[rel] = sorted(
                self.rules_dict[rel], key=lambda x: x["conf"], reverse=True
            )

    def save_rules(self, dt, rule_lengths, num_walks, transition_distr, seed):
        """
        Save all rules.

        Parameters:
            dt (str): time now
            rule_lengths (list): rule lengths
            num_walks (int): number of walks
            transition_distr (str): transition distribution
            seed (int): random seed

        Returns:
            None
        """

        rules_dict = {int(k): v for k, v in self.rules_dict.items()}
        filename = "{0}_r{1}_n{2}_{3}_s{4}_rules.json".format(
            dt, rule_lengths, num_walks, transition_distr, seed
        )
        filename = filename.replace(" ", "")
        with open(self.output_dir + filename, "w", encoding="utf-8") as fout:
            json.dump(rules_dict, fout)

    def save_rules_verbalized(
        self, dt, rule_lengths, num_walks, transition_distr, seed
    ):
        """
        Save all rules in a human-readable format.

        Parameters:
            dt (str): time now
            rule_lengths (list): rule lengths
            num_walks (int): number of walks
            transition_distr (str): transition distribution
            seed (int): random seed

        Returns:
            None
        """

        rules_str = ""
        for rel in self.rules_dict:
            for rule in self.rules_dict[rel]:
                rules_str += verbalize_rule(rule, self.id2relation) + "\n"

        filename = "{0}_r{1}_n{2}_{3}_s{4}_rules.txt".format(
            dt, rule_lengths, num_walks, transition_distr, seed
        )
        filename = filename.replace(" ", "")
        with open(self.output_dir + filename, "w", encoding="utf-8") as fout:
            fout.write(rules_str)


def verbalize_rule(rule, id2relation):
    """
    Verbalize the rule to be in a human-readable format.

    Parameters:
        rule (dict): rule from Rule_Learner.create_rule
        id2relation (dict): mapping of index to relation

    Returns:
        rule_str (str): human-readable rule
    """

    if rule["var_constraints"]:
        var_constraints = rule["var_constraints"]
        constraints = [x for sublist in var_constraints for x in sublist]
        for i in range(len(rule["body_rels"]) + 1):
            if i not in constraints:
                var_constraints.append([i])
        var_constraints = sorted(var_constraints)
    else:
        var_constraints = [[x] for x in range(len(rule["body_rels"]) + 1)]

    rule_str = "{0:8.6f}  {1:4}  {2:4}  {3}(X0,X{4},T{5}) <- "
    obj_idx = [
        idx
        for idx in range(len(var_constraints))
        if len(rule["body_rels"]) in var_constraints[idx]
    ][0]
    rule_str = rule_str.format(
        rule["conf"],
        rule["rule_supp"],
        rule["body_supp"],
        id2relation[rule["head_rel"]],
        obj_idx,
        len(rule["body_rels"]),
    )

    for i in range(len(rule["body_rels"])):
        sub_idx = [
            idx for idx in range(len(var_constraints)) if i in var_constraints[idx]
        ][0]
        obj_idx = [
            idx for idx in range(len(var_constraints)) if i + 1 in var_constraints[idx]
        ][0]

        rule_str += "{0}(X{1},X{2},T{3}), ".format(
            id2relation[rule["body_rels"][i]], sub_idx, obj_idx, rule["body_timestamp_order"][i]
        )

    return rule_str[:-2]


def rules_statistics(rules_dict):
    """
    Show statistics of the rules.

    Parameters:
        rules_dict (dict): rules

    Returns:
        None
    """

    print(
        "Number of relations with rules: ", len(rules_dict)
    )  # Including inverse relations
    print("Total number of rules: ", sum([len(v) for k, v in rules_dict.items()]))

    lengths = []
    for rel in rules_dict:
        lengths += [len(x["body_rels"]) for x in rules_dict[rel]]
    rule_lengths = [(k, v) for k, v in Counter(lengths).items()]
    print("Number of rules by length: ", sorted(rule_lengths))
