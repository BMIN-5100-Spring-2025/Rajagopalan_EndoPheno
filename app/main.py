import clips
import pandas as pd
import sys
sys.path.append('./src/')
from clips_util import pull_facts, print_rules, print_templates, build_read_assert
import argparse
import csv

def count_symptoms(*args):
    count = 0
    for symptom in args:
        if symptom == "yes":
            count += 1
    return count

def pull_explanation(endo_class, concomitant_class):
    explanation = ""
    if endo_class == "yes" and concomitant_class == "yes":
        explanation = "Patient has at least 1 symptom(s) that are consistent with both endometriosis and additional concomitant disease (irritable bowel syndrome, interstitial cystitis, urinary tract stones, or a reproductive tract anomaly). The purpose of this system is to identify endometriosis cases for large-scale research studies - this is NOT intended to be a formal diagnosis; classification was made based on limited symptoms without lab tests/physical exam results and further confirmation may be necessary."
    elif endo_class == "yes" and concomitant_class == "no":
        explanation = "Patient has at least 1 symptom that is consistent only with endometriosis and no symptoms consistent with additional diseases (irritable bowel syndrome, interstitial cystitis, urinary tract stones, or a reproductive tract anomaly). The purpose of this system is to identify endometriosis cases for large-scale research studies - this is NOT intended to be a formal diagnosis; classification was made based on limited symptoms without lab tests/physical exam results and further confirmation may be necessary."
    elif endo_class == "no" and concomitant_class == "yes":
        explanation = "Patient has at least 1 symptom that is consistent only with non-Endometriosis phenotypes (irritable bowel syndrome, interstitial cystitis, urinary tract stones, or a reproductive tract anomaly). The purpose of this system is to identify endometriosis cases for large-scale research studies - this is NOT intended to be a formal diagnosis; classification was made based on limited symptoms without lab tests/physical exam results and further confirmation may be necessary."
    elif endo_class == "no" and concomitant_class == "no":       
        explanation = "Patient has no symptoms that are consistent with endometriosis or other phenotypes that we screened for (irritable bowel syndrome, interstitial cystitis, urinary tract stones, or a reproductive tract anomaly). The purpose of this system is to identify endometriosis cases for large-scale research studies - this is NOT intended to be a formal diagnosis; classification was made based on limited symptoms without lab tests/physical exam results and further confirmation may be necessary."
    
    return explanation

# create the CLIPS environment
env = clips.Environment()

# env.define_function(store_result)
env.define_function(count_symptoms)

# patient endometriosis symptoms
DEFTEMPLATE_PATIENT_ENDOMETRIOSIS_SYMPTOMS = """
(deftemplate patient_endo_symptoms
    (slot endometriosis (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot abdominal_pelvic_pain (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot dysmenorrhea (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot pain_with_sex (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot dyschezia (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot dysuria (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot infertility (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot pelvic_perineal_pain (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot adenomyosis (type SYMBOL)
        (allowed-symbols yes no unknown))

    )
"""
env.build(DEFTEMPLATE_PATIENT_ENDOMETRIOSIS_SYMPTOMS)

# patient concomitant disease symptoms
DEFTEMPLATE_PATIENT_CONCOMITANT_DISEASE_SYMPTOMS = """
(deftemplate patient_concomitant_disease_symptoms
    (slot amenorrhea (type SYMBOL) 
        (allowed-symbols yes no unknown))
    (slot constipation (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot diarrhea (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot flank_pain (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot hematuria (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot frequent_urination (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot ibs (type SYMBOL)
        (allowed-symbols yes no unknown))
    (slot interstitial_cystitis (type SYMBOL)
        (allowed-symbols yes no unknown))

)
"""
env.build(DEFTEMPLATE_PATIENT_CONCOMITANT_DISEASE_SYMPTOMS)

# status of whether or not patient has symptoms consistent with endo
DEFTEMPLATE_ENDOMETRIOSIS_INCLUSION = """
(deftemplate endometriosis_inclusion
    (slot meets_criteria (type SYMBOL)
    (allowed-symbols yes no unknown))
)
"""
env.build(DEFTEMPLATE_ENDOMETRIOSIS_INCLUSION)

# status of whether or not patient has symptoms consistent with non-endo diseases
DEFTEMPLATE_CONCOMITANT_DISEASE_INCLUSION = """
(deftemplate concomitant_disease_inclusion
    (slot meets_criteria (type SYMBOL)
    (allowed-symbols yes no unknown))
)
"""
env.build(DEFTEMPLATE_CONCOMITANT_DISEASE_INCLUSION)

