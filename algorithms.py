# NOTICE some of this code was copied from the research-experimental repo

import random

from align_system.algorithms.abstracts import AlignedDecisionMaker
# from align_system.algorithms.outlines_regression_adm_comparative import OutlinesTransformersComparativeRegressionADM

class DummyADM(AlignedDecisionMaker):

    def __init__(self, default_choice, predict_kdma_values):
        if default_choice == 'random':
            default_choice = None

        self.default_choice = default_choice
        self.predict_kdma_values = predict_kdma_values

    def __call__(self, sample, target_kdma_values, **kwargs):
        print(sample)
        print(target_kdma_values)
        choice = self.default_choice
        if self.default_choice is None:
            choice = random.choice(range(len(sample['choices'])))

        response = {
            'choice': choice
        }

        if self.predict_kdma_values:
            response['predicted_kdma_values'] = [
                {
                    kdma_name: random.uniform(0, 10)
                    for kdma_name in target_kdma_values
                }
                for _ in sample['choices']
            ]

        return response


def dummy_adm(config):
    return DummyADM(**config)

eval_fns = [
    dummy_adm,
]


def get_algorithm(config):
    algorithm_function = [eval_fn for eval_fn in eval_fns if eval_fn.__name__ in config]
    if len(algorithm_function) != 1:
        return None
    algo_config = config[algorithm_function[0].__name__]
    return algorithm_function[0](algo_config), algo_config
