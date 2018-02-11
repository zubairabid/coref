#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys
reload(sys)
import codecs
sys.setdefaultencoding("utf-8")
import os

#import re
#import ssf
#from util import *
from bs4 import BeautifulSoup

class SSFInfo():
    def __init__(self, sentenceList, globalWordList):
        self.sentenceList = sentenceList
        self.globalWordList = globalWordList


class Node():
    def __init__(self,node_name,node_relation,node_parent):
        self.nodeName=node_name
        self.nodeRelation=node_relation
        self.nodeParent=node_parent
        self.childList=[]
        self.nodeLevel=-1
        self.chunkNum=-1
    def addChild(self,child):
        self.childList.append(child)
    def getChunkName(self,node_name):
        i=len(node_name)
        while (node_name[i-1]>="0" and node_name[i-1]<="9"):
            i-=1
#		print "qwe",node_name,node_name[:i]
        return node_name[:i]

class Sentence():
    def __init__(self,sentence_num):
#		print "-"*30,"adding sentence"
        self.sentenceNum=sentence_num
        self.chunkList=[]
        self.wordNumList=[]
        self.nodeDict={}
        self.rootNode=[]
        return
    def addChunk(self,chunk):
#		print "-"*30,"adding chunk"
        self.chunkList.append(chunk)
    def addWord(self,word):
#		print "-"*30,"adding word to sentence"
        self.wordNumList.append(word)
    def addNode(self,node):
        print self.sentenceNum ,node.nodeName
        self.nodeDict[node.nodeName]=node
    def addChunkNumToNode(self,node_name,chunk_num):
        self.nodeDict[node_name].chunkNum=chunk_num

class Chunk():
    def __init__(self,tag,node_name,features_set,sentenceNum,chunk_num):
#		print "-"*30,"new chunk with tag - %s and f = %s"%(tag,features_string)
        self.chunkTag=tag
        self.chunkNum=chunk_num
        self.nodeName=node_name
        self.featureSet=features_set
        self.wordNumList=[]
        self.sentenceNum=sentenceNum
    def addWord(self,word):
#		print "-"*30,"adding word to chunk"
        self.wordNumList.append(word)
class Word():
    def __init__(self,word,tag,features_string,extra_features,sentenceNum,chunkNum):
#		print "-"*30,"new word- %s with tag - %s and f = %s"%(word,tag,features_string)
        self.wordTag=tag;
        self.word=word.decode("utf-8")
        self.featureSet=FeatureSet(features_string)
        self.extraFeatureSet=extra_features
        self.sentenceNum=sentenceNum
        self.chunkNum=chunkNum
        self.sense=None
        self.conn=False
        self.splitConn=False
        self.arg1=False
        self.arg2=False
        self.relationNum=None
        self.arg1Span=None
        self.arg2Span=None
class FeatureSet():
    def __init__(self,featureString):
        self.featureDict={}
        self.processFeatureString(featureString)
    def processFeatureString(self,featureString):
        featureSet=re.split(' ',featureString)
        featureSet=featureSet[1:]
        for feature in featureSet:
#			print feature
            feature=re.split('=',feature)
            key=feature[0]
            try:
                value=re.split('\'',feature[1])[1]
            except:
                value=re.split('\"',feature[1])[1]
	    	#print key,"=",value
            self.featureDict[key]=value

def createChildList(ssfinfo):
    for sent in ssfinfo.sentenceList:
        print sent.sentenceNum
        for i in sent.nodeDict:
            if sent.nodeDict[i].nodeParent!="None":
                sent.nodeDict[sent.nodeDict[i].nodeParent].childList.append(i)

def extractExtraSSF(filePath):
    filePath=filePath.replace("/ssf/","/ssf_1/") #ssf_1 has no chunk markings
    print filePath
    if not os.path.isfile(filePath) :
        print "No file found"
        return None
    fileFD=codecs.open(filePath,"r",encoding="utf-8")
    data=fileFD.read()
    fileFD.close()
    beautData = BeautifulSoup(data)
    sentenceList=beautData.find_all('sentence')
    sList=[]
    for sentence in sentenceList:
        content=sentence.renderContents()
        lines=re.split("\n",content)
        wList=[]
        for line in lines:
#			print line
            columns=line.split("\t")
            if(len(columns)<4):
                continue

            f=FeatureSet(columns[3])
#			try:
#				print "XXX",f.featureDict["af"]
#			except:
#				print "XXXhere"
            wList.append(f)
        sList.append(wList)
    return sList

def folderWalk(folderPath):
	fileList = []
	for dirPath , dirNames , fileNames in os.walk(folderPath) :
		for fileName in fileNames :
			fileList.append(os.path.join(dirPath , fileName))
	return fileList

def createDirectory(filePath):
	dirPath=os.path.dirname(filePath)
	print "here XXX",dirPath
	if not os.path.exists(dirPath):
		os.makedirs(dirPath)

def fetchLines(lines):
    lineset = []
    for line in lines:
        cols = line.split('\t')
        if len(cols)<4:
            continue
        else:
            lineset += [[cols[1], cols[2], FeatureSet(cols[3])]]
    return lineset

def fetchChunks(lines):
    chunkmarks = []
    start = -1
    pchunk = '-'
    for iline, line in enumerate(lines):
        chunk = line[2].featureDict['chunktype'].split(':')[1]
        if chunk != pchunk:
            if start!=-1:
                end = iline-1
                chunkmarks += [[start, end]]
            start = iline
            pchunk = chunk
    chunkmarks+=[[start, iline]]
    return chunkmarks    


