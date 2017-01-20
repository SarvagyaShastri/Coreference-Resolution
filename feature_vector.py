import re, copy
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import names
from difflib import SequenceMatcher
male_names=[]
with open("male(1).txt") as doc:
	for lines in doc:
		lines=lines.lower()
		male_names.append(lines)

female_names=[]
with open("female(1).txt") as doc:
	for lines in doc:
		lines=lines.lower()
		female_names.append(lines)



female_names_set=set(female_names)
male_names_set=set(male_names)
symbols=["!","@","$","%","^","&","*","-",",","\\","/",'"',"~",".",";"]
article = ['a','an','the']
nominative_pronouns=['I', 'you', 'he', 'she', 'it', 'they', 'we']
accusative_pronouns=['me', 'you', 'him', 'her', 'it', 'us', 'you', 'them']
possessive_pronouns=['my','your','his','her','its','our','their','whose','mine','yours','his','hers','ours','theirs']
male_pronouns=["he","his"]
female_pronouns=["she","her"]
singular_reflexive=["myself","yourself","himself","herself","itself"]
plural_reflexive=["ourselves","yourselves", "themselves"]
pronoun_set=set(nominative_pronouns+accusative_pronouns+possessive_pronouns+male_pronouns+female_pronouns+singular_reflexive+plural_reflexive)
#all_names=[m for m in names.words('male.txt')]+[m for m in names.words('female.txt')]
#male_names=[m for m in names.words('male.txt')]
#female_names=[m for m in names.words('female.txt')]
List_Plural = 'We,Us,You,They,Them,These,Those,Both,Few,Many,Several,Ourselves,Yourselves,Themselves,Our,Your,Their,Ours,Yours,Theirs'.lower().split(",")
List_Singular = 'I,me,You,She,Her,He,Him,It,This,That,Anybody,Anyone,Anything,Each,Either,Everybody,Everyone,Everything,Neither,Nobody,Noone,Nothing,One,Somebody,Someone,Something,Myself,Yourself,Himself,Herself,Itself,My,Your,His,Her,Its,Mine,Yours,Hers'.lower().split(",")

ROOT = 'ROOT'
global counter
counter=0
global ID
ID=0

def getID():
	global ID
	ID+=1
	return "X%d"%ID

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


