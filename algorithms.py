# NOTICE some of this code was copied from the research-experimental repo

import torch

from align_system.algorithms.chat_kdma_predicting_adm import ChatKDMAPredictingADM
from align_system.algorithms.llama_2_single_kdma_adm import Llama2SingleKDMAADM
from align_system.algorithms.llama_index import LlamaIndex
from align_system.algorithms.pulse_tagging_adm import PulseTaggingADM
from align_system.algorithms.multi_comparison_adm import MultiComparisonADM

from align_system.algorithms.lib.aligned_decision_maker import AlignedDecisionMaker
import align_system.evaluation.adm_evaluator as adm_evaluator


class DummyADM(AlignedDecisionMaker):
    
    def __init__(self, default_choice, predict_kdma_values):
        self.default_choice = default_choice
        self.predict_kdma_values = predict_kdma_values
    
    def __call__(self, sample, target_kdma_values, **kwargs):    
        response = {
            'choice': self.default_choice
        }
        
        if self.predict_kdma_values:
            response['predicted_kdma_values'] = [
                {
                    kdma_name: 0
                    for kdma_name in target_kdma_values
                }
                for _ in sample['choices']    
            ]
        
        return response


class OracleADM(AlignedDecisionMaker):
    
    def __init__(self, flip_alignment, predict_kdma_values):
        self.flip_alignment = flip_alignment
        self.predict_kdma_values = predict_kdma_values
    
    def __call__(self, sample, target_kdma_values, labels, **kwargs):
        
        eval_fn = max
        if self.flip_alignment:
            eval_fn = min
        
        choice_idx = eval_fn(range(len(labels)),
            key=lambda i: adm_evaluator.kitware_similarity_score(target_kdma_values, labels[i])
        )
        
        response = {'choice': choice_idx}
        
        if self.predict_kdma_values:
            response['predicted_kdma_values'] = labels
        
        return response
    

def chat_kdma_predicting_adm(config):
    algorithm = ChatKDMAPredictingADM.load_model(
        device=config['language_model']['device'],
        hf_model_name=config['language_model']['model_name'],
        precision={
            'half': torch.float16,
            'full': torch.float32
        }[config['language_model']['precision']],
    )
    
    return algorithm


def llama_2_single_kdma_adm(config):
    algorithm = Llama2SingleKDMAADM(**config)
    algorithm.load_model()
    return algorithm


def llama_index_adm(config):
    algorithm = LlamaIndex(**config)
    algorithm.load_model()
    return algorithm


def dummy_adm(config):
    return DummyADM(**config)


def oracle_adm(config):
    return OracleADM(**config)

def pulse_tagging_adm(config):
    return PulseTaggingADM.load_model(
        device=config['device'],
        hf_model_name=config['model_name'],
        precision={
            'half': torch.float16,
            'full': torch.float32
        }[config['precision']]
    )

def multi_comparison_adm(config):
    return MultiComparisonADM.load_model(**config['language_model'])

eval_fns = [
    chat_kdma_predicting_adm,
    llama_2_single_kdma_adm,
    llama_index_adm,
    dummy_adm,
    oracle_adm,
    pulse_tagging_adm,
    multi_comparison_adm,
]


def get_algorithm(config):
    algorithm_function = [eval_fn for eval_fn in eval_fns if eval_fn.__name__ in config]
    if len(algorithm_function) != 1:
        return None
    
    return algorithm_function[0](config[algorithm_function[0].__name__])
    