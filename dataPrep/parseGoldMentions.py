import pickle
import os
import sys
from ssf_api import *

path = sys.argv[1]
files = os.listdir(path)

class Chain:
    def __init__(self, chainId):
        self.chainId = chainId
        self.mentionList = []
        self.chainHead = None

class Mention:
    def __init__(self, mentionId, chainId, mentionHead=None, crefType=None, antecedentType=None, crefMod=None):
        self.mentionId = mentionId
        self.chainId = chainId
        self.tokenList = []
        self.mentionHead = None
        self.relType = None
        self.antecedentId = None
        self.crefMod = None

#DOUBT: Can we have them cref fields in mod mentions??
class modMention:
    def __init__(self, mmid):
        self.modMentionId = mmid
        self.tokenList = []

class Token:
    def __init__(self, tokenId):
        self.tokenId = tokenId
        #self.string = string
        #self.featureDict = featureDict

def checkToken(fs, curmentionId):
    #print fs
    if 'cref' in fs:
        mannotations = fs['cref'].split(',')
        for iann, ann in enumerate(mannotations):
            if ann.split("%")[0]==curmentionId:
                return iann
    return None

def processMention(i, j, globalWordList, mentionIds, chains, chainObjs):

    #get word
    word = globalWordList[i]
    fs = word.featureSet.featureDict

    #get cref anno
    #print 'word, posn', i, word.word, j
    #print word.featureSet.featureDict
    mInfo, chainId = fs['cref'].split(',')[j].split(':')
    curmentionId = mInfo.split('%')[0]
    
    #Already processed
    if curmentionId in mentionIds:
        #print 'ouch'
        return

    if chainId not in chains:
        chains += [chainId]
        chainObjs+=[Chain(chainId)]

    #Create mention
    #print 'mentionstart'
    mention = Mention(curmentionId, chainId)                

    mode = 1

    #Add tokens
    while mode==1:
        word = globalWordList[i]
        fs = word.featureSet.featureDict

        #checks if this token has annotation for curmention
        iann = checkToken(fs, curmentionId)
        if iann is None:
            i+=1
            continue

        mentionId, bio = fs['cref'].split(',')[iann].split(':')[0].split('%')
        mention.tokenList += [Token(i)]
        
        if 'crefhead' in fs.keys():
            #print '.'*10
            if fs['crefhead'].split(':')[1]==curmentionId:
                mention.mentionHead = i
                #The coref relations for the mention
                if 'creftype' in fs:
                    brrp = fs['creftype'].split(':')
                    if len(brrp)>2:
                        print word.sentenceNum
                        print '  '.join([key + ':' + fs[key] for key in fs])
                    relType, antecedentId = brrp[:2]
                    mention.relType = relType
                    mention.antecedentId = antecedentId

        #if 'creftype' in fs.keys() :

        if 'chainhead' in fs.keys():
            if fs['chainHead'].split(':')[0]==curmentionId:
                chainObjs[chains.index(chainId)].chainHead = mentionId
            
        if bio=='1':
            mode=0
            #print 'mentionend'
            mentionIds += [curmentionId]
            chainObjs[chains.index(chainId)].mentionList += [mention]

        i+=1

errs = []
for fil in files:
    #if '2484354' in fil or '4344896' in fil or '3128589' in fil or '2484342' in fil or '2561785' in fil or '2585727' in fil or '2575966' in fil:
    #    continue

    if '2561785' in fil or '2583308' in fil:
        continue

    print '\n'
    print '>'*20, fil

    f= pickle.load(open(path+fil))
    sList = f.sentenceList
    globalWordList = f.globalWordList
    mentionIds = []
    chains = []
    chainObjs = []
    for sent in sList:
        #print '\n\n', sent.sentenceNum
        for i in sent.wordNumList:
            word = globalWordList[i]
            fs = word.featureSet.featureDict
            if 'cref' in fs.keys():
             for j in range(len(fs['cref'].split(','))):
                 processMention(i, j, globalWordList, mentionIds, chains, chainObjs)

    #except Exception as e:
    #    errs += [(fil, e)]
    
    pickle.dump(chainObjs, open('processedData/mentionsPickled/'+fil+'.coref','w'))

#exit()

print fil

for chain in chainObjs:
    print 'chainId:', chain.chainId
    for mention in chain.mentionList:
        print 'mention : ', mention.mentionId
        print mention.relType, mention.antecedentId
        print mention.chainId
        for tk in mention.tokenList:
            print globalWordList[tk.tokenId].word
        print '*'*20
