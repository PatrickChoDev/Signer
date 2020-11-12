import requests,json,os,threading,time


def loadJson(path='./tmp/raw.json') :
    with open(path) as json_file: 
        data = json.load(json_file)
    json_file.close()
    return data

def saveJson(data,path,method='w',clean=False) :
    if clean : open(path, 'w').close()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,method) as json_file:
        json.dump(data,json_file)
    json_file.close()

def fetchURL(keys='all',keytype='alp',url='Ralpx'):
    requestURL = 'http://www.e-tsl.com/'+url+'.php'
    if keytype == 'alp' :
        print('[Single Mode] Searching API for alp: ' + keys)
        r = requests.post(requestURL,data={keytype:keys})
        saveJson(r.json(),'./tmp/raw.json')
        print('[Single Mode] Wrote results of "' + keys + '" to ./tmp/raw.json')
    else :
        try:
            raise ValueError("This type of keywords isn't support at the moment")
        except ValueError :
            raise

def fetchSynonyms(word) :
    synonyms = []
    for syn in word['wrd_synonyms'] :
        if syn['1'] != '-' :
            synonyms.append(syn['1'])
    return synonyms

def fetchVideo(word) :
    for req in word['wrd_signs']:
        if req['sgn_video_normal'] :
            return req['sgn_video_normal']['0']
        # if requests.get('http://e-tsl.com/resources/Video/Video_'+str(req['sgn_video_normal']['0'])+'_0.mp4').status_code != 404 :
        #     return req['sgn_video_normal']['0']

def cleanJson(jsonFile) :
    data = {}
    data['count'] = jsonFile['count']
    data['result'] = {}
    for wordData in jsonFile['results'][:] :
        print('Finding : '+wordData['1'])
        data['result'][wordData['1']] = {}
        data['result'][wordData['1']]['synnonyms'] = fetchSynonyms(wordData)
        data['result'][wordData['1']]['video'] = fetchVideo(wordData)
    return data

def fetchAPI(alps,path='./tmp/API.json') :
    data = {}
    if os.path.exists(os.path.dirname(path)+'/raw.json'): os.rename(os.path.dirname(path)+'/raw.json',os.path.dirname(path)+'/raw.json.bak')
    if os.path.exists(os.path.dirname(path)+'/API.json'): os.rename(os.path.dirname(path)+'/API.json',os.path.dirname(path)+'/API.json.bak')
    for alp in alps :
        fetchURL(alp)
        data[alp] = cleanJson(loadJson())
    saveJson(data,'./tmp/API.json')

def loadVideo(f,limit=float('inf')) :
    with open(f,'r') as f:
        f = json.load(f)
        for alp in f.items() :
            os.makedirs('./Videos/e-tsl/'+alp[0],exist_ok=True)
            words = alp[1]
            for word in words['result'].items() :
                if word[0] == 'count' :
                    continue
                limit -= 1
                if limit < 0 : break
                print("Downloading : " + word[0] + '...')
                threading.Thread(target=videoDownloader,args=(alp[0],word)).start()
                time.sleep(0.5)

def videoDownloader(alp,word) :
    r = requests.get('http://www.e-tsl.com/resources/Video/Video_'+word[1]['video']+'_0.mp4')
    with open('./Videos/e-tsl/'+alp+'/'+word[0].split()[0]+'.mp4', 'wb') as fd:
        fd.write(r.content)
if __name__ == '__main__' :
    # THIS IS FOR TEST
    # fetchURL('ก')
    # data = loadJson('./tmp/API.json')
    # print(data)
    # data = cleanJson(data)
    # loadVideo(data['result'],4)
    # saveJson(data,'./tmp/data.json')
    fetchAPI('กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝฟภมยรลวศษสหฬอฮ')
    # fetchAPI('ย')
    loadVideo('./tmp/API.json')