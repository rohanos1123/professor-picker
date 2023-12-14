from flask import json
from flask.json import tag
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS 
from PDF_Reader import Get_Gator_Eval_Data
from NeighborAlgorithm import Get_Close_Divergence
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import numpy as np
from scipy.linalg import diagsvd
from transformers import BertModel, BertTokenizer
import torch



''' 
HELPER METHODS (NOT API)
'''
Data_Extract = Get_Gator_Eval_Data()

scaled_vects = Data_Extract["GE_VECTOR"]
sum_weights = Data_Extract["SUM_WEIGHTS"]
name_list = Data_Extract["NAME_LIST"]

RMP_Embeddings_str = "Professor_Embedding.json"
f = open(RMP_Embeddings_str)
RMP_BERT_EMBEDDINGS =  json.load(f)

# Representative sentences based of RMP reviews
REPRESENTATITVE_TAGS = [
    "Tough Grader", 
    "Requires Reading", 
    "Participation Reccomended", 
    "Extra Credit", 
    "Group Projects", 
    "Great Lectures",
    "Clear Grading Critera",
    "Provides Feedback",
    "Generally Hard", 
    "Generally Easy", 
    "Caring Professor",
    "Test Heavy"
]


REPRESENTATIVE_SENTENCES = [
    "This professor is a tough grader.", 
    "This class requires a lot of reading.", 
    "Make sure to participate a lot in this class.", 
    "The professor gives us extra credit.", 
    "There are a lot of group projects in this course.", 
    "The Lectures are great and informative, the professor can explain well.", 
    "The grading criteria is easy to understand.", 
    "The professor gives feedback in a good and timely manner.", 
    "This class was difficult and required a lot of effort.", 
    "This class did not require too much effort.",
    "This professor was kind, understaning, and caring.",
    "Exams made up majority of the class grade"
]

def Calculate_REP_SENT_Embeddings():
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained("bert-base-uncased")

    tag_list = list(zip(REPRESENTATITVE_TAGS, REPRESENTATIVE_SENTENCES)) 
    tag_embed_pairs = []


    for tag, sent in tag_list: 
        bert_input = tokenizer(sent, return_tensors="pt")

        with torch.no_grad():
            outputs = model(input_ids=bert_input['input_ids'], attention_mask=bert_input['attention_mask'])
            new_embedding = torch.mean(outputs.last_hidden_state, dim=1)[0]
            tag_embed_pairs.append((tag, new_embedding))

    return tag_embed_pairs 


def Calculate_Classification_Vector(Prof_Embeddings, tag_embed_pairs, n_eig):
    # Perform SVD Decomp on embeddings
    Prof_Embeddings = np.array(Prof_Embeddings)
    if Prof_Embeddings.shape[0] != 768: 
        Prof_Embeddings = Prof_Embeddings.T
    
    U,S,Vt = np.linalg.svd(Prof_Embeddings)
    S = diagsvd(S, *Prof_Embeddings.shape)

    Topic_Score = []
    Tag_List = []

    n_Principal_Components = U.T[0:n_eig]

    for tag, embedding in tag_embed_pairs: 
        # Form Projection vector of tag embedding with eigensubspace
        tag_projection = np.zeros(U.shape[0])
        for col in n_Principal_Components: 
            tag_projection += (np.dot(embedding, col) * col)
        
        # Cosine Similarity
        cos_sim = np.dot(tag_projection, embedding)/(np.linalg.norm(tag_projection) * np.linalg.norm(embedding))
        Topic_Score.append(cos_sim)

        
        # vect_difference = tag_projection - embedding.numpy()
        # projection_ratio =  1 - np.linalg.norm(vect_difference)/np.linalg.norm(embedding)
        # Topic_Score.append(projection_ratio)


        Tag_List.append(tag)

    Topic_Score = np.array(Topic_Score)
    Tag_List = np.array(Tag_List)

    desc_order_index = np.flip(np.argsort(Topic_Score)) 
    Topic_Score = Topic_Score[desc_order_index]
    Tag_List = Tag_List[desc_order_index]

    return list(zip(Tag_List.tolist(), Topic_Score.tolist()))






      
        
    


