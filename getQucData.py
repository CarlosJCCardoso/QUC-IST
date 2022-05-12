import requests
from bs4 import BeautifulSoup

url = 'https://fenix.tecnico.ulisboa.pt/publico/viewCourseResults.do?executionCourseID=1690460473010771&degreeCurricularPlanOID=2581275345334'
r = requests.get(url)

soup = BeautifulSoup(r.text, 'html.parser')

def barcolorToText(barcolor):
    # Verde   - De acordo com o previsto
    # Amarelo - Acima do previsto
    # Roxo    - Abaixo do previsto
    # Cinza   - Sem representatividade
    if( barcolor == 'bar-green'):
        return 'De acordo com o previsto'
    elif( barcolor == 'bar-purple'):
        return 'Acima do previsto'
    elif( barcolor == 'bar-yellow'):
        return 'Abaixo do previsto'
    elif( barcolor == 'bar-grey'):
        return 'Sem representatividade'
    return 'Erro'


# Resultados Gerais
def getGeneralResults(soup):
    table = soup.findAll("table", { "class" : "graph general-results table" })
    tds = table[0].findAll("td")

    graph_dict = {'Carga de trabalho': barcolorToText(tds[0].div['class'][0]), 
                  'Organização da UC': barcolorToText(tds[1].div['class'][0]), 
                  'Avaliação da UC'  : barcolorToText(tds[2].div['class'][0]), 
                  'Docência da UC'   : barcolorToText(tds[3].div['class'][0])}

    print(graph_dict)
    return graph_dict

# 3. Método de avaliação da UC
def getEvaluationMethod(soup):
    table = soup.findAll("table", { "class" : "graph-2col" })
    trs = table[0].findAll("tr")
    graph2col_dict = {'Nº de inscritos'   : trs[0].td.text.strip(), 
                      'Nº de aprovados'   : trs[1].td.text.strip(), 
                      'Taxa de aprovação' : trs[2].td.text.strip(), 
                      'Tx. de aprovação média no ano curricular do curso':  trs[3].td.text.strip(),
                      'Média classificações': trs[4].td.text.strip()}
    print(graph2col_dict)
    return graph2col_dict

getGeneralResults(soup)
getEvaluationMethod(soup)


