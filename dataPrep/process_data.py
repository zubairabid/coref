#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import codecs
reload(sys)
sys.setdefaultencoding("utf-8")
#from util import *
#from extract_relations import *
from ssf_api import *
#from letter import *
#from merge_annotations import *
#from identify_connectives import *
#from annotated_data import *
import pickle

if len(sys.argv)<2:
    print "Please data give folder location"
    exit()

dataLocation=sys.argv[1]
FileList=folderWalk(dataLocation)
fileNum=0
createDirectory("./processedData/collection/")

errs = []
for rawFile in FileList:
    #print rawFile
    #if '2633495' in rawFile:
    fd=codecs.open(rawFile,"r",encoding="utf-8")
    try:
        sentenceList, globalWordList = extractSSFannotations(rawFile)
        ssfinfo = SSFInfo(sentenceList, globalWordList)
        createChildList(ssfinfo)
    except Exception as e:
        errs += [rawFile, e]
        continue
    #sentenceList, globalWordList = extractSSFannotations(rawFile)

    if(sentenceList==None):
        print "Continuing"
        continue
    #print sentenceList
    pickle.dump(ssfinfo, open("processedData/collection/"+rawFile.split('/')[-1]+'.pkl','w'))
    fd.close()
    fileNum+=1

#exportModel("processedData/annotatedData",discourseFileCollection)
print "processed %d files correctly"%(fileNum)
print 'errors faced in these files:', errs
