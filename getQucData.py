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

# 1. Acompanhamento da UC ao longo do semestre/carga de trabalho da UC
# Para os alunos que indicaram acréscimo de carga de trabalho, a razão deveu-se a:
def getAttendance(soup):
    tables = soup.findAll("table", { "class" : "graph table" })

    table_high = tables[0]
    td_divs = table_high.findAll('div', {"class": "graph-bar-horz-number"})
    thigh_dict = {'Trabalhos/projectos complexos'                             : td_divs[0].text, 
                  'Trabalhos/projectos extensos'                              : td_divs[1].text, 
                  'Trabalhos/projectos em número elevado'                     : td_divs[2].text, 
                  'Falta de preparação anterior exigindo mais trabalho/estudo': td_divs[3].text,
                  'Extensão do programa face ao nº de aulas previstas'	 	  : td_divs[4].text,
                  'Pouco acompanhamento das aulas ao longo do semestre'       : td_divs[5].text,
                  'Problemas na organização da UC'	                          : td_divs[6].text,
                  'Problemas pessoais / com os colegas de grupo'              : td_divs[7].text,
                  'Outras razões'                                             : td_divs[8].text,
                  }

    table_down = tables[1]
    td_divs = table_down.findAll('div', {"class": "graph-bar-horz-number"})
    tdown_dict = {'O programa não foi cumprido'                               : td_divs[0].text, 
                  'O programa foi pouco extenso'                              : td_divs[1].text, 
                  'A matéria já tinha sido leccionada noutra UC'              : td_divs[2].text,
                  'Frequência de UC em repetência'                            : td_divs[3].text,
                  'Trabalho excessivo noutras UC'	 	                      : td_divs[4].text,
                  'Avaliação pouco exigente'                                  : td_divs[5].text,
                  'Boa organização da UC'	                                  : td_divs[6].text,
                  'Outras razões:'                                            : td_divs[7].text, 
                  }

    both = {"Para os alunos que indicaram acréscimo de carga de trabalho, a razão deveu-se a" : thigh_dict,
            "Para os alunos que indicaram baixa carga de trabalho, a razão deveu-se a:"       : tdown_dict }
    
    print(both)
    return both

# Os conhecimentos anteriores foram suficientes para o acompanhamento desta UC
def getKnowledge(soup):
    tables = soup.findAll("table", { "class" : "graph neutral table" })
    table  = tables[0]
    N       = table.findAll("td", {"class" : "x2"})[0].text.strip()
    mediana = table.findAll("td", {"class" : "x1"})[0].text.strip()

    scores = []
    for i in range(1,10):
        scores.append(table.find("div", {"class": f'graph-bar-19-{i}'}).text)
    
    knowledge = {"Os conhecimentos anteriores foram suficientes para o acompanhamento desta UC": {"N" : N, "Mediana": mediana , "scores" : scores}}
    print(knowledge)
    return knowledge


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
getAttendance(soup)
getKnowledge(soup)


