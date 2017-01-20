import sys
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import names 
import re, feature_vector
global ID
ID=0
final_dict={}
result={}
all_names=[m for m in names.words('male.txt')]+[m for m in names.words('female.txt')]
List_Plural = 'We,Us,You,They,Them,These,Those,Both,Few,Many,Several,Ourselves,Yourselves,Themselves,Our,Your,Their,Ours,Yours,Theirs'.lower().split(",")
List_Singular = 'I,me,You,She,Her,He,Him,It,This,That,Anybody,Anyone,Anything,Each,Either,Everybody,Everyone,Everything,Neither,Nobody,Noone,Nothing,One,Somebody,Someone,Something,Myself,Yourself,Himself,Herself,Itself,My,Your,His,Her,Its,Mine,Yours,Hers'.lower().split(",")

def read_upper_passage(fname):
	upper_passage=[]
	try:
		with open(fname) as doc:
			for line in doc:
				line=line.strip()
				if(re.findall(r'<COREF.*?>(.*?)</COREF>',line)):
					return upper_passage[1:]
				else:
					if re.findall(r'(..?)/(...?)/(.*)',line):
						line=line.replace("/","-")
						#print line
					upper_passage.extend(line.split())

	except Exception,e:
		raise e

def read_anaphors(fname):
	anaphors_sentences=[]
	enter=True
	with open(fname) as doc:
		for line in doc:
			line=line.strip()
			if(re.findall(r'<COREF.*?>(.*?)</COREF>',line)) and enter:
				enter=False
			if line and enter is False:
				anaphors_sentences.append(line)
	return anaphors_sentences

ROOT = 'ROOT'
def getNodes(parent,NPs):
    for node in parent:
        if type(node) is nltk.Tree:
            if node.label() == ROOT:
            	pass
            else:
                if(node.label()=="NP"):
                	NPs.append(node.leaves())
               
            getNodes(node,NPs)
        else:
            pass

    return NPs
def find_NP(foobar):
	sentence=nltk.pos_tag(foobar.split())
	grammar="NP: {<DT>?<CD>?<JJ.?>*<NN.?>+}"
	cp=nltk.RegexpParser(grammar)
	result=cp.parse(sentence)
	NPs=[]
	NPs=getNodes(result,NPs)
	noun_phrases=[]
	for item in NPs:
		temp=[]
		foo=""
		for tup in item:
			foo=foo+" "+tup[0]
		noun_phrases.append(foo)
	return noun_phrases
def find_semantic_dist(anaphor,ante):
	r=0
	if len(anaphor)>1:
		_anaphor=anaphor.split()[-1]
	else:
		_anaphor=anaphor
	if len(ante)>1:
		_ante=ante.split()[-1]
	else:
		_ante=ante
	
	word_1=_anaphor
	word_2=_ante
	syn_sets_word1=wn.synsets(word_1)
	syn_sets_word2=wn.synsets(word_2)
	for item in syn_sets_word1:
		for val in syn_sets_word2:
			foo1=wn.synset(item.name())
			foo2=wn.synset(val.name())
			d=foo1.wup_similarity(foo2)
			if d>0.10:
				r=d
	return r
def check_number(anaphor,ante):
	r=0
	tagged1=nltk.pos_tag(anaphor.split())
	tagged2=nltk.pos_tag(ante.split())
	if ((tagged2[-1][1] == "NNS") and (tagged1[-1][1]!="NNS")) or ((tagged1[-1][1] == "NNS") and (tagged2[-1][1]!="NNS")):
		r=1
	else:
		r=0
	return r
def check_head_noun(anaphor,ante):
	if len(anaphor)>1:
		_anaphor=anaphor.split()[-1]
	else:
		_anaphor=anaphor
	if len(ante)>1:
		_ante=ante.split()[-1]
	else:
		_ante=ante
	if _anaphor==_ante:
		print "head nouns match"
	else:
		print "head nouns dont match"
