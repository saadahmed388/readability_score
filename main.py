# -*- coding: utf-8 -*-
"""_nlp.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K5FYaDRx6hSRPDFwaV1ZifHuUV3mjX6h
"""

!pip install contractions
!pip install hyphenate

!pip install beautifulsoup4
!pip install lxml
!pip install html5lib
!pip install requests

import pandas as pd
from bs4 import BeautifulSoup as soup
import requests
import glob
import re
import nltk 
import string
import time
import hyphenate
import contractions
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

def read_url(path):
  return pd.read_excel(path)

def save_text_no_head(input_url,path_to_save_files,user_agent_header):
  #headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
  headers = user_agent_header
  for i  in range(len(input_url['URL'])):
    if(i==7 or i==20 or i==107): continue
    test_url = input_url['URL'][i]
    html= requests.get(test_url,headers=headers)
    soup_= soup(html.content, 'lxml')

    file = open(path_to_save_files + '/{}.txt'.format(int(input_url['URL_ID'][i])), 'w')

    para = soup_.find('div',class_='td-post-content')
    paragraphs = para.find_all('p')
    for p in paragraphs:
      file.write(p.text)

    file.close()

def save_text_with_head(input_url,path_to_save_files):
  headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}

  for i  in range(len(input_url['URL'])):
    if(i==7 or i==20 or i==107): continue
    test_url = input_url['URL'][i]
    html= requests.get(test_url,headers=headers)
    soup_= soup(html.content, 'lxml')

    file = open(path_to_save_files + '/{}.txt'.format(int(input_url['URL_ID'][i])), 'w')
    title = soup_.head.title.text
    title = title.split('-')[0]
    file.write(title + '\n')

    para = soup_.find('div',class_='td-post-content')
    paragraphs = para.find_all('p')
    for p in paragraphs:
      file.write(p.text + '\n')

    file.close()

### Reading article and pre-processing
def preprocessing(i,saved_text_dir):

  with open(saved_text_dir+"/{}.txt".format(int(input_url['URL_ID'][i]))) as file:
    txt = file.read()
    sentences = txt
  remove = string.punctuation
  remove = remove.replace("-", "") # don't remove hyphens
  pattern = r"[{}]".format(remove) # create the pattern
  txt_sub = re.sub(pattern, "", txt)
  txt_sub = contractions.fix(txt_sub)
  words = txt_sub.split()
  alphabetic_only = [word for word in words if(not(any(chr.isalpha() for chr in word) and any(chr.isdigit() for chr in word)) and not(word.isnumeric()))]
  lower_case_only = [word.lower() for word in alphabetic_only]
  num_total_words = len(alphabetic_only)
 
  sentences = sentences.split('.')
  sentences = [sentence.strip() for sentence in sentences]
  num_sentences  = len(sentences)-1

  stop_words = set(stopwords.words('english'))
  cleaned = [word for word in lower_case_only if word not in stop_words]
  num_total_words_nltk = len(cleaned)

  return alphabetic_only,lower_case_only,num_total_words,num_sentences,num_total_words_nltk

### Words after cleaning from stopwords class of NLTK 
def cleaned_words_nltk(lower_case_only):
  stop_words = set(stopwords.words('english'))
  cleaned = [word for word in lower_case_only if word not in stop_words]
  num_total_words_nltk = len(cleaned)
  return num_total_words_nltk    

### Calculating number of positive and negative words in article
### Calculating scores
def sentimental_scores(lower_case_only,stopwords_directory,pos_word_path,neg_word_path):
  filenames = glob.glob(stopwords_directory + "/*.txt")
  stopwords = []
  for file in filenames:
    with open(file,"r",encoding='latin-1') as file:
      lines = file.readlines()

    text_sorted = [line.partition(' |')[0] for line in lines]  
    text_sorted = [word.strip() for word in text_sorted]
    lower_case_only_stopwords = [word.lower() for word in text_sorted]
    stopwords.extend(lower_case_only_stopwords)
  cleaned_words = [word for word in lower_case_only if word not in stopwords]
  num_total_cleaned = len(cleaned_words)

  with open(pos_word_path,"r",encoding='latin-1') as file:
    pos_words = file.readlines()
  text_sorted = [word.strip() for word in pos_words]
  lower_pos_words = [word.lower() for word in text_sorted]

  with open(neg_word_path,"r",encoding='latin-1') as file:
    neg_words = file.readlines()
  text_sorted = [word.strip() for word in neg_words]
  lower_neg_words = [word.lower() for word in text_sorted]

  pos_in_file = [word for word in cleaned_words if word in lower_pos_words]
  neg_in_file = [word for word in cleaned_words if word in lower_neg_words]

  num_pos = len(pos_in_file)
  num_neg = len(neg_in_file)

  polarity_score = ((num_pos-num_neg)/((num_pos+num_neg)+ 0.000001)) 
  subjectivity_score = ((num_pos + num_neg)/(num_total_cleaned + 0.000001))

  return num_pos,num_neg,round(polarity_score,3),round(subjectivity_score,3)  

### Complex word count
def complex_count(words):
  complex_words = [word for word in words if (len(hyphenate.hyphenate_word(word)))>2]  
  return len(complex_words)

### Syllable per word
def syllable_per_word_count(words):
  count = 0
  for word in words: 
   count += len(hyphenate.hyphenate_word(word))  
  return round(float(count/len(words)),3)

### Calculating fog index
def readability_scores(words):
  average_sentence_length = num_total_words/num_sentences
  percentage_complex_words = complex_count(words)/num_total_words
  fog_index = 0.4 * (average_sentence_length + percentage_complex_words)
  return round(average_sentence_length,3),round(percentage_complex_words,3),round(fog_index,3)  

