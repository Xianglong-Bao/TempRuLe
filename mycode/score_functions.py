import numpy as np


def score1(rule, c=0):
    """
    Calculate candidate score depending on the rule's confidence.

    Parameters:
        rule (dict): rule from rules_dict
        c (int): constant for smoothing

    Returns:
        score (float): candidate score
    """

    score = rule["rule_supp"] / (rule["body_supp"] + c)

    return score


def score2(cands_walks, test_query_ts, lmbda, rule):
    """
    Calculate candidate score depending on the time difference.

    Parameters:
        cands_walks (pd.DataFrame): walks leading to the candidate
        test_query_ts (int): test query timestamp
        lmbda (float): rate of exponential distribution

    Returns:
        score (float): candidate score
    """
    body_timestamp_order = rule["body_timestamp_order"]
    min_index = body_timestamp_order.index(min(body_timestamp_order))

    # max_cands_ts = max(cands_walks["timestamp_0"])
    max_cands_ts = max(cands_walks["timestamp_{}".format(min_index)])
    score = np.exp(
        lmbda * (max_cands_ts - test_query_ts)
    )  # Score depending on time difference
    return score


def score_12(rule, cands_walks, test_query_ts, lmbda, a):
    """
    Combined score function.

    Parameters:
        rule (dict): rule from rules_dict
        cands_walks (pd.DataFrame): walks leading to the candidate
        test_query_ts (int): test query timestamp
        lmbda (float): rate of exponential distribution
        a (float): value between 0 and 1

    Returns:
        score (float): candidate score
    """
    # score = a * score1(rule) + (1 - a) * score2(cands_walks, test_query_ts, lmbda)
    score = a * score1(rule) + (1 - a) * score2(cands_walks, test_query_ts, lmbda, rule)
    return score

def score_ruleConfidence_timediffReward(rule, cands_walks, test_query_ts, a, alpha, lambda1, lambda2,):
    score = a * score1(rule) + (1 - a) * score_timediffReward(rule, cands_walks, test_query_ts, alpha, lambda1, lambda2,)
    return score

def score_timediffReward(rule, cands_walks, test_query_ts, alpha, lambda1, lambda2,):
    body_timestamp_order = rule["body_timestamp_order"]
    min_index = body_timestamp_order.index(min(body_timestamp_order))
    max_cands_ts = max(cands_walks["timestamp_{}".format(min_index)])

    # timestamp_columns = cands_walks.filter(like='timestamp_')
    # average_timestamp_by_walk = timestamp_columns.mean(axis=1)
    # total_average_timestamp = average_timestamp_by_walk.mean()
    # time_diff = test_query_ts - total_average_timestamp

    time_diff = test_query_ts - max_cands_ts

    time_diff = 0.1 * time_diff 

    short_term = alpha / (1 + lambda1 * time_diff)

    long_term = (1 - alpha) / (1 + np.log(lambda2 * time_diff))
    # long_term = (1 - alpha) / (10 + np.log(lambda2 * time_diff))
    return short_term + long_term

    # return np.exp(-time_diff)