def check_word_substring(anaphor,ante,anaphor_ids):
	r=0
	tagged=nltk.pos_tag(anaphor.split())
	NPlist=[]
	
	for item in tagged:
		if item[1]=="NN" or item[1]=="NNS" or item[1]=="NNP":
			NPlist.append(item[0])

	foo=ante.split()
	for item in NPlist:
		if item in foo:
			if anaphor+" "+anaphor_ids in final_dict:
				if final_dict[anaphor+" "+anaphor_ids][1]<0.2:
					ids=getID()
					check=True
					for anap in anaphors:
						if ante in anap[0]:
							check=False
							ids=anap[1]
							result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

					if check:
						result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
						result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
						
					final_dict[anaphor+" "+anaphor_ids]=[ante,0.5]
			else:
				ids=getID()
				check=True
				for anap in anaphors:
					if ante in anap[0]:
						check=False
						ids=anap[1]
						result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

				if check:
					result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
					result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
					

				final_dict[anaphor+" "+anaphor_ids]=[ante,0.5]

	return r
def check_appositive(anaphor,ante,ante_sen=None):
	r=0
	if len(anaphor)>1:
		_anaphor=anaphor.split()[0]
	else:
		_anaphor=anaphor
	if len(ante)>1:
		_ante=ante.split()[-1]
	else:
		_ante=ante
	appositive_temp=_ante+", "+_anaphor
	if ante_sen is None:
		pass
	else:
		if appositive_temp in ante_sen:
			r=1
		else:
			r=0

	return r
def check_proper_name(anaphor,ante):
	r=0
	if len(anaphor)<=3 and len(anaphor)>1:
		_anaphor=anaphor.split()
		count=0
		for item in _anaphor:
			if item[0].isupper():
				count+=1
		if count==len(_anaphor):
			if ante.isalpha():
				_ante=ante.split()
				indexes=[]
				for item in _anaphor:
					if item in _ante:
						indexes.append(_ante.index(item))
				if len(indexes)==0:
					r=100
				else:
					r=0

	return r
