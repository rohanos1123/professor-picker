from PDF_Reader import Get_Gator_Eval_Data
import numpy as np 

def KL_Diverge(Q, M):
    # Make sure that the M matrix is has no zero Entries:
    if np.all(M == 0):
        raise Exception("JSD Calcualtion failed, probability vector has 0")
    else:
        KL_score = np.sum(Q * np.log(Q / M), axis=1)

    return KL_score

def Get_Close_Divergence(Query_Vect, Search_Matrix, Name_List, total_scores, ts_weight, k,
    JSD_Sim_Weight = 2, scaler = 'exponential'):
    # Use the JSD Convergence to get similarity between prob vectors
    # Multiply by the total_score_weight

    M = 1/2 * (Search_Matrix + Query_Vect)
    Resultant = 1/2 * KL_Diverge(Query_Vect, M) + 1/2 * KL_Diverge(Search_Matrix, M)
    
    
    if(scaler == 'exponential'):
        Resultant =(Resultant ** JSD_Sim_Weight) * 1/(np.exp(total_scores * ts_weight))
    else:
        Resultant = (Resultant ** JSD_Sim_Weight) * 1/(np.exp(total_scores) * ts_weight)

    Selected_Names = Name_List[np.argsort(Resultant)[0:k]]

    return list(Selected_Names)


# Gets K closest professors using the Gator Evals metric
# TODO: EDIT AND PLAY AROUND WITH WEIGHT HYPERPARAMETERS

def Get_Closest_PROF_GE(query_vector, prof_quality_weight, k):
    Data_Extract = Get_Gator_Eval_Data()

    scaled_vects = Data_Extract["GE_VECTOR"]
    sum_weights = Data_Extract["SUM_WEIGHTS"]
    name_list = Data_Extract["NAME_LIST"]

    # perform the JSD with each of the scaled prob vectors: 

    return Get_Close_Divergence(query_vector, scaled_vects, name_list, 
    sum_weights, prof_quality_weight, k, JSD_Sim_Weight = 4, scaler = 'linear')



