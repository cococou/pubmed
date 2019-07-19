#!/usr/bin/env python3
import re
import sys
import requests
import xml.etree.ElementTree as ET

def GetJson(pubmedid):
    r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ID}&rettype=xml".format(ID=str(pubmedid)))
    if r.status_code != 200:
        print("connection err!!! return {}".format(r.status_code),file=sys.stderr)
        exit(1)
    return r.content

def ParseXml(xmltext):
    root = ET.fromstring(xmltext)
    # print(root.tag,root.attrib)  #PubmedArticleSet
    # for child in root:
    #     print(child.tag, child.attrib) #PubmedArticle
    #     for leaf in child:
    #         print(leaf.tag, leaf.attrib) #MedlineCitation PubmedData #i need parse MedlineCitation
    Cite = []

    LastNames = []
    for LastName in root.iter('LastName'):
        LastNames.append(LastName.text)
    Initials = []
    for Initial in root.iter('Initials'):
        Initials.append(Initial.text)
    authors = ','.join([L + ' ' + I for L,I in zip(LastNames,Initials)])
    Cite.append(authors)

    ArticleTitle = ''
    for ArticleTitle in root.iter('ArticleTitle'):
        #print(Title.tag,Title.text)
        ArticleTitle = ArticleTitle.text
        ArticleTitle = re.sub("\.$","",ArticleTitle.strip())
        break
    Cite.append(ArticleTitle)

    ISOAbbreviation=''
    for ISOAbbreviation in root.iter('ISOAbbreviation'):
        ISOAbbreviation = ISOAbbreviation.text.replace('.','')
        break
    Cite.append(ISOAbbreviation)

    year='';month=''
    for PubDate in root.iter("PubDate"):
        for Year in PubDate.iter('Year'):
            year = Year.text

        for Month in PubDate.iter("Month"):
            month = Month.text
        break
    issue='';volume=''
    for JournalIssue in root.iter("JournalIssue"):
        for Volume in JournalIssue.iter("Volume"):
            volume = Volume.text
        for Issue in JournalIssue.iter("Issue"):
            issue = Issue.text
        break
    for MedlinePgn in root.iter('MedlinePgn'):
        MedlinePgn = MedlinePgn.text
        break
    DateIssue = year + ' ' + month + ';' + volume + '(' + issue + ')' + ':' + MedlinePgn
    Cite.append(DateIssue)

    ArticleId = ''
    for ArticleId in root.iter('ArticleId'):
        ArticleId = ArticleId.text
        break
    Cite.append(ArticleId)

    for PMID in root.iter('PMID'):
        PMID = PMID.text
        break
    ID = 'PubMed PMID:' + PMID + '.'
    Cite.append(ID)
    return '.'.join(Cite)

if __name__ == "__main__":

    papers = ' '.join(sys.argv[1:])
    All = set(re.split(';|,|\t+|\s+',papers))
    if not All:
        print("pubmed input empty!!!",file=sys.stderr)
        exit(1)

    for i in All:
        x = GetJson(pubmedid=i)
        print(ParseXml(xmltext=x))