def check_pronoun(anaphor,ante,ante_sen,anaphor_ids):
	anaphor.replace(",","")
	anaphor.replace('"',"")
	ante.replace(',',"")
	ante.replace('"',"")
	if anaphor in List_Singular:
		final_ante=""
		if ante_sen==None:	
			item=ante	
			if len(item)>1:
				select=True
				for val in item:
					if val[0].isupper():
						continue
					else:
						select=False
				if select==True:
					final_ante=item
					
			else:
				if item[0].isupper():
					final_ante=item

			if anaphor+" "+anaphor_ids in final_dict:
				if 0.10>final_dict[anaphor+" "+anaphor_ids][1]:
					ids=getID()
					check=True
					for anap in anaphors:
						if ante in anap[0]:
							check=False
							ids=anap[1]
							result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

					if check:
						result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
						result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
						
					final_dict[anaphor+" "+anaphor_ids]=[final_ante,0.1]
			else:
				ids=getID()
				check=True
				for anap in anaphors:
					if ante in anap[0]:
						check=False
						ids=anap[1]
						result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

				if check:
					result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
					result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
					
				final_dict[anaphor+" "+anaphor_ids]=[final_ante,0.1]
				#print final_dict,"*******************************************"


		else:
			ante_sen=ante_sen.replace('"',"")
			ante_sen_list=ante_sen.split()
			demo_sen_list=ante_sen.lower().split()
			index_anaphor=demo_sen_list.index(anaphor.lower())+1
			
			if anaphor in ' '.join(demo_sen_list[:index_anaphor]):
				if (anaphor+" "+anaphor_ids) in final_dict:
					if 0.5>final_dict[(anaphor+" "+anaphor_ids)][1]:
						val=demo_sen_list[demo_sen_list.index(anaphor)]
						ids=getID()
						check=True
						for anap in anaphors:
							if ante in anap[0]:
								check=False
								ids=anap[1]
								result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

						if check:
							result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
							result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
							


						final_dict[anaphor+" "+anaphor_ids]=[val,0.5]

				else:
					val=demo_sen_list[demo_sen_list.index(anaphor)]
					ids=getID()
					check=True
					for anap in anaphors:
						if ante in anap[0]:
							check=False
							ids=anap[1]
							result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

					if check:
						result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
						result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
						

					final_dict[anaphor+" "+anaphor_ids]=[val,0.5]
				
			
			elif index_anaphor>1:
				new_text=ante_sen_list[:index_anaphor]
				NPS=find_NP(' '.join(new_text))
				finalNPS=[]
				len_NPS=len(NPS)
				for item in NPS:
					if len(item)>1:
						select=True
						for val in item:
							if val[0].isupper():
								continue
							else:
								select=False
						if select==True:
							finalNPS.append(item)
					else:
						if item[0].isupper():
							finalNPS.append(item)

				if len(finalNPS)>5:
					finalNPS=finalNPS[-5:]
				else:
					finalNPS=finalNPS

				for item in finalNPS:
					tagged=nltk.pos_tag(item.split())
					
					lastNP=""
					if len(tagged)>1:
						for item in tagged[::-1]:
							if item[1]=="NNS":
								break
							else:
								lastNP=item[0]+" "+lastNP
					else:
						if tagged[0][1]=="NNS":
							break
						else:
							lastNP=item[0]

					if item[-1] in all_names:
						if anaphor+" "+anaphor_ids in final_dict:
							if 0.30>final_dict[anaphor+" "+anaphor_ids][1]:
								ids=getID()
								check=True
								for anap in anaphors:
									if ante in anap[0]:
										check=False
										ids=anap[1]
										result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

								if check:
									result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
									result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
									
								final_dict[anaphor+" "+anaphor_ids]=[item,0.3]
						else:
							ids=getID()
							check=True
							for anap in anaphors:
								if ante in anap[0]:
									check=False
									ids=anap[1]
									result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

							if check:
								result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
								result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
								
							final_dict[anaphor+" "+anaphor_ids]=[item,0.3]
					else:
						if anaphor+" "+anaphor_ids in final_dict:
							if 0.10>final_dict[anaphor+" "+anaphor_ids][1]:
								ids=getID()
								check=True
								for anap in anaphors:
									if ante in anap[0]:
										check=False
										ids=anap[1]
										result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

								if check:
									result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
									result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
									
								final_dict[anaphor+" "+anaphor_ids]=[item,0.1]
						else:
							ids=getID()
							check=True
							for anap in anaphors:
								if ante in anap[0]:
									check=False
									ids=anap[1]
									result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

							if check:
								result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
								result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
								
							final_dict[anaphor+" "+anaphor_ids]=[item,0.1]

							
	if anaphor.lower() in List_Plural:
		if ante_sen==None:	
			final_ante=""
			item=ante	
			if len(item)>1:
				select=True
				for val in item:
					if val[0].isupper():
						continue
					else:
						select=False
				if select==True:
					final_ante=item
					
			else:
				if item[0].isupper():
					final_ante=item

			if anaphor+" "+anaphor_ids in final_dict:
				if 0.10>final_dict[anaphor+" "+anaphor_ids][1]:
					ids=getID()
					check=True
					for anap in anaphors:
						if ante in anap[0]:
							check=False
							ids=anap[1]
							result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

					if check:
						result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
						result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
						
					final_dict[anaphor+" "+anaphor_ids]=[final_ante,0.1]
			else:
				ids=getID()
				check=True
				for anap in anaphors:
					if ante in anap[0]:
						check=False
						ids=anap[1]
						result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

				if check:
					result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
					result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
					
				final_dict[anaphor+" "+anaphor_ids]=[final_ante,0.1]	
			
		else:
			ante_sen=ante_sen.replace('"',"")
			ante_sen_list=ante_sen.split()
			demo_sen_list=ante_sen.lower().split()
			index_anaphor=demo_sen_list.index(anaphor.lower())+1
			
			if anaphor in ' '.join(demo_sen_list[:index_anaphor]):
				if (anaphor+" "+anaphor_ids) in final_dict:
					if 0.5>final_dict[anaphor+" "+anaphor_ids][1]:
						ids=getID()
						check=True
						for anap in anaphors:
							if ante in anap[0]:
								check=False
								ids=anap[1]
								result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

						if check:
							result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
							result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
							
						final_dict[anaphor+" "+anaphor_ids]=[val,0.5]	
					#	print final_dict[anaphor+" "+anaphor_ids],"**********"
				else:
					val=demo_sen_list[demo_sen_list[:index_anaphor].index(anaphor)]
					ids=getID()
					check=True
					for anap in anaphors:
						if ante in anap[0]:
							check=False
							ids=anap[1]
							result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

					if check:
						result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
						result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
						
					final_dict[anaphor+" "+anaphor_ids]=[val,0.5]
				
			
			elif index_anaphor>1:
				new_text=ante_sen_list[:index_anaphor]
				NPS=find_NP(' '.join(new_text))
				finalNPS=[]
				len_NPS=len(NPS)
				for item in NPS:
					if len(item)>1:
						select=True
						for val in item:
							if val[0].isupper():
								continue
							else:
								select=False
						if select==True:
							finalNPS.append(item)
					else:
						if item[0].isupper():
							finalNPS.append(item)

				if len(finalNPS)>5:
					finalNPS=finalNPS[-5:]
				else:
					finalNPS=finalNPS

				for item in finalNPS:
					tagged=nltk.pos_tag(item.split())
					
					lastNP=""
					if len(tagged)>1:
						for item in tagged[::-1]:
							if item[1]=="NNS":
								lastNP=item[0]+" "+lastNP
							else:
								break
					else:
						if tagged[0][1]=="NNS":
							lastNP=item[0]							
						else:
							break

					if anaphor+" "+anaphor_ids in final_dict:
						if 0.10>final_dict[anaphor+" "+anaphor_ids][1]:
							ids=getID()
							check=True
							for anap in anaphors:
								if ante in anap[0]:
									check=False
									ids=anap[1]
									result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

							if check:	
								result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
								result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
								
							final_dict[anaphor+" "+anaphor_ids]=[lastNP,0.1]
					else:
						ids=getID()
						check=True
						for anap in anaphors:
							if ante in anap[0]:
								check=False
								ids=anap[1]
								result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

						if check:
							result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
							result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
							
						final_dict[anaphor+" "+anaphor_ids]=[lastNP,0.1]