def main(anaphors_sentences,anaphors,lower_passage, upper_passage, result, plain_complete_string):
	#print "________________________________________________________"
	global counter
	counter=0
	filtered=[]
	anaphors_sentences=[lower_passage]
	for val in anaphors_sentences:
		corefs=re.findall(r'<COREF.*>(.*)</COREF>',val) 
		temp=val
		for item in corefs:
			temp=re.sub(r'(<COREF.*>(.*)</COREF>)',"",temp,1)
			filtered.append(temp)
	
	preprocess=[]
	appositives=[]
	footemp= []
	for item12 in upper_passage:

		if item12 in symbols:
			upper_passage=upper_passage.replace(item12, " ")

	upper_passage=upper_passage.split()
	for item in upper_passage:
		temp=find_NP(item)
		for temp2 in temp:
			if temp2.strip()!="":
				counter+=1
				preprocess.append([temp2.strip(),counter, "NP",getID()])
	
	
	for item in anaphors_sentences:
		item=item.split("\n")
		rest=""
		for foo in item:
			if re.findall(r'<COREF.*>(.*?)</COREF>',foo):	
				if len(re.findall(r'<COREF.*?>(.*?)</COREF>',foo))>1:
					corefs=re.findall(r'<COREF.*?>(.*?)</COREF>',foo)
					anaphor_ids=re.findall(r'<COREF ID="(.*?)">',foo)
					index=[(m.start(0),m.end(0)) for m in re.finditer(r'<COREF.*?>(.*)</COREF>',foo)]
					temp=find_NP(foo[:index[0][0]].strip())
					for temp2 in temp:
						if temp2.strip()!="":
							counter+=1
							preprocess.append([temp2.strip(),counter,"NP",getID()])

					counter+=1
					preprocess.append([corefs[0].strip(),counter, "A",anaphor_ids[0]])
					for i,demo in enumerate(re.findall(r'</COREF>(.*?)<COREF.*?>',foo)):
						temp=find_NP(demo.strip())
						for temp2 in temp:
							if temp2.strip()!="":
								counter+=1
								preprocess.append([temp2.strip(),counter,"NP",getID()])
						counter+=1
						preprocess.append([corefs[i+1].strip(),counter,"A",anaphor_ids[i+1]])

					temp=find_NP(foo[index[0][1]:].strip())
					for temp2 in temp:
						if temp2.strip()!="":
							counter+=1
							preprocess.append([temp2.strip(),counter,"NP",getID()])
					
					
				elif len(re.findall(r'<COREF.*?>(.*?)</COREF>',foo))==1:
					corefs=re.findall(r'<COREF.*?>(.*?)</COREF>',foo)
					anaphor_ids=re.findall(r'<COREF (.*?)>',foo)
					for val in re.findall(r'(.*)<COREF.*>.*</COREF>(.*)',foo):
						for i in val:
							if i!="":
								i=i.strip()
								temp=find_NP(i)
								for temp2 in temp:
									if temp2.strip()!="":
										counter+=1
										preprocess.append([temp2.strip(),counter,"NP",getID()])
							else:
								counter+=1
								preprocess.append([corefs[0].strip(),counter,"A",anaphor_ids[0]])

			else:
				temp=find_NP(foo)
				for temp2 in temp:
					if temp2.strip()!="":
						counter+=1
						preprocess.append([temp2.strip(),counter,"NP",getID()])

	#for i in range(len(preprocess)):
		#preprocess[i][0]=' '.join(re.findall(r'[a-zA-Z0-9]+',preprocess[i][0]))
	#for demo in preprocess:
	#	print demo
	feature_vector=make_feature_vector(preprocess)
	result=check_appositive_new(preprocess,plain_complete_string,result)
	result=calculate_distance(feature_vector, anaphors, anaphor_ids, result, plain_complete_string)
	
	return result

def calculate_distance(feature_vector, anaphors, anaphor_ids, result, plain_complete_string):
	temp_feature_vector=copy.deepcopy(feature_vector)
	position_anaphor=[]
	for item in anaphors:
		for value in temp_feature_vector:
			if item==value[0] and value[1]=="A":
				index=temp_feature_vector.index(value)
				position_anaphor.append([item, index, value[2]])
				temp_feature_vector[index][0]="000ABCD./."
				break

	for item in position_anaphor:
		index=item[1]
		
		result=find_antecedent(item, feature_vector[:index][::-1], result, plain_complete_string, position_anaphor)

	#print result
	return result

