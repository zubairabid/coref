import pickle
import os
import sys
from ssf_api import *

class CheckFileError(Exception):
    pass

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
        self.mentionHead = mentionHead
        self.relType = crefType
        self.antecedentId = antecedentType
        self.crefMod = crefMod

class ModMention:
    def __init__(self, modmentionId, mentionId, modmentionHead=None ):
        self.modmentionId = modmentionId
        self.tokenList = []
        self.modmentionHead = modmentionHead
        self.mentionId = mentionId
#DOUBT: Can we have them cref fields in mod mentions??

class Token:
    def __init__(self, tokenId):
        self.tokenId = tokenId
        #self.string = string
        #self.featureDict = featureDict

def checkToken(fs, curmentionId):
    #print fs
    mannotations = fs['cref'].split(',')
    for iann, ann in enumerate(mannotations):
        if ann.split("%")[0]==curmentionId:
            return iann
    return None

def checkModToken(fs, curmodmentionId):
    #print fs
    mannotations = fs['acrefmod'].split(',')
    for iann, ann in enumerate(mannotations):
        if ann.split("%")[0]==curmodmentionId:
            return iann
    return None

def processMention(i, j, globalWordList):
    global mentions, chains

    word = globalWordList[i]
    fs = word.featureSet.featureDict
    mInfo, chainId = fs['cref'].split(',')[j].split(':')
    curmentionId = mInfo.split('%')[0]
    
    #Already processed
    if curmentionId in mentions.keys():
        return

    if chainId not in chains.keys():
        chains[chainId] = Chain(chainId)

    #Create mention
    #print 'mentionstart'
    mention = Mention(curmentionId, chainId)                
    mentions[curmentionId] = mention
    chains[chainId].mentionList += [curmentionId]
    mode = 1

    #Add tokens
    while mode==1:
        word = globalWordList[i]
        print '\t',word.word, fs
        fs = word.featureSet.featureDict
        
        #checks if this token has annotation for curmention
        iann = checkToken(fs, curmentionId)
        if iann is None:
            continue

        mentionId, bio = fs['cref'].split(',')[iann].split(':')[0].split('%')
        mention.tokenList += [Token(i)]
        
        if 'crefhead' in fs.keys() :
            #print '>'*50
            print fs['crefhead']
            if ',' in fs['crefhead']:
                print "heeee"*10
                for section in range(len(fs['crefhead'])):
                    if fs['crefhead'].split(',')[section].split(':')[1]==curmentionId:
                        mention.mentionHead = i
                        break
            else:
                if fs['crefhead'].split(':')[1]==curmentionId:
                    mention.mentionHead = i


        if 'creftype' in fs.keys() :
            if ',' in fs['creftype']:
                relType, antecedentId = fs['creftype'].split(',')[section].split(':')
            else:    
                relType, antecedentId = fs['creftype'].split(':')
            mention.relType = relType
            mention.antecedentId = antecedentId

        if 'chainhead' in fs.keys():
            if fs['chainhead'].split(':')[0]==curmentionId:
                chains[chainId].chainHead = mentionId
            
        if bio=='1':
            mode=0
            #print 'mentionend'

        i+=1

def processModMention(i, j, globalWordList):
    global mentions, modmentions
    
    word = globalWordList[i]
    fs = word.featureSet.featureDict
    modminfo, mid = fs['acrefmod'].split(',')[j].split(':')
    curmodmentionId = modminfo.split('%')[0]

    #Already processed
    if curmodmentionId in modmentions.keys():
        return

    #Create modmention
    #print 'mentionstart'
    modmention = ModMention(curmodmentionId, mid)                
    modmentions[curmodmentionId] = modmention
    mode = 1

    #Add tokens
    while mode==1:
        word = globalWordList[i]
        fs = word.featureSet.featureDict
        
        #checks if this token has annotation for curmention
        iann = checkModToken(fs, curmodmentionId)
        if iann is None:
            continue

        modmentionId, bio = fs['acrefmod'].split(',')[iann].split(':')[0].split('%')
        modmention.tokenList += [Token(i)]
        
        if 'acrefmodhead' in fs.keys() :
            #print '>'*50
            if fs['acrefmodhead'].split(':')[1]==curmodmentionId:
                modmention.modmentionHead = i

        if bio=='1':
            mode=0
            #print 'mentionend'

        i+=1


if __name__=='__main__':
    
    try:
        sourcepath = sys.argv[1]
        files = os.listdir(sourcepath)
        destpath = sys.argv[2]
    except:
        raise CheckFileError
        exit()

    mentions = {}
    chains = {}
    modmentions = {}
    for fil in files:
        #if '2474841' not in fil:
        #    continue
        f= pickle.load(open(sourcepath+fil))
        print fil
        sList = f.sentenceList
        globalWordList = f.globalWordList
        for sent in sList:
            print 'Sentence', sent.sentenceNum
            for i in sent.wordNumList:
                word = globalWordList[i]
                print word.word
                fs = word.featureSet.featureDict
                if 'cref' in fs.keys():
                    for j in range(len(fs['cref'].split(','))):
                        processMention(i, j, globalWordList)
                if 'acrefmod' in fs.keys():
                    for j in range(len(fs['acrefmod'].split(','))):
                        processModMention(i, j, globalWordList)

        filannos = {'chains':chains, 'mentions':mentions, 'modmentions':modmentions, 'fileid':fil}
        pickle.dump(filannos, open(destpath + fil, 'w'))
    '''
    for chain in chains:
        print 'chainId:', chains[chain].chainId
        for mentionname in chains[chain].mentionList:
            mention = mentions[mentionname]
            print 'mention : ', mention.mentionId
            print mention.relType, mention.antecedentId
            print mention.chainId
            for tk in mention.tokenList:
                print globalWordList[tk.tokenId].word
            print '*'*20
    for mmentionname in modmentions:
        modmention = modmentions[mmentionname]
        print modmention.modmentionId
        print modmention.mentionId
        print modmention.modmentionHead
        for tk in modmention.tokenList:
            print globalWordList[tk.tokenId].word
        print '>'*20
    '''