def getID():
	global ID
	ID+=1
	return "X%d"%ID
def calc_dist(anaphor,ante,ante_sen,anaphor_ids):
	r=0
	if anaphor.lower()=="today":
		if re.findall(r'(..)/(...?)/(.*)',ante) or re.findall(r'(..)-(...?)-(.*)',ante):
			if (anaphor+" "+anaphor_ids) in final_dict:
				final_dict[anaphor+" "+anaphor_ids]=[ante,1.0]
			else:
				ids=getID()
				check=True
				for anap in anaphors:
					if ante in anap[0]:
						check=False
						ids=anap[1]
						result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

				if check:
					result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
					result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
					
					#anaphors.append([ante+" "+ids,ids])
				final_dict[anaphor+" "+anaphor_ids]=[ante,1.0]

	if re.findall(r'(..)/(..)/(.*)',anaphor) or re.findall(r'(..)/(...)/(.*)',anaphor) or re.findall(r'(..)-(..)-(.*)',anaphor) or re.findall(r'(..)-(...)-(.*)',anaphor):
		if (anaphor in ante) or (ante in anaphor) or ante.lower()=="today":
			if (anaphor+" "+anaphor_ids) in final_dict:
				final_dict[anaphor+" "+anaphor_ids]=[ante,1.0]
			else:
				ids=getID()
				check=True
				for anap in anaphors:
					if ante in anap[0]:
						check=False
						ids=anap[1]
						result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

				if check:
					result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
					result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
					
				final_dict[anaphor+" "+anaphor_ids]=[ante,1.0]
		

	if len(anaphor.split())==1 and (anaphor in List_Singular or anaphor in List_Plural):
		try:
			check_pronoun(anaphor,ante,ante_sen,anaphor_ids)
		except Exception,e:
			pass

	try:
		check_word_substring(anaphor,ante,anaphor_ids)
	except Exception:
		pass
	d=find_semantic_dist(anaphor,ante)
	if (d==1.0):
		if anaphor+" "+anaphor_ids in final_dict:
			if (d > final_dict[anaphor+" "+anaphor_ids][1]):
				ids=getID()
				check=True
				for anap in anaphors:
					if ante in anap[0]:
						check=False
						ids=anap[1]
						result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

				if check:
					result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
					result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
					
				
				final_dict[anaphor+" "+anaphor_ids]=[ante,d]
		else:
			ids=getID()
			check=True
			for anap in anaphors:
				if ante in anap[0]:
					check=False
					ids=anap[1]
					result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))

			if check:
				result[anaphor+" "+anaphor_ids]=('<COREF %s REF="%s">%s</COREF>'%(anaphor_ids,ids,anaphor))
				result[ante+" "+ids]=('<COREF ID="%s">%s</COREF>'%(ids,ante))
				
			final_dict[anaphor+" "+anaphor_ids]=[ante,d]
def find_NPs_noco(ante_sen):
	simple_text=make_plain_text_noco(ante_sen)
	nps=find_NP(simple_text)
	return nps