def find_antecedent(item, possible_antecedents, result, plain_complete_string, position_anaphor):
	for antecedents in possible_antecedents:
		if item[0].lower()=="today":
			if re.findall(r'(..)/(...?)/(.*)',antecedents[0]) or re.findall(r'(..)-(...?)-(.*)',antecedents[0]):
				if (item[2][1]) not in result:
					result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
				if (antecedents[2][1]) not in result:
					result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]

		if re.findall(r'(..)/(..)/(.*)',item[0]) or re.findall(r'(..)/(...)/(.*)',item[0]) or re.findall(r'(..)-(..)-(.*)',item[0]) or re.findall(r'(..)-(...)-(.*)',item[0]):				
			if (item[0] in antecedents[0]) or (antecedents[0] in item[0]) or antecedents[0].lower()=="today":
				if (item[2][1]) not in result:
					result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
				if (antecedents[2][1]) not in result:
					result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]


		if unicode(item[0],'utf-8').isnumeric():
			if item[0] in plain_complete_string.split() :
				new_id=getID()
				if (item[2][1]) not in result:
					result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], new_id, item[0])]
				if (new_id) not in result:
					result[(new_id)]=['<COREF ID="%s">%s</COREF>'%(new_id,item[0])]


	#___________________________________o______________________________________WORD SUBSTRING
	best=["*" for i in range(5)]
	best[1]=0
	for antecedents in possible_antecedents:
		if item[0] in pronoun_set and item[2][-1]=="ANIM":
			continue
		result_word_substring=check_word_substring(item, antecedents)
		if result_word_substring>best[1]:
			best[0]=item[0]
			best[1]=result_word_substring
			best[2]=antecedents[0]
			best[3]=item[2][1]
			best[4]=antecedents[2][1]

	if best[1]!=0:
		if (best[3]) not in result:
			result[(best[3])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(best[3],best[4],best[0])]
		if (best[4]) not in result:
			result[(best[4])]=['<COREF ID="%s">%s</COREF>'%(best[4],best[2])]

	"""best=["*" for i in range(5)]
	best[1]=0

	for antecedents in possible_antecedents:
		if item[0] in pronoun_set and item[2][-1]=="ANIM":
			continue
		result_word_substring=check_word_substring(antecedents, item)
		if result_word_substring>best[1]:
			best[0]=item[0]
			best[1]=result_word_substring
			best[2]=antecedents[0]
			best[3]=item[2][1]
			best[4]=antecedents[2][1]

	if best[1]!=0:
		if (best[3]) not in result:
			result[(best[3])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(best[3],best[4],best[0])]
		if (best[4]) not in result:
			result[(best[4])]=['<COREF ID="%s">%s</COREF>'%(best[4],best[2])]
	"""


	#_________________________________________x_________________________________________________WORD SUBSTRING01
	if item[0].lower() in pronoun_set:
		if item[0].lower() in singular_reflexive:
			for antecedents in possible_antecedents:
				if antecedents[2][5]=="SING" and antecedents[2][-1]=="ANIM":
					if (item[2][1]) not in result:
						result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
					if (antecedents[2][1]) not in result:
						result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]
						break

		if item[0].lower() in plural_reflexive:
			for antecedents in possible_antecedents:
				if antecedents[2][5]=="PLURAL" and antecedents[2][-1]=="ANIM":
					if (item[2][1]) not in result:
						result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
					if (antecedents[2][1]) not in result:
						result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]
						break

			
		if item[0].lower() in male_pronouns:
			for antecedents in possible_antecedents:
				_antecedents=antecedents[0].split()
				for sonam in _antecedents:
					if sonam in male_names_set:
						if (item[2][1]) not in result:
							result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
						if (antecedents[2][1]) not in result:
							result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]
							break


		if item[0].lower() in female_pronouns:
			for antecedents in possible_antecedents:
				_antecedents=antecedents[0].split()
				for sonam in _antecedents:
					if sonam in female_names_set:
						if (item[2][1]) not in result:
							result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
						if (antecedents[2][1]) not in result:
							result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]
							break

		for antecedents in possible_antecedents:
			if antecedents[2][-1]=="ANIM" and item[2][-1]=="ANIM" and (item[2][0]-antecedents[2][0]<=2):
				if item[0].lower() in List_Plural and antecedents[2][5]=="PLURAL":
					if (item[2][1]) not in result:
						result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
					if (antecedents[2][1]) not in result:
						result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]
				
				elif item[0].lower() in List_Singular and antecedents[2][5]=="SING":
					if (item[2][1]) not in result:
						result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
					if (antecedents[2][1]) not in result:
						result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]
					
	if item[0].lower()=="its" or item[0].lower()=="it":#(item[2][0]-antecedents[2][0])<2 : #(item[0].lower()=="it" or item[0].lower()=="its") and (item[2][0]-antecedents[2][0]<2)
		for antecedents in possible_antecedents:
			if antecedents[2][-1]=="INANIM" and item[0].lower()=="its":
				if True in [antecedents[0]==i[0] for i in position_anaphor]:
					#print item[0], " ",item[2][1], " ",antecedents[0], " ", antecedents[2][1], "****************"
					if (item[2][1]) not in result:
						result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
					if (antecedents[2][1]) not in result:
						result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]
					break
			if antecedents[2][-1]=="INANIM" and antecedents[2][5]=="SING" and item[0].lower()=="it":
				if antecedents[2][6]=="YES":
					if True in [antecedents[0]==i[0] for i in position_anaphor]:
						#print item[0], item[2][1], antecedents[0], antecedents[2][1]
						if (item[2][1]) not in result:
							result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
						if (antecedents[2][1]) not in result:
							result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]
						break

	if item[0].lower()=="then":
		for antecedents in possible_antecedents:
			if True in [antecedents[0]==i[0] for i in position_anaphor]:
				if unicode(antecedents[0],'utf-8').isnumeric() or "year" in antecedents[0] or "day" in antecedents[0] or "hours" in antecedents[0]:
					if (item[2][1]) not in result:
						result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
					if (antecedents[2][1]) not in result:
						result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]
					break



	#____________________________________________________________________________________________________________PRONOUN
	for antecedents in possible_antecedents:
		if item[2][5]==antecedents[2][5]:
			antecedents[0]=antecedents[0].lower()
			item[0]=item[0].lower()
			temp_item=item[0].split()
			temp_ante=antecedents[0].split()
			if len(temp_item)>1:
				_temp_item=temp_item[-1]
				if temp_item[0] not in article:
					_temp_item_head=temp_item[0]
				else:
					_temp_item_head=temp_item[1]
			else:
				_temp_item=temp_item[0]
				_temp_item_head=temp_item[0]

			if len(temp_ante)>1:
				_temp_ante=temp_ante[-1]
				if _temp_ante[0] not in article:
					_temp_ante_head=temp_ante[0]
				#	print _temp_item_head, _temp_ante_head
				else:
					_temp_ante_head=temp_ante[1]
			else:
				_temp_ante=temp_ante[0]
				_temp_ante_head=temp_ante[0]
			
			if _temp_item.lower() in temp_ante or _temp_item_head.lower() in temp_ante:
				if _temp_item.lower() in temp_ante:
					index=temp_ante.index(_temp_item.lower())

				else:
					index=temp_ante.index(_temp_item_head.lower())					
				if (item[2][1]) not in result:
					result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
				if (antecedents[2][1]) not in result:
					result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],temp_ante[index])]

	
	#____________________________________________________________________________________________________________
	best=[0 for i in range(5)]
	for antecedents in possible_antecedents:
		if item[2][5]==antecedents[2][5]:
			something_common=False
			temp_item=item[0].split()
			temp_ante=antecedents[0].split()
			for tp in temp_item:
				if tp in article:
					continue
				for dm in temp_ante:
					if tp==dm:
						something_common=True

			if something_common is True:
				similarity=SequenceMatcher(None, item[0], antecedents[0]).ratio()
				#print similarity
				if similarity>best[1]:
					best[0]=item[0]
					best[1]=similarity
					best[2]=item[2][1]
					best[3]=antecedents[0]
					best[4]=antecedents[2][1]
	if best[1]!=0:
		if (best[2]) not in result:
			result[(best[2])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(best[2], best[4], best[0])]
		if (best[4]) not in result:
			result[(best[4])]=['<COREF ID="%s">%s</COREF>'%(best[4],best[3])]
		#print best[2], best[4], best[0], best[4],best[3]
	#______________________________________________________________________________________________________________
	
	#_______________________________________________________________________________________________________________
	
	best_semantic=0
	for antecedents in possible_antecedents:
		if item[2][-1]==antecedents[2][-1] and item[2][5]==antecedents[2][5]:
			r=find_semantic_dist(item[0].split()[-1],antecedents[0].split()[-1])
			if r>0.7:
				if (item[2][1]) in result:
					pass
				else:		
					result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
					if (antecedents[2][1]) not in result:
						result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]
			else:
				antecedents[0]=antecedents[0].lower()
				item[0]=item[0].lower()
				temp_item=item[0].split()
				temp_ante=antecedents[0].split()
				if len(temp_item)>1:
					_temp_item=temp_item[-1]
					if temp_item[0] not in article:
						_temp_item_head=temp_item[0]
					else:
						_temp_item_head=temp_item[1]
				else:
					_temp_item=temp_item[0]
					_temp_item_head=temp_item[0]

				if len(temp_ante)>1:
					_temp_ante=temp_ante[-1]
					if _temp_ante[0] not in article:
						_temp_ante_head=temp_ante[0]
					#	print _temp_item_head, _temp_ante_head
					else:
						_temp_ante_head=temp_ante[1]
				else:
					_temp_ante=temp_ante[0]
					_temp_ante_head=temp_ante[0]

				r=find_semantic_dist(_temp_ante_head,_temp_item_head)
				if r>0.7:
					if (item[2][1]) in result:
						pass
					else:		
						result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
						if (antecedents[2][1]) not in result:
							result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]

				


	
	new_id=getID()
	if (item[2][1]) not in result:
		result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], new_id, item[0])]
	if (new_id) not in result:
		result[(new_id)]=['<COREF ID="%s">%s</COREF>'%(new_id,item[0].split()[-1])]


	"""for antecedents in possible_antecedents:
		_item=item[0].split()
		_item_head=_item[-1]
		longest=max(_item, key=len)
		if longest in antecedents[0] or _item_head in antecedents[0]:
			#print "referred"
			if (item[2][1]) not in result:
				result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
			if (antecedents[2][1]) not in result:
				result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]

		_antecedent=antecedents[0].split()
		if True in [i==j for i in _item for j in _antecedent]:
			#print "referred"
			if (item[2][1]) not in result:
				result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
			if (antecedents[2][1]) not in result:
				result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]


	best_semantic=0
	for antecedents in possible_antecedents:
		if item[2][-1]==antecedents[2][-1]:
			for foo1 in item[0].split():
				for foo2 in antecedents[0].split():
					r=find_semantic_dist(foo1,foo2)
					if r>0.5:
						#print item[0],"with ID",item[2][1],"Refers", antecedents[0], "with ID", antecedents[2][1], "semantic"
						if (item[2][1]) in result:
							pass
						else:		
							result[(item[2][1])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(item[2][1], antecedents[2][1], item[0])]
							if (antecedents[2][1]) not in result:
								result[(antecedents[2][1])]=['<COREF ID="%s">%s</COREF>'%(antecedents[2][1],antecedents[0])]

	"""

	return result
	