# status of patient being classified as case or control
DEFTEMPLATE_NEW_PHENOTYPE_STATUS = """
(deftemplate new_phenotype_status
    (slot endometriosis_phenotype_status (type SYMBOL)
    (allowed-symbols yes no unknown))
)
"""
env.build(DEFTEMPLATE_NEW_PHENOTYPE_STATUS)

# Add deffacts that all statuses are unknown initially
DEFFACTS_INITIAL_STATUS = """
(deffacts starting_inclusion_exclusion_facts "Set the initial templates to unknown"
    (endometriosis_inclusion (meets_criteria unknown))
    (concomitant_disease_inclusion (meets_criteria unknown))
    (new_phenotype_status (endometriosis_phenotype_status unknown))
)
"""
env.build(DEFFACTS_INITIAL_STATUS)


DEFRULE_ENDOMETRIOSIS_INCLUSION_CRITERIA_NOT_MET = """
(defrule endo-inclusion-criteria-not-met "Rule to define a person not having any symptoms consistent with endometriosis"
    (logical
        (and
            (patient_endo_symptoms (abdominal_pelvic_pain ~yes))  
            (patient_endo_symptoms (dysmenorrhea ~yes))   
            (patient_endo_symptoms (pain_with_sex ~yes)) 
            (patient_endo_symptoms (dyschezia ~yes)) 
            (patient_endo_symptoms (dysuria ~yes)) 
            (patient_endo_symptoms (infertility ~yes))   
            (patient_endo_symptoms (pelvic_perineal_pain ~yes))
            (patient_endo_symptoms (adenomyosis ~yes))
            (patient_endo_symptoms (endometriosis ~yes))
        )
    )

    ?f1 <-(endometriosis_inclusion (meets_criteria unknown))

    => 

    (modify ?f1 (meets_criteria no))
)
"""
env.build(DEFRULE_ENDOMETRIOSIS_INCLUSION_CRITERIA_NOT_MET)

# indicates presence of symptom(s) that are consistent with endometriosis
DEFRULE_ENDOMETRIOSIS_INCLUSION_CRITERIA_MET = """
(defrule endo-inclusion-criteria-met "Rule to define a person as having symptom(s) consistent with endometriosis"
    (patient_endo_symptoms 
        (abdominal_pelvic_pain ?v1) 
        (dysmenorrhea ?v2) 
        (pain_with_sex ?v3) 
        (dyschezia ?v4) 
        (dysuria ?v5) 
        (infertility ?v6) 
        (pelvic_perineal_pain ?v7)
        (adenomyosis ?v8)
        (endometriosis ?v9))
    
    ?f1 <-(endometriosis_inclusion (meets_criteria unknown))
    
    => 
    (bind ?num_symptoms (count_symptoms ?v1 ?v2 ?v3 ?v4 ?v5 ?v6 ?v7 ?v8 ?v9))
    (if (>= ?num_symptoms 2) then
        (modify ?f1 (meets_criteria yes))
    )
    (if (< ?num_symptoms 2) then
        (modify ?f1 (meets_criteria no))
    )
)
"""
env.build(DEFRULE_ENDOMETRIOSIS_INCLUSION_CRITERIA_MET)

# indicates presence of symptoms that indicate no concomitant disease (along with or instead of) endometriosis
DEFRULE_CONCOMITANT_DISEASE_INCLUSION_CRITERIA_NOT_MET = """
(defrule concomitant-inclusion-criteria-not-met "Rule to define a person as having symptom(s) not consistent with other (non-endo) disease based on symptoms"
    (logical
        (and
            (patient_concomitant_disease_symptoms (amenorrhea ~yes))  
            (patient_concomitant_disease_symptoms (constipation ~yes))   
            (patient_concomitant_disease_symptoms (diarrhea ~yes)) 
            (patient_concomitant_disease_symptoms (flank_pain ~yes)) 
            (patient_concomitant_disease_symptoms (hematuria ~yes)) 
            (patient_concomitant_disease_symptoms (frequent_urination ~yes))
            (patient_concomitant_disease_symptoms (ibs ~yes))
            (patient_concomitant_disease_symptoms (interstitial_cystitis ~yes))
        )
    )

    ?f1 <-(concomitant_disease_inclusion (meets_criteria unknown))

    => 

    (modify ?f1 (meets_criteria no))
)
"""
env.build(DEFRULE_CONCOMITANT_DISEASE_INCLUSION_CRITERIA_NOT_MET)

