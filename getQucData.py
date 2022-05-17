import requests
from bs4 import BeautifulSoup
from parseScriptQUC import getScriptAnswer


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
    graph_dict = {}
    table = soup.findAll("table", { "class" : "graph general-results table" })
    if table:
        tds = table[0].findAll("td")
        # Get table headers
        ths = table[0].findAll("th")
        if tds:
            for i in range(0, len(tds)):
                header = ths[i].contents[0].strip()
                value = barcolorToText(tds[i].div['class'][0])
                graph_dict = graph_dict | {header : value}

            return {'Resultados gerais da UC e estatísticas de preenchimento' : graph_dict}
        else:
            return {}
    else:
        return {}
        

def parseGraphTable(table):
    info = {}
    
    td_divs = table.findAll('div', {"class": "graph-bar-horz-number"})
    ths = table.findAll('th')

    if td_divs and ths:
        # "Nº de respostas: 12"
        answers = ths[0].text.split(":") 

        info = info | {answers[0].strip() : answers[1].strip()}

        # 'O programa não foi cumprido' : '0%'        
        for i in range(0, len(td_divs)):
            header = ths[i+1].text.strip()
            value = td_divs[i].text.strip()
            info = info | {header : value}
        
    return info

def parseGraph2colTable(table):
    graph2col_dict = {}
    if table:
        trs = table.findAll("tr")
        ths = table.findAll("th")
        if trs and ths:
            for i in range (0, len(trs)):
                header = ths[i].text.strip()
                value  = trs[i].td.text.strip()
                graph2col_dict = graph2col_dict | {header : value}

    return graph2col_dict


# 1. Acompanhamento da UC ao longo do semestre/carga de trabalho da UC
# Para os alunos que indicaram acréscimo de carga de trabalho, a razão deveu-se a:
# Para os alunos que indicaram baixa carga de trabalho, a razão deveu-se a:
def getAttendance(soup):
    tables = soup.findAll("table", { "class" : "graph table" })

    if (len(tables) == 2):
        table_high = tables[0]
        thigh_dict = parseGraphTable(table_high)
   
        table_down = tables[1]
        tdown_dict = parseGraphTable(table_down)

        both = {"Para os alunos que indicaram acréscimo de carga de trabalho, a razão deveu-se a" : thigh_dict,
                "Para os alunos que indicaram baixa carga de trabalho, a razão deveu-se a:"       : tdown_dict }
    
        return {'1. Acompanhamento da UC ao longo do semestre/carga de trabalho da UC' : both}
    else:
        return {}

def parseNeutralTableHeaders(neutralTable):
    headers = []
    head = neutralTable.findAll("tr", {"class" : "thead"})
    if head:
        ths = head[0].findAll("th")
        if ths:
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

    if table:
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

    # Get graph-2col table and parse
    table = soup.findAll("table", { "class" : "graph-2col" })
    graph2col_dict = parseGraph2colTable(table[0])

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
    neutralTable  = tables[2]

    development = parseNeutralTable(neutralTable)
    
    return {'4. A UC contribuiu para a aquisição e/ou desenvolvimento das competências' : development}


def getQUCdata(url):
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(e)
    else:
        soup = BeautifulSoup(r.text, 'html.parser')
        answersQUC = getScriptAnswer(soup)
        answersQUC['General Results'] = getGeneralResults(soup)     #0
        answersQUC['Attendance'] = getAttendance(soup)              #1.1
        answersQUC['Previous Knowledge'] = getKnowledge(soup)       #1.2
        answersQUC['Importance'] = getImportance(soup)              #1.3
        answersQUC['Organization'] = getOrganization(soup)          #2
        answersQUC['Evaluation Method'] = getEvaluationMethod(soup) #3
        answersQUC['Development'] = getDevelopment(soup)            #4

        # 5. Corpo Docente

        return answersQUC


def main():
    url = 'https://fenix.tecnico.ulisboa.pt/publico/viewCourseResults.do?executionCourseID=1690460473010771&degreeCurricularPlanOID=2581275345334'
    answersQUC = getQUCdata(url)
    #print(answersQUC)
    print(answersQUC["Evaluation Method"])

if __name__ == "__main__":
    main()