def find_semantic_dist(anaphor,ante):
	r=0
	_anaphor=anaphor
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
			if d>0.7:
				r=d
	return r

			
def check_word_substring(item, ante_string):

	item[0]=item[0].lower()
	ante_string[0]=ante_string[0].lower()
	best=0
	result=[]
	if re.search(r"\b" + re.escape(item[0]) + r"\b", ante_string[0]):
		#print float(len(item[0].split()))/len(ante_string[0].split()), item[0], ante_string[0]
		return float(len(item[0].split()))/len(ante_string[0].split())
	else:
		return 0

def make_feature_vector(preprocess):
	feature_vector=[]
	for item in preprocess:
		_feature_vector=[]
		if re.findall(r'[a-zA-Z0-9]+',item[0]):
			_feature_vector.append(getPos(item))
			_feature_vector.append(findID(item))
			_feature_vector.append(getPronounType(item[0]))
			_feature_vector.append(getArticle(item[0]))
			_feature_vector.append(getAppositive(item[0]))
			_feature_vector.append(getNumber(item[0]))
			_feature_vector.append(getProperName(item[0]))
			_feature_vector.append(getSemanticClass(item[0]))
			_feature_vector.append(getGender(item[0]))
			_feature_vector.append(getAnimacy(item[0]))
			feature_vector.append([item[0],item[2],_feature_vector])


	return feature_vector

