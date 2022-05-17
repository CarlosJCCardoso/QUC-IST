import requests
from bs4 import BeautifulSoup
from parseScriptQUC import getScriptAnswer



url = 'https://fenix.tecnico.ulisboa.pt/publico/viewCourseResults.do?executionCourseID=1690460473010771&degreeCurricularPlanOID=2581275345334'
r = requests.get(url)

soup = BeautifulSoup(r.text, 'html.parser')
tables = soup.findAll("table", { "class" : "graph neutral table" })

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

    return {'Resultados gerais da UC e estatísticas de preenchimento' : graph_dict}

# 1. Acompanhamento da UC ao longo do semestre/carga de trabalho da UC
# Para os alunos que indicaram acréscimo de carga de trabalho, a razão deveu-se a:
# Para os alunos que indicaram baixa carga de trabalho, a razão deveu-se a:
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
    
    return {'1. Acompanhamento da UC ao longo do semestre/carga de trabalho da UC' : both}

def parseNeutralTableHeaders(neutralTable):
    headers = []
    head = neutralTable.findAll("tr", {"class" : "thead"})
    ths = head[0].findAll("th")

    # Ignore first and last th
    for i in range(1, len(ths) -1):
        headers.append(ths[i].text.strip())

    return headers

def parseNeutralTableRow(row, headers):
    # Get first columns values
    values = []
    for i in range (1, len(headers) + 1):
        values.append(row.findAll("td", {"class" : f'x{i}'})[0].text.strip())
   
    # Get scores
    scores = []
    for i in range(1,10):
        scores.append(row.find("div", {"class": f'graph-bar-19-{i}'}).text)

    #{"N" : N, "Mediana": mediana , "scores" : scores}
    out = {}
    
    for i in range(0, len(headers)):
        out = out | {headers[i] : values[i]}

    out = out |  {"scores" : scores}

    return  out

def parseNeutralTable(neutralTable):
    info = {}
    headers = parseNeutralTableHeaders(neutralTable)

    trows = neutralTable.tbody.findChildren("tr" , recursive=False)

    # Ignore Table headers
    for i in range(1, len(trows)):
        title = trows[i].find("th").text.strip()
        row = { title : parseNeutralTableRow(trows[i], headers)}
        info = info | row

    # { '1.3.1 Assistir às aulas teóricas/seminário' : {'N': '5', 'Mediana': '7', 'Não se aplica': '65', 'scores': ['', '', '', '', '7%', '15%', '23%', '23%', '22%']}}
    
    #print(info)
    return info

# 1.2 Os conhecimentos anteriores foram suficientes para o acompanhamento desta UC
def getKnowledge(soup):
    tables = soup.findAll("table", { "class" : "graph neutral table" })
    table  = tables[0]

    rows = table.findAll("tr")
    headers = parseNeutralTableHeaders(table)

    info = parseNeutralTableRow(rows[2], headers)
    
    knowledge = {"1.2 Os conhecimentos anteriores foram suficientes para o acompanhamento desta UC": info}
    #print(knowledge)
    return knowledge

# 1.3 Caracterização do nível de importância que atribui aos meios de estudos, quando utilizados, nesta UC:
def getImportance(soup):
    tables = soup.findAll("table", { "class" : "graph neutral table" })
    neutralTable  = tables[1]
    
    info = parseNeutralTable(neutralTable)
    
    return {'1.3 Caracterização do nível de importância que atribui aos meios de estudos, quando utilizados, nesta UC' : info}

# 2. Organização da UC
def getOrganization(soup):
    organization = {}
    tables = soup.findAll("table", { "class" : "graph classification table" })
    classTable = tables[0]

    # Parsed in the same way as the NeutralTables
    organization = parseNeutralTable(classTable)

    return {'2. Organização da UC' : organization}


# 3. Método de avaliação da UC
def getEvaluationMethod(soup):
    evaluation = {}

    table = soup.findAll("table", { "class" : "graph-2col" })
    trs = table[0].findAll("tr")
    graph2col_dict = {'Nº de inscritos'   : trs[0].td.text.strip(), 
                      'Nº de aprovados'   : trs[1].td.text.strip(), 
                      'Taxa de aprovação' : trs[2].td.text.strip(), 
                      'Tx. de aprovação média no ano curricular do curso':  trs[3].td.text.strip(),
                      'Média classificações': trs[4].td.text.strip()}
    #print(graph2col_dict)

    # Get Classification Table
    tables = soup.findAll("table", { "class" : "graph classification table" })
    classTable = tables[1]

    # Parsed in the same way as the NeutralTables
    info = parseNeutralTable(classTable)

    evaluation = graph2col_dict | info

    return {'3. Método de avaliação da UC' : evaluation}


# 4. A UC contribuiu para a aquisição e/ou desenvolvimento das competências
def getDevelopment(soup):
    development = {}
    tables = soup.findAll("table", { "class" : "graph neutral table" })
    table  = tables[2]

    rows = table.findAll("tr")
    headers = parseNeutralTableHeaders(table)

    development = parseNeutralTableRow(rows[2], headers)
    
    return {'4. A UC contribuiu para a aquisição e/ou desenvolvimento das competências' : development}


answersQUC = getScriptAnswer(soup)
answersQUC['General Results'] = getGeneralResults(soup)     #0
answersQUC['Attendance'] = getAttendance(soup)              #1.1
answersQUC['Previous Knowledge'] = getKnowledge(soup)       #1.2
answersQUC['Importance'] = getImportance(soup)              #1.3
answersQUC['Organization'] = getOrganization(soup)          #2
answersQUC['Evaluation Method'] = getEvaluationMethod(soup) #3
answersQUC['Development'] = getDevelopment(soup)            #4

# 5. Corpo Docente


print(answersQUC)

# Usar esta linha para dar print "bonito" dos dados
# print(json.dumps(answersQUC["Grades"],indent = 4))