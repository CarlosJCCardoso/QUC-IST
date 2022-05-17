import encodings
import requests
import json


def getDegrees(academic_term = '2021/2022'):
    url = f'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/degrees?academicTerm={academic_term}'
    degrees = []
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e: 
        raise SystemExit(e)
    else:
        data = r.json()
        for i in range (0, len(data)):
            try:
                id   = data[i]['id']
                name = data[i]['name']
            except:
                print("error")
            else:
                degrees.append({'id': id, 'name': name})
    return degrees


def getCoursesFromDegree(degree_id, academic_term = '2021/2022'):
    courses = []
    url = f'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/degrees/{degree_id}/courses?academicTerm={academic_term}'

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e: 
        raise SystemExit(e)
    else:
        data = r.json()
        for i in range(0, len(data)):
            try:
                id           = data[i]['id']
                name         = data[i]['name']
                acronym      = data[i]['acronym']
                academicTerm = data[i]['academicTerm']
                credits      = data[i]['credits']
            except:
                print("error")
            else:
                courses.append({'id': id, 'name': name, 'acronym' : acronym, 'academicTerm':academicTerm, 'credits': credits})

    return courses



def main():
    all = []

    degrees = getDegrees()
    with open('degrees.json', 'w',  encoding='utf-8') as json_file:
        json.dump(degrees, json_file, indent=4, ensure_ascii=False)

    for i in range(0, 10):
        courses = getCoursesFromDegree(degrees[i]['id'])
        all.append({'id' : degrees[i]['id'] , 'name' : degrees[i]['name'], 'courses' : courses})

    with open('degrees_courses.json', 'w',  encoding='utf-8') as json_file:
        json.dump({'degree' : all}, json_file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