def extractSSFannotations(filePath):
    if not os.path.isfile(filePath) :
        print "ExtractSSF: No file found"
        return (None,None)
    #extraInfoList=extractExtraSSF(filePath)
    #if(extraInfoList==None):
    #    print "ExtractSSFExtraSSF : No file found"
    #    return (None,None)
    fileFD=codecs.open(filePath,"r",encoding="utf-8")
    data=fileFD.read()
    fileFD.close()
    beautData = BeautifulSoup(data)
    sentenceList=beautData.find_all('sentence')
    sentenceInstList=[]
    globalWordList=[]
    sentenceNum=0
    wordNum=0
    for sentence in sentenceList:
        print '\n'*4
        #extraSentenceInfo=extraInfoList[sentenceNum]
        sentenceInst=Sentence(sentenceNum)
        content=sentence.renderContents()
        lines=re.split("\n",content)
        
        #Store lines as [[token, POS,FeatureSet]......]
        nlines = fetchLines(lines)
        #Store Chunk markings as [[start, end].....]
        chunks = fetchChunks(nlines)

        '''
        for chunk in chunks:
            for i in range(chunk[0], chunk[1]+1):
                print nlines[i][0], nlines[i][1] 
            print '\n', '*'*10
        '''

	#drel resolution
        for iline, line in enumerate(nlines):
            #print line
            featset = line[2]
            fdict = featset.featureDict
            if 'drel' in fdict.keys():
                drel = fdict['drel']
                #print drel
                ref = drel.split(':')[1]
                #print ref
                for isubline, subline in enumerate(nlines):
                    subfdict = subline[2].featureDict
                    if ref==subfdict['name']:
                        nref = subfdict['chunktype'].split(':')[1]
                        break
                fdict['drel'] = drel.split(':')[0]+':'+nref
            if 'dmrel' in fdict.keys():
                drel = fdict['dmrel']
                #print drel
                ref = drel.split(':')[1]
                #print ref
                for isubline, subline in enumerate(nlines):
                    subfdict = subline[2].featureDict
                    if ref==subfdict['name']:
                        nref = subfdict['chunktype'].split(':')[1]
                        break
                fdict['dmrel'] = drel.split(':')[0]+':'+nref

        print 'drels and dmrels resolved'

        chunkInst=None
        NodeInst=None
        wordInst=None
        chunkNum=-1
        skip=False
        wNum=0
        
        for chunk in chunks:
            #get head drel/dmrel and postag
            #Iteration for chunk start
            for i in range(chunk[0], chunk[1]+1):
                fdict = nlines[i][2].featureDict
                if fdict['chunktype'].startswith('head'):
                    postag = nlines[i][1]
                    
                    chunkid = fdict['chunkid']
                    fs = '<fs name=\''+chunkid+'\''
                    drel = None
                    dmrel = None
                    if 'drel' in  fdict.keys():
                        drel = fdict['drel']
                        fs = fs + ' drel=\''+drel+'\''
                    elif 'dmrel' in fdict.keys():
                        dmrel = fdict['dmrel']
                        fs = fs + ' dmrel=\''+dmrel+'\''
                    fs = fs+'>'
                    #print fs                   
                    featset = FeatureSet(fs)
            
            chunkNum+=1
            featureSetInst = featset
            chunkInst = Chunk(postag, chunkid, featset, sentenceNum, chunkNum)
            try:
                nodeInst=Node(featureSetInst.featureDict["name"],featureSetInst.featureDict["drel"].split(":")[0],featureSetInst.featureDict["drel"].split(":")[1])
            except Exception as e:
                try:
                    nodeInst=Node(featureSetInst.featureDict["name"],featureSetInst.featureDict["dmrel"].split(":")[0],featureSetInst.featureDict["dmrel"].split(":")[1])
                except Exception as er:
                    print '>'*100, er
                    nodeInst=Node(featureSetInst.featureDict["name"],"None","None")
                    print "dmrel not got",featureSetInst.featureDict
            
            #Iteration for words
            for i in range(chunk[0],chunk[1]+1):
                line = nlines[i]
                if(line[0]=="NULL"):
                    continue
                try:
                    extraWordInfo=line[2]
                except:
                    print "Could not match intrachunk and interchunk SSF annotations !!!"
                    print line
                    #print columns[1],columns[2],wordNu
                featstring = ' '.join([key+'=\''+extraWordInfo.featureDict[key]+'\'' for key in extraWordInfo.featureDict])
                print featstring
                wordInst=Word(line[0],line[1],featstring,extraWordInfo,sentenceNum,chunkNum)
                chunkInst.addWord(wordNum)
                sentenceInst.addWord(wordNum)
                globalWordList.append(wordInst)
                wordNum+=1
                wNum+=1
        
            #Chunk End
            sentenceInst.addNode(nodeInst)
            if(len(chunkInst.wordNumList)!=0):
                sentenceInst.addChunk(chunkInst)
                sentenceInst.addChunkNumToNode(nodeInst.nodeName,chunkInst.chunkNum)
            else:
                print "found file with empty chunk !!!",filePath
                chunkNum-=1

        sentenceInstList.append(sentenceInst)
        sentenceNum+=1
    return (sentenceInstList,globalWordList)
