from bs4 import BeautifulSoup
from RMP_Scraper import RMPScraper
import requests
import re
import json


# GET THE RATE MY PROFESSOR DATA:





math_dept_professors = "https://math.ufl.edu/people/faculty-2-2/"
comp_sci_dept_professors = "https://www.cise.ufl.edu/people/faculty/"
phy_dept_professors = "https://www.phys.ufl.edu/wp/index.php/people/faculty/"



def Get_Math_Professors():
    math_name_list = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    html_set = requests.get(math_dept_professors, headers=headers).text
    prof_soup = BeautifulSoup(html_set, features='lxml')
    prof_list = prof_soup.find_all('td', class_="column-2")
    for prof in prof_list:
        a_tag = prof.find_all('a')
        if a_tag:
            name_cont = a_tag[0].text
            name_list = name_cont.split(",")
            if len(name_list) == 2:
                math_name_list.append(name_list[1] + ' ' + name_list[0])

    return math_name_list


def Get_Comp_Sci_Professors():
    comp_sci_list = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    html_set = requests.get(comp_sci_dept_professors, headers=headers).text
    prof_soup = BeautifulSoup(html_set, features='lxml')
    prof_list = prof_soup.find_all('p', class_="wp-show-posts-entry-title")
    for prof in prof_list:
        prof_name = prof.find('a').text.split(",")[0]
        comp_sci_list.append(prof_name)

    return comp_sci_list


def GET_RMP_PROFESSOR_MAP(target_name, target_dept):
    new_name = target_name.replace(' ', '%20')
    page = requests.get("https://www.ratemyprofessors.com/search/professors/1100?q=" + new_name).text
    bsoup = BeautifulSoup(page, features='lxml')
    script_subset = bsoup.find_all('script')

    # TODO: NOTE ASSUMPTION THAT THE PROFESSOR NAME IS UNIQUE FOR DEPARTMENT IN UF

    teacher_json = re.findall(r"(?<=\"__typename\":\"Teacher\",)(.*?)(?=,\"client)", str(script_subset))

    for i in range(len(teacher_json)):
        leg_id_extract = re.findall(r"(?<=\"legacyId\":)(.*?)(?=,)", teacher_json[i])
        dept_extract = re.findall(r"(?<=\"department\":\")(.*?)(?=\",)", teacher_json[i])
        hasName = re.findall(r"University of Florida", teacher_json[i])

        # Scroll through candiate lists and the\
        if hasName:
            for i in range(len(dept_extract)):
                if dept_extract[i].lower() == target_dept.lower():
                    return leg_id_extract[i]

    return "NO_MATCH"


def GET_RMP_DATA_MEGA_FUNCTION(debug_count=-1):
    # Part 1: Contains the functions to scroll each website and extract data from each
    # TODO: ADD CUSTOM EXTRACT FUNCTIONS FOR PHYSICS AND ADD TO LIST:
    comp_sci_profs = Get_Comp_Sci_Professors()
    math_profs = Get_Math_Professors()
    Dept_Dictionary = {"COMPUTER SCIENCE": comp_sci_profs, "MATHEMATICS": math_profs}
    Review_Dictionary = {"COMPUTER SCIENCE" : {}, "MATHEMATICS" : {}}
    count = 0
    for dept_name in Dept_Dictionary.keys():
        prof_name_list = Dept_Dictionary[dept_name]
        for prof_name in prof_name_list:
            ProfGetter = RMPScraper()
            # Store the RMP ID map here
            RMP_MAP = GET_RMP_PROFESSOR_MAP(prof_name, dept_name)
            if RMP_MAP != "NO_MATCH":
                try:
                    review_list = ProfGetter.Get_Prof_Reviews(RMP_MAP)
                    Review_Dictionary[dept_name].update({prof_name : review_list})
                    print("Read : ", prof_name)
                except:
                    print("Failed to get ", prof_name)


            count += 1

            if debug_count != -1 and count >= debug_count:
                return Review_Dictionary

    return Review_Dictionary


RATE_MY_PROF_DATA = GET_RMP_DATA_MEGA_FUNCTION()

# WRITE THE RMP DATA TO JSON:
with open("RMP_Results/Review_JSONS.json", "w") as outfile:
    json.dump(RATE_MY_PROF_DATA, outfile)












