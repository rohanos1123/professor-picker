import PyPDF2
import re
import numpy as np
import os




def Get_Gator_Eval_Data():
    os.chdir("/Users/noham/Desktop/MAS 4115 FREE PROJ/prof-pull/Backend/Gator_Evals_Backend")
    # Test read directory_data:
    dir_list = os.listdir('PDFS')
    gator_eval_vector = []
    sum_list = []
    name_list = []

    for file_name in dir_list:
        try: 
            pdfFileObj = open('PDFS/' + file_name, 'rb')
            pdfReader = PyPDF2.PdfReader(pdfFileObj)
            pageObj = pdfReader.pages[0]
            pdf_string = pageObj.extract_text()
            pdf_string = pdf_string.replace('\n', '')
            pattern_string_extract = re.compile(r'(?:\d\.\d\d\d){10}')
            pattern_name_extract = re.compile(r'(?<=INSTRUCTOR_NAME)(.*)(?=RESPONSE)')
            numeric_string = pattern_string_extract.findall(pdf_string)[0]
            name_full = pattern_name_extract.findall(pdf_string)[0].replace('\t', '').split(",")
            name_value = name_full[1] + " " + name_full[0]

            number_list = []

            for i in range(0, len(numeric_string), 5):
                j = i + 4
                number_list.append(float(numeric_string[i : j]))
                rev_nl = np.array(number_list)

                eval_sum = np.sum(rev_nl)
                scaled_eval = rev_nl/eval_sum

                i = j

            pdfFileObj.close()

            gator_eval_vector.append(scaled_eval)
            sum_list.append(eval_sum)
            name_list.append(name_value)
        except: 
            print("Faulty: ",         file_name)

    return {"GE_VECTOR" : np.array(gator_eval_vector),
            "SUM_WEIGHTS" : np.array(sum_list)/10,
            "NAME_LIST" : np.array(name_list)}

