'''

  sträucher, arbustos, shrubs
  baum, árbol/Arboles, tree
  gras, hierba, grass 


'''

import requests
import re 
from bs4 import BeautifulSoup
import pandas as pd 


MAX_RETRY = 5
INPUT_FILENAME = 'names'
XLSX_FILENAME = 'data'
MAX_GENINFO_LEN = 300
WFO_URL = 'https://www.worldfloraonline.org/taxon/wfo-'

requests.packages.urllib3.disable_warnings()

# cookies = {
#     '_gid': 'GA1.2.915583917.1702651974',
#     'JSESSIONID': '4EEB3616EDD8C679A98CBB018EFB3DB3',
#     '_gat_gtag_UA_114340265_1': '1',
#     '_ga_4LYR7CZFD6': 'GS1.1.1702693795.2.1.1702698330.0.0.0',
#     '_ga': 'GA1.1.1154062738.1702651974',
# }

def find_wfo_all_id(name='Pinus sylvestris') -> list[str]: 

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'close', 
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    params = {
        'query': name,
        'limit': '10',
        'start': '0',
        # 'sort': '_asc',
        'sort': '',
    }

    t = 0
    response = None 

    while t < MAX_RETRY: 
        
        try: 
            response = requests.get('https://www.worldfloraonline.org/search', 
                                    params=params, 
                                    # cookies=cookies, 
                                    headers=headers, 
                                    verify=False, 
                                    # timeout=10, 
                                    )
        except requests.exceptions.SSLError as ssle: 
            print('\tSearch SSLError...', end='')
            t += 1
            print("\tretry {}".format(t))
        
        if response != None and response.status_code == 200: 
            print('\tok')
            break 

    if t == MAX_RETRY: 
        return []


    # with open('out.html', 'w') as f: 
    #     f.write(response.text)

    html = response.text
    pattern = r"/taxon/wfo-(\d+)"

    # match = re.search(pattern, html)
    matches = re.findall(pattern, html)

    # for match in matches:
    #     print(match)

    return matches


def find_wfo_id(name='Pinus sylvestris') -> str:
    tmp = ''
    try: 
        tmp = find_wfo_all_id(name)[0]
    except IndexError as ie: 
        # print('\tempty.')
        pass 
    return tmp 


def get_detail(id): 
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        'Connection': 'close',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    t = 0
    response = None 

    while t < MAX_RETRY: 
        try: 
            response = requests.get(WFO_URL + id, 
                                    # cookies=cookies, 
                                    headers=headers, 
                                    verify=False)
        except requests.exceptions.SSLError as ssle: 
            print('\tDetail SSLError...', end='')
            t += 1
            print("retry {}".format(t))
        
        if response != None and response.status_code == 200: 
            print('\tok')
            break 

    if t == MAX_RETRY: 
        return ''
    
    # print(response)
    # with open('out2-3.html', 'w') as f: 
    #     f.write(response.text)
    return response.text 


def get_by_name(name): 

    wfo_id = find_wfo_id(name)
    if len(wfo_id) == 0:
        print('\tempty wfo id.')
        return (name, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A')
    
    detail = get_detail(wfo_id)

    text = BeautifulSoup(detail, features='html.parser').get_text()

    text = text.replace('\t', ' ').lower()

    is_tree = 'N' 
    is_shrubs = 'N'
    is_grass = 'N'

    # baum, árbol/Arboles, tree
    if text.find('tree') != -1 or text.find('baum') != -1 \
        or text.find('arboles') != -1 or text.find('árbol') != -1: 
        print('tree')
        is_tree = 'Y'

    #   sträucher, arbustos, shrubs
    if text.find('shrubs') != -1:
        print('shrubs')
        is_shrubs = 'Y'

    # Gras, hierba, grass 
    if text.find('grass') != -1 or text.find('gras') != -1 or text.find('hierba') != -1: 
        print('grass')
        is_grass = 'Y'

    info = ''
    idx = text.find('general information')
    if idx != -1:
        info = text[idx + 19 : (idx + 19 + MAX_GENINFO_LEN)] + '...'

    # general_info.append(info)

    typeinfo = ''
    if is_tree == 'Y': 
        typeinfo += 'tree or '
    
    if is_shrubs == 'Y': 
        typeinfo += 'shrubs or '
    
    if is_grass == 'Y': 
        typeinfo += 'grass or '

    typeinfo = typeinfo.strip()
    if typeinfo.endswith('or'): 
        typeinfo = typeinfo[:-2]

    return (name, is_tree, is_shrubs, is_grass, typeinfo, WFO_URL+wfo_id, info)

# scientific_name, is_tree, is_shrubs, is_grass, type, detail_url, general_info


names = []
with open('{}.txt'.format(INPUT_FILENAME), 'r') as f:
    names = f.readlines()

data = []
for name in names: 
    name = name.strip()
    if len(name) == 0:
        continue
    print('Finding "{}"...'.format(name))
    line = get_by_name(name)
    print(str(line)[:80])
    data.append(line)

# print(data)

df = pd.DataFrame(data, columns=[
                                "scientific_name", 
                                "is_tree", 
                                "is_shrubs", 
                                "is_grass", 
                                "type", 
                                "detail_url", 
                                "general_info" ])

print(df.head(3))
print('...')

df.to_excel("{}.xlsx".format(XLSX_FILENAME))
print('{} records are saved to ./{}.xlsx'.format(df.shape[0], XLSX_FILENAME))