### avg number of words per sentence
def avg_num_words_per_sent():
  avg_num_words_per_sent = num_total_words/num_sentences
  return round(avg_num_words_per_sent,3)  

### avg word length
def avg_word_length(words):
  count = 0
  for word in words:
    length = 0
    if(word.isalpha()):
      count+=len(word)
    else:
      for chr in word:
        if(chr.isalpha()): length+=1
        else: continue
      count+= length 

  return round(count/len(words),3) 

### personal pronoun count
def personal_pronoun_count(words,words_):
  p_p_list = ['i','we','my','ours','us']
  count = 0
  for (word,word_) in zip(words,words_):
    if word in p_p_list:
      if (word_ == 'US'): continue
      count+=1  
  return count

alphabetic_only,lower_case_only,num_total_words,num_sentences,num_total_words_nltk = preprocessing(3)                   ### Preprocessing of text and filtering numeric and seminumerics 

num_total_words_nltk = cleaned_words_nltk(lower_case_only)                           ### Total number of words after cleaning using NLTK stopwords

positive_score,negative_score,polarity_score,subjectivity_score = sentimental_scores(lower_case_only)       ### Sentimental Scores

average_sentence_length,percentage_complex_words,fog_index = readability_scores(lower_case_only)            ### Readability Scores

avg_num_words_persent = avg_num_words_per_sent()                                            ### Average number of words per sentence

avg_word = avg_word_length(lower_case_only)                                                          ### Average word length

p_p_count = personal_pronoun_count(lower_case_only,alphabetic_only)                            ### Count of personal pronouns

num_complex = complex_count(lower_case_only)                                                                ### Complex word count

syllables_per_word = syllable_per_word_count(lower_case_only)                                               ### Syllables per word

print('Total number of words after cleaning using NLTK stopword : ', num_total_words_nltk, '\n')
print('Positive score : ', positive_score ,'\n')
print('Negative score : ', negative_score , '\n')
print('Polarity score : ', polarity_score , '\n')
print('Subjectivity score : ', subjectivity_score , '\n')
print('Average sentence length : ', average_sentence_length , '\n')
print('percentage complex words : ', percentage_complex_words , '\n')
print('Average number of words per sentence : ', avg_num_words_persent , '\n')
print('Average word length : ', avg_word, '\n')
print('Count of personal pronouns : ', p_p_count , '\n')
print('Complex word count : ', num_complex , '\n')
print('Syllables per word : ', syllables_per_word , '\n')

url_path = "/content/drive/MyDrive/20211030 Test Assignment/Input.xlsx" ### Input URL path
input_url = read_url(url_path)
saved_txt_dir = '/content/drive/MyDrive/test_assignment/text_files_nohead' ### Saved text (scraped text) path
pos_word_path = '/content/drive/MyDrive/20211030 Test Assignment/MasterDictionary/positive-words.txt' ### Positive words path
neg_word_path = '/content/drive/MyDrive/20211030 Test Assignment/MasterDictionary/negative-words.txt' ### Negative words path 
stopwords_dir = '/content/drive/MyDrive/20211030 Test Assignment/StopWords'  ### Stopwords path
output_path = '/content/drive/MyDrive/test_assignment/Output files/output2.csv'  ### Output path

listy = [[] for i in range(len(input_url['URL_ID']))]

for i in range(len(input_url['URL_ID'])):
  if(i==7 or i==20 or i==107): 
    listy[i].append(input_url['URL_ID'][i])
    listy[i].append(input_url['URL'][i])
  else:
    listy[i].append(input_url['URL_ID'][i])
    listy[i].append(input_url['URL'][i])
    
    alphabetic_only,lower_case_only,num_total_words,num_sentences,num_total_words_nltk = preprocessing(i,saved_txt_dir)       ### Preprocessing of text and filtering numeric and seminumerics 

    positive_score,negative_score,polarity_score,subjectivity_score = sentimental_scores(lower_case_only,stopwords_dir,pos_word_path,neg_word_path)       ### Sentimental Scores
    listy[i].append(positive_score)
    listy[i].append(negative_score)
    listy[i].append(polarity_score)
    listy[i].append(subjectivity_score)

    average_sentence_length,percentage_complex_words,fog_index = readability_scores(lower_case_only)            ### Readability Scores
    listy[i].append(average_sentence_length)
    listy[i].append(percentage_complex_words)
    listy[i].append(fog_index)

    avg_num_words_per_sent_ = avg_num_words_per_sent()                                            ### Average number of words per sentence
    listy[i].append(avg_num_words_per_sent_)

    num_complex = complex_count(lower_case_only)                                                                ### Complex word count
    listy[i].append(num_complex)

    listy[i].append(num_total_words_nltk)                                                                       ### Total number of words after cleaning using NLTK stopwords
    
    syllables_per_word = syllable_per_word_count(lower_case_only)                                               ### Syllables per word
    listy[i].append(syllables_per_word)

    p_p_count = personal_pronoun_count(lower_case_only,alphabetic_only)                            ### Count of personal pronouns
    listy[i].append(p_p_count)

    avg_word_length_ = avg_word_length(lower_case_only)                                                          ### Average word length
    listy[i].append(avg_word_length_)  

df = pd.DataFrame(listy,
               columns =['URL_ID', 'URL','Positive Score','Negative Score','Polarity Score','Subjectivity Score','Avg Sentence Length','Percentage of Complex Words','Fog Index','Avg Number of Words Per Sentence','Complex Word Count','Word Count (Post NLTK cleaning)','Syllable Per Word','Personal Pronouns Count','Avg Word Length'])
df.to_csv(output_path)