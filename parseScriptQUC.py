import requests
from bs4 import BeautifulSoup
import json5

#removes json attribute from string
def removeAttr(txt, attr):
    splited = txt.split(attr + ": {")
    
    removed = splited[0]
    for toRemove in splited[1:]:
        countBraces = 1
        for chars, i in zip(toRemove, range(len(toRemove))):
            if chars == '{':
                countBraces += 1
            elif chars == '}':
                countBraces -= 1
            if countBraces == 0:
                if len(toRemove) > i + 2 and toRemove[i+1] == ',':
                    i += 1
                removed += toRemove[i+1:]
                break
    return removed

#gets half of a string
def getHalf(txt, sep, firstHalf = False, warning = False):
    newText = txt.split(sep)
    if len(newText) != 2:
        if warning:
            print("ERROR IN READING SCRIPT - NO SEPARATOR")
        return ""
    if firstHalf:
        return newText[0]
    return newText[1]

#converts script arguments in string form to python dict
def scriptToJson(rawText):
    sep = """);
	});"""
	#ignores end of the string, produces warnings
    leftText = getHalf(rawText, sep, True, True)
	#removes problematic attributes from string
    rem1 = removeAttr(leftText, "plotOptions")
    rem2 = removeAttr(rem1, "tooltip")
    rem3 = removeAttr(rem2, "legend")
    return json5.loads(rem3)

#receives args of number of answers script, returns number of answers info
def getAnswered(answerScript):
    argsInJson = scriptToJson(answerScript)
    totalRespostasStr = argsInJson['subtitle']['text']
    totalRespostas = int(''.join(x for x in totalRespostasStr if x.isdigit()))
    answerPct = argsInJson['series'][0]['data']
    answerNo, answerYes = answerPct[0][1], answerPct[1][1]
    answerToForm = {'noAnswer' : round(answerNo * totalRespostas / 100), 
		'answer' : round(answerYes * totalRespostas / 100)}
    return answerToForm

#receives args of ects script, returns ects info
def getECTs(answerScript):
    argsInJson = scriptToJson(answerScript)
    data = argsInJson["series"]
    ectsPrevistos = {"Trabalho Autonomo":data[2]["data"][0], "Contacto":data[3]["data"][0]}
    ectsEstimados = {"Aulas":data[1]["data"][1], "Contacto":data[3]["data"][1], "Exames":data[0]["data"][1]}
    return {"ECTS Previstos": ectsPrevistos, "ECTS Estimados" : ectsEstimados}

#receives args of grade script, returns grades info
def getGrades(gradesScript):
    argsInJson = scriptToJson(gradesScript)
    xAxis = argsInJson['xAxis']['categories']
    dataReal = argsInJson['series'][0]['data']
    dataPrevisto = argsInJson['series'][0]['data']
    realDict, predictedDic = {}, {}
    for x, r, p in zip(xAxis, dataReal, dataPrevisto):
        realDict[x] = r / 100
        predictedDic[x] = p / 100

    return {"Grades Predicted" : predictedDic, "Real Grades": realDict}

#receives html in soup object return dict for QUC attributes
sepScript = '''var chart;
	jQuery(document).ready(function() {
	   chart = new Highcharts.Chart('''
def getScriptAnswer(soup):
    scriptAns = {}
    i = 0
    for link in soup.find_all('script'):
        scriptText = getHalf(link.get_text(), sepScript)
        if scriptText != "":
            if i == 0:
                scriptAns["nbrAnswers"] = getAnswered(scriptText)
            elif i == 1:
                scriptAns["ECTs"] = getECTs(scriptText)
            elif i == 2:
                scriptAns["Grades"] = getGrades(scriptText)
            i += 1
    return scriptAns


if __name__ == "__main__":
    response = requests.get("https://fenix.tecnico.ulisboa.pt/publico/viewCourseResults.do?executionCourseID=1690460473010886&degreeCurricularPlanOID=2581275345334")
    soup = BeautifulSoup(response.text, 'html.parser')
    scriptAnswers = getScriptAnswer(soup)
    print(scriptAnswers)