# indicates presence of symptoms that indicate concomitant disease (along with or instead of) endometriosis
DEFRULE_CONCOMITANT_DISEASE_INCLUSION_CRITERIA_MET = """
(defrule concomitant-inclusion-criteria-met "Rule to define a person as having symptom(s) consistent with other (non-endo) disease based on inclusion criteria facts"
    (patient_concomitant_disease_symptoms 
        (amenorrhea ?v1) 
        (constipation ?v2) 
        (diarrhea ?v3) 
        (flank_pain ?v4) 
        (hematuria ?v5) 
        (frequent_urination ?v6)
        (ibs ?v7)
        (interstitial_cystitis ?v8)
    ) 
    
    ?f1 <-(concomitant_disease_inclusion  (meets_criteria unknown))
    
    => 
    (bind ?num_symptoms (count_symptoms ?v1 ?v2 ?v3 ?v4 ?v5 ?v6 ?v7 ?v8))
    (if (>= ?num_symptoms 2) then
        (modify ?f1 (meets_criteria yes))
    )
    (if (< ?num_symptoms 2) then
        (modify ?f1 (meets_criteria no))
    )

)
"""
env.build(DEFRULE_CONCOMITANT_DISEASE_INCLUSION_CRITERIA_MET)
# not going to try and classify the concomitant disease - but will factor whether they do have a concomitant disease (IBS, or interstitial cystitis, or adenomyosis) in my evaluation
    # because I don't have detailed symptom data for all of the concomitant diseases, only some of them

DEFRULE_ENDOMETRIOSIS_AND_CONCOMITANT_INCLUSION = """
(defrule endo-and-concomitant-inclusion
    (endometriosis_inclusion (meets_criteria yes))
    (concomitant_disease_inclusion (meets_criteria yes))
    ?f1 <-(new_phenotype_status (endometriosis_phenotype_status unknown))
    =>
    (modify ?f1 (endometriosis_phenotype_status yes))
    (println "___________")
    (println "Patient has at least 1 symptom(s) that are consistent with both endometriosis and additional concomitant disease (irritable bowel syndrome, interstitial cystitis, urinary tract stones, or a reproductive tract anomaly). The purpose of this system is to identify endometriosis cases for large-scale research studies - this is NOT intended to be a formal diagnosis; classification was made based on limited symptoms without lab tests/physical exam results and further confirmation may be necessary.")
    (println "___________")
)
"""
env.build(DEFRULE_ENDOMETRIOSIS_AND_CONCOMITANT_INCLUSION)

DEFRULE_ENDOMETRIOSIS_AND_CONCOMITANT_EXCLUSION = """
(defrule endo-and-concomitant-exclusion
    (endometriosis_inclusion (meets_criteria no))
    (concomitant_disease_inclusion (meets_criteria no))
    ?f1 <-(new_phenotype_status (endometriosis_phenotype_status unknown))
    =>
    (modify ?f1 (endometriosis_phenotype_status no))
    (println "___________")
    (println "Patient has no symptoms that are consistent with endometriosis or other phenotypes that we screened for (irritable bowel syndrome, interstitial cystitis, urinary tract stones, or a reproductive tract anomaly). The purpose of this system is to identify endometriosis cases for large-scale research studies - this is NOT intended to be a formal diagnosis; classification was made based on limited symptoms without lab tests/physical exam results and further confirmation may be necessary.")
    (println "___________")
)
"""
env.build(DEFRULE_ENDOMETRIOSIS_AND_CONCOMITANT_EXCLUSION)

DEFRULE_ONLY_ENDOMETRIOSIS_INCLUSION = """
(defrule only-endo-inclusion
    (endometriosis_inclusion (meets_criteria yes))
    (concomitant_disease_inclusion (meets_criteria no))
    ?f1 <-(new_phenotype_status (endometriosis_phenotype_status unknown))
    =>
    (modify ?f1 (endometriosis_phenotype_status yes))
    (println "___________")
    (println "Patient has at least 1 symptom that is consistent only with endometriosis and no symptoms consistent with additional diseases (irritable bowel syndrome, interstitial cystitis, urinary tract stones, or a reproductive tract anomaly). The purpose of this system is to identify endometriosis cases for large-scale research studies - this is NOT intended to be a formal diagnosis; classification was made based on limited symptoms without lab tests/physical exam results and further confirmation may be necessary.")
    (println "___________")
)
"""
env.build(DEFRULE_ONLY_ENDOMETRIOSIS_INCLUSION)

DEFRULE_ONLY_ENDOMETRIOSIS_EXCLUSION = """
(defrule only-endo-exclusion
    (endometriosis_inclusion (meets_criteria no))
    (concomitant_disease_inclusion (meets_criteria yes))
    ?f1 <-(new_phenotype_status (endometriosis_phenotype_status unknown))
    =>
    (modify ?f1 (endometriosis_phenotype_status no))
    (println "___________")
    (println "Patient has at least 1 symptom that is consistent only with non-Endometriosis phenotypes (irritable bowel syndrome, interstitial cystitis, urinary tract stones, or a reproductive tract anomaly). The purpose of this system is to identify endometriosis cases for large-scale research studies - this is NOT intended to be a formal diagnosis; classification was made based on limited symptoms without lab tests/physical exam results and further confirmation may be necessary.")
    (println "___________")
)
"""
env.build(DEFRULE_ONLY_ENDOMETRIOSIS_EXCLUSION)