'''
 CONSTANT VARIABLES AND FILE LOADING
'''

# Running out of names here 
TAG_SENT_EMBEDDINGS = Calculate_REP_SENT_Embeddings() 



'''
API CODE 
'''



app = Flask(__name__)
CORS(app)

# Used to determine the maximum value for Perplexity
@app.route("/api/GetDataLength", methods=["POST"])
def GetDataLength():
    data = request.get_json() 
    dept_name = data["dept_name"].upper()
    prof_name = data["prof_name"]

    Prof_Embeddings = np.array(RMP_BERT_EMBEDDINGS[dept_name][prof_name]) 
    return jsonify({"max" : Prof_Embeddings.shape[0]})



# Get th
@app.route("/api/ClusterEmbeddings", methods=["POST"])
def Cluster_Embeddings():
    data = request.get_json() 
    Cluster_Num = int(data["Cluster_Num"])
    dept_name = data["dept_name"].upper()
    prof_name = data["prof_name"]
    color_code = np.array(["red", "blue", "green", "pink", "purple", "orange", "brown",
    "black", "yellow", "cyan"])

    # Get the professor embeddings for them 
    Prof_Embeddings = np.array(RMP_BERT_EMBEDDINGS[dept_name][prof_name]) 


    K_means_obj = KMeans(n_clusters = Cluster_Num)
    clusters_labels = K_means_obj.fit_predict(Prof_Embeddings)
    color_code_list = color_code[clusters_labels]

    # Produce Cluster Wise Categorization vectors
    classification_vectors = [] 
    for i in range(Cluster_Num): 
        Clustered_Embeddings = Prof_Embeddings[clusters_labels == i]
        res_class = Calculate_Classification_Vector(Clustered_Embeddings, TAG_SENT_EMBEDDINGS,
                                                                  15)
        classification_vectors.append((i, res_class))


    return jsonify({"Point_Color_Codes" : color_code_list.tolist(), 
                   "Resultant Classifcation Vectors" : classification_vectors})

                

@app.route("/api/TSNE_Visualization", methods = ["POST"])
def TSNE_Visualiation(): 
    data = request.get_json()
    print(data)
    dept_name = data["dept_name"].upper()
    prof_name = data["prof_name"]
    tsne_perplexity = int(data['tsne_perplexity'])

    Prof_Embeddings = np.array(RMP_BERT_EMBEDDINGS[dept_name][prof_name]) 

    tsne_obj = TSNE(n_components = 2, perplexity = tsne_perplexity)

    E2 = tsne_obj.fit_transform(Prof_Embeddings)

    return jsonify({"x_data" : E2.T[0].tolist(), "y_data" : E2.T[1].tolist()})


@app.route("/api/Get_Nearest_GE", methods = ["POST"])
def Get_Nearest_Vector(): 
    # Establish CONSTANT values for weights: 
    
    '''
        HYPERPARAMETERS: 
    '''

    # Constant Weight value placed on overall professor quality (average of scores)
    PROFESSOR_QUALITY_WEIGHT = 1

    # CONSTANT (Exponential) WEIGHT PLACED ON PROBABILITY SIMILARITY SCORE
    JSD_SIM_WEIGHT = 10

    # METHOD USED TO CALCULATE PROF WEIGHT:
    SCALAR_METHODS  = ['linear', 'exponential']
    SCALER_METH = SCALAR_METHODS[0]
    


    # Extract the query data from the json request

    data = request.get_json()
    query_vect = data["Scaled_Vect"]
    selected_Dept = data["Selected_Department"]

    # TODO: CHANGE TO A VALUE EXTRACT FROM FE JSON
    k = 5

    # Perform the JSD_Divergence_Algorithm to get the nearest neighbors (probability vectors)
    Closest_Profs = Get_Close_Divergence(query_vect, scaled_vects, name_list, sum_weights, 
    PROFESSOR_QUALITY_WEIGHT, 4, JSD_SIM_WEIGHT, scaler = SCALER_METH)


    return jsonify(Closest_Profs)

if __name__ == "__main__":


    app.run(debug=True)