def find_distance(anap_sen,anaphors_sentences_rev):
	for i,ante_sen in enumerate(anaphors_sentences_rev):
		if i==0:
			footemp=ante_sen.split()
			indexes=[]
			filler=0
			for i,item in enumerate(footemp):
				if item=="<COREF":
					indexes.append(i-filler)
					filler+=1
			plain_t=make_plain_text(ante_sen)
			NPs=find_NPs(ante_sen)
			anaphors=re.findall(r'<COREF.*?>(.*?)</COREF>',anap_sen)
			anaphor_ids=re.findall(r'<COREF (.*?)>',anap_sen)
			ran_demo= plain_t.split()
			m=0 
			for i,item in enumerate(anaphors):
				if m>len(indexes)-1:
					break
				temp=ran_demo[:indexes[m]]
				if temp:
					NPs=find_NP(' '.join(temp))
					for j,val in enumerate(NPs):
						r=calc_dist(item,val.strip(),plain_t,anaphor_ids[i])
				m+=1
		
		else:
			NPs=find_NPs(ante_sen)
			plain_t=make_plain_text(ante_sen)
			anaphors=re.findall(r'<COREF.*?>(.*?)</COREF>',anap_sen)
			anaphor_ids=re.findall(r'<COREF (.*?)>',anap_sen)
			for i,item in enumerate(anaphors):
				for val in NPs:
					r=calc_dist(item,val.strip(),None,anaphor_ids[i])
def make_plain_text_noco(ante_sen):
	corefs=re.findall(r'<COREF.*?>(.*?)</COREF>',ante_sen)
	temp=ante_sen
	for item in corefs:
		temp=re.sub(r'(<COREF.*?>(.*?)</COREF>)',"",temp,1)
	return temp
def make_plain_text(ante_sen):
	corefs=re.findall(r'<COREF.*?>(.*?)</COREF>',ante_sen)
	temp=ante_sen
	for item in corefs:
		temp=re.sub(r'(<COREF.*?>(.*?)</COREF>)',item,temp,1)
	return temp
def find_NPs(ante_sen):
	simple_text=make_plain_text(ante_sen)
	nps=find_NP(simple_text)
	return nps

responselist=sys.argv[1]
filename=[]
try:
	with open(responselist,"r") as doc:
		for lines in doc:
			lines=lines.strip()
			filename.append(lines)

except Exception:
	print "file not found"

for fname in filename:
	final_dict={}
	result={}
	upper_passage=read_upper_passage(fname)
	anaphors_sentences=read_anaphors(fname)	
	file_label=re.findall(r'(.+)\..+',fname)
	complete_sentence=upper_passage+anaphors_sentences
	final_ante=[]
	for item in complete_sentence:
		temp=make_plain_text(item)
		final_ante.append(temp)

	complete_str=' '.join(complete_sentence)
	plain_complete_string = make_plain_text(complete_str)
	#print plain_complete_string
	anaphors=re.findall(r'<COREF.*?>(.*?)</COREF>',complete_str)
	anaphor_ids=re.findall(r'<COREF (.*?)>',complete_str)
	#print anaphors
	vector=feature_vector.main(complete_sentence,anaphors,' '.join(anaphors_sentences), ' '.join(upper_passage),result, plain_complete_string)
	
	#continue
	
	
	"""final_anaphor_list=[]
	for i in range(len(anaphors)):
		final_anaphor_list.append([anaphors[i],anaphor_ids[i]])

	indexes=[]
	filler=0
	anap_str=' '.join(anaphors_sentences)

	temp_anap_list=anap_str.split()
	indices = [i for i, x in enumerate(temp_anap_list) if x=='<COREF']
	for i in range(len(indices)):
		indices[i]=indices[i]-i

	anaphors_sentences_rev=complete_sentence[::-1]
	for i,item in enumerate(anaphors_sentences_rev):
		if i<len(anaphors_sentences_rev):
			if i==len(anaphors_sentences_rev)-1:
				find_distance(anaphors_sentences_rev[i],anaphors_sentences_rev[i])
			else:
				find_distance(anaphors_sentences_rev[i],anaphors_sentences_rev[i:])
	count=0

	for item in final_dict:
		if final_dict[item][0] in plain_complete_string :
			count+=1

	"""
	#print file_label
	target=open("%s.response"%file_label[0],"w")
	target.write("<TXT>")
	target.write("\n")
	for item in vector:
		#print vector[item]
		target.write(vector[item][0])
		target.write("\n")

	target.write("</TXT>")
	target.write("\n")
	target.close()
	#print "___________________________",target.closed
	