# simulated input data
# data_file = './data/input/simulated_endopheno_data.csv'

# parser to take in filename containing input data
parser = argparse.ArgumentParser(
                    prog='Endometriosis Phenotyping System (Rule-Based)',
                    description='Takes in csv of input data and produces output file with classifications and explanations.')
parser.add_argument('filename') # positional argument
args = parser.parse_args()

data = pd.read_csv(args.filename, sep=',')

# retrieve the fact templates
patient_endo_template = env.find_template('patient_endo_symptoms')
patient_concomitant_disease_template = env.find_template('patient_concomitant_disease_symptoms')

output_df_columns = ['classification', 'explanation']
output_df = pd.DataFrame(columns=output_df_columns)

predicted_phenotype = []
for index, row in data.iterrows():
    # resetting knowledge base each time
    env.reset()

    # split into endo and concomitant disease dicts
    endo_data = data.loc[index, ['endometriosis', 'abdominal_pelvic_pain', 'dysmenorrhea', 'pain_with_sex', 'dyschezia', 'dysuria', 'infertility', 'pelvic_perineal_pain', 'adenomyosis']]
    additional_disease_data = data.loc[index, ['amenorrhea', 'constipation', 'diarrhea', 'flank_pain', 'hematuria', 'frequent_urination', 'ibs', 'interstitial_cystitis']]

    # create dictionary from current row, populated only with the symptoms I need
    endo_dict = endo_data.to_dict()
    other_diseases_dict = additional_disease_data.to_dict()

    # convert all the data into types as clips Symbol: 0 -> no, 1 -> yes, '' -> unknown
    for key, value in endo_dict.items():
        curr_value = value
        if curr_value == 0:
            endo_dict[key] = clips.Symbol('no')
        elif curr_value == 1:
            endo_dict[key] = clips.Symbol('yes')
        elif curr_value == '':
            endo_dict[key] = clips.Symbol('unknown')
            # this doesn't seem to ever get used but leaving it in for robustness

    for key, value in other_diseases_dict.items():
        curr_value = value
        if curr_value == 0:
            other_diseases_dict[key] = clips.Symbol('no')
        elif curr_value == 1:
            other_diseases_dict[key] = clips.Symbol('yes')
        elif curr_value == '':
            other_diseases_dict[key] = clips.Symbol('unknown')
            # this doesn't seem to ever get used but leaving it in for robustness

    # populate those into the templates using assert_fact
    patient_endo_template.assert_fact(**endo_dict)
    patient_concomitant_disease_template.assert_fact(**other_diseases_dict)

    env.run()
    facts_present = pull_facts(env)

    for idx, fact in enumerate(env.facts()):
        if idx == 0:
            endo_pred = fact['meets_criteria']
        elif idx == 1:
            concomitant_pred = fact['meets_criteria']

    results_data = data.loc[index, ['endometriosis', 'adenomyosis', 'ibs', 'interstitial_cystitis']]

    # ONLY END PRED (A) -> CASES (1)
    classification = None
    if endo_pred == clips.Symbol('yes') and concomitant_pred == clips.Symbol('no'):
        # tabulate_actual_results('A')
        classification = 1.0
        explanation = pull_explanation('yes', 'no')
        predicted_phenotype.append(1.0)
    # BOTH ENDO CONCOMITANT PRED (C) -> CASES (1)
    elif endo_pred == clips.Symbol('yes') and concomitant_pred == clips.Symbol('yes'):
        # tabulate_actual_results('C')
        classification = 1.0
        explanation = pull_explanation('yes', 'yes')
        predicted_phenotype.append(1.0)
    # ONLY CONCOMITANT PRED (B) -> CONTROLS (0)
    elif endo_pred == clips.Symbol('no') and concomitant_pred == clips.Symbol('yes'):
        # tabulate_actual_results('B')
        classification = 0.0
        explanation = pull_explanation('no', 'yes')
        predicted_phenotype.append(0.0)
    # NEITHER PRED (D) -> CONTROLS (0)
    elif endo_pred == clips.Symbol('no') and concomitant_pred == clips.Symbol('no'):
        # tabulate_actual_results('D')
        classification = 0.0
        explanation = pull_explanation('no', 'no')
        predicted_phenotype.append(0.0)

    output_df = pd.concat([pd.DataFrame([[classification,explanation]], columns=output_df.columns), output_df], ignore_index=True)


print(predicted_phenotype)

filename = './data/output/classifications.csv'
output_df.to_csv(filename, index=False)