def findID(item):
	return item[-1]

def getPos(item):
	return item[1]

def getPronounType(item):
	#print item
	item=item.split()
	#print item
	if item[-1] in possessive_pronouns:
		return "POSS"
	elif item[-1] in nominative_pronouns:
		return "NOM"
	elif item[-1] in accusative_pronouns:
		return "ACC"
	else:
		return None

def getArticle(item):
	item=item.split()
	if item[0].lower()=="the":
		return "DEF"
	elif item[0].lower()=="a" or item[0].lower()=="an":
		return "INDEF"
	else:
		return None

def getAppositive(item):
	return 0

def getNumber(item):
	item=' '.join(re.findall(r'[a-zA-Z0-9]+',item))
	item=item.split()
	if item[0].lower() in List_Plural and len(item)==1:
		return "PLURAL"
	if item[0].lower() in List_Singular and len(item)==1:
		return "SING"
	if item[0].lower() in article or item[0].lower() in pronoun_set:
		if len(item)>1:
			if item[1].lower().endswith("s") or item[-1].lower().endswith("s"):
				return "PLURAL"
		
	if item[-1].lower().endswith("s") or item[0].lower().endswith("s"):
		return "PLURAL"
	else:
		return "SING"

def getProperName(item):
	pn=True
	item=item.split()
	for val in item:
		if val[0].isupper():
			pass
		else:
			pn=False

	if pn:
		return "YES"
	else:
		return "NO"


def getSemanticClass(item):
	return 0

def getGender(item):
	return 0

def getAnimacy(item):
	item=item.split()
	word_1=item[-1]
	if word_1.lower() in pronoun_set and (word_1.lower()!="it" and word_1.lower()!="its"):
		return "ANIM"

	syn_sets_word1=wn.synsets(word_1)
	decision=False
	for item in syn_sets_word1:
		foo1=wn.synset(item.name())
		hypernyms=[synset.name() for synset in foo1.hypernym_paths()[0]]
		for hypernym in hypernyms:	
			if 'person' in hypernym or 'living_thing' in hypernym or 'animal' in hypernym or 'organism' in hypernym:
				decision=True
				break
	if decision:
		return "ANIM"
	else:
		return "INANIM"

def check_appositive_new(vector,plain_complete_string,result):
	#print "mai hu don"
	for noun_phrase in vector:
		np_length = len(noun_phrase[0])
		if noun_phrase[0] in plain_complete_string:
			index_np = plain_complete_string.index(noun_phrase[0]) 
			if(((plain_complete_string[index_np-2] == ",") and (plain_complete_string[index_np+np_length] == ",")) or \
			((plain_complete_string[index_np-1] == ",") and (plain_complete_string[index_np+np_length] == ",")) or \
			((plain_complete_string[index_np-2] == ",") and (plain_complete_string[index_np+np_length] == ".") and (noun_phrase[0].split()[0] in article)) or \
			((plain_complete_string[index_np-2] == ",") and (noun_phrase[0][-1] == ".") and (noun_phrase[0].split()[0] in article))): 
		
				if (noun_phrase[3]) not in result:
					#print noun_phrase[3]
					#print noun_phrase[0],noun_phrase[3],vector[noun_phrase[1]-2][3], vector[noun_phrase[1]-2][0]
					result[(noun_phrase[3])]=['<COREF ID="%s" REF="%s">%s</COREF>'%(noun_phrase[3],vector[noun_phrase[1]-2][3], noun_phrase[0])]
				if (vector[noun_phrase[1]-2][3]) not in result:
				#	print vector[noun_phrase[1]-2][3],vector[noun_phrase[1]-2][0]
					result[(vector[noun_phrase[1]-2][3])]=['<COREF ID="%s">%s</COREF>'%(vector[noun_phrase[1]-2][3],vector[noun_phrase[1]-2][0])]
				
			else:
				pass
				#print noun_phrase,": Not Appositive"
		else:
			continue
	
	return result




		

