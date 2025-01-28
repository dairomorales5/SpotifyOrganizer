# Description: This class is used to summarize text using the TextRank algorithm.
# Adapted from https://github.com/codelucas/newspaper/blob/master/newspaper/nlp.py
# adding support for multiple languages and optimized lemmatization.

import nltk
import json
import math
import spacy
from langdetect import detect
from collections import Counter
from nltk.corpus import stopwords as nltk_stopwords
from langdetect.lang_detect_exception import LangDetectException

class Nlp():
  def __init__(self, lemma_file='', languages=['english']):
    self.ideal = 20.0
    self.NUM_KEYWORDS = 10
    self.languages = languages
    self.stopwords = self.load_stopwords()
    self.tokenizers = self.load_tokenizers()
    self.nlps = self.load_spacy_models()
    self.lemma_directory = lemma_file if lemma_file else 'lemma_file.json'
    if lemma_file:
      with open(lemma_file, 'r', encoding='utf-8') as f:
        self.lemma_file = json.load(f)
    else:
      self.lemma_file = {}
  
  def load_stopwords(self):
    """
    Loads stopwords for all specified languages
    """
    stopwords = {}
    for lang in self.languages:
      try:
        nltk.download('stopwords')
        stopwords[lang] = set(nltk_stopwords.words(lang))
      except OSError:
        stopwords[lang] = set()
    return stopwords
  
  def load_tokenizers(self):
    """
    Loads tokenizers for all specified languages
    """
    tokenizers = {}
    for lang in self.languages:
      try:
        tokenizers[lang] = nltk.data.load(f'tokenizers/punkt/{lang}.pickle')
      except LookupError:
        nltk.download('punkt')
        nltk.download('punkt_tab')
        tokenizers[lang] = nltk.data.load(f'tokenizers/punkt/{lang}.pickle')
    return tokenizers
  
  def load_spacy_models(self):
    """
    Loads SpaCy models for all specified languages
    """
    spacy_models = {
      'spanish': 'es_core_news_sm',
      'english': 'en_core_web_sm'
    }
    nlps = {}
    for lang in self.languages:
      model_name = spacy_models.get(lang)
      if model_name:
        try:
          nlps[lang] = spacy.load(model_name)
        except OSError:
          spacy.cli.download(model_name)
          nlps[lang] = spacy.load(model_name)
      else:
        nlps[lang] = None
    return nlps

  def summarize(self, text='', title='', max_sents=5):
    if not text or max_sents <= 0:
        return []

    try:
      lang = detect(text)
      lang = lang if lang in self.languages else 'english'
    except LangDetectException:
      lang = 'english'
    summaries = []
    sentences = self.split_sentences(text, lang)
    keys = self.keywords(text, lang)

    # Score sentences, and use the top 5 or max_sents sentences
    if title:
        titleWords = self.split_words(title, lang)
        ranks = self.score(sentences, keys, lang, titleWords).most_common(max_sents)
    else:
        ranks = self.score(sentences, keys, lang).most_common(max_sents)
    for rank in ranks:
        summaries.append(rank[0])
    summaries.sort(key=lambda summary: summary[0])
    return [summary[1] for summary in summaries]
  
  def score(self, sentences, keywords, lang, titleWords=[]):
    """Score sentences based on different features
    """
    senSize = len(sentences)
    ranks = Counter()
    for i, s in enumerate(sentences):
        sentence = self.split_words(s, lang)
        sentenceLength = self.length_score(len(sentence))
        sentencePosition = self.sentence_position(i + 1, senSize)
        sbsFeature = self.sbs(sentence, keywords)
        dbsFeature = self.dbs(sentence, keywords)
        frequency = (sbsFeature + dbsFeature) / 2.0 * 10.0
        # Weighted average of scores from four categories
        if titleWords:
            titleFeature = self.title_score(titleWords, sentence, lang)
        else:
            titleFeature = 0
        totalScore = (frequency*2.0 + titleFeature*1.5 +
                      sentenceLength*1.0 + sentencePosition*1.0)/4.0
        ranks[(i, s)] = totalScore
    return ranks
  
  @staticmethod
  def sbs(words, keywords):
    score = 0.0
    if (len(words) == 0):
        return 0
    for word in words:
        if word in keywords:
            score += keywords[word]
    return (1.0 / math.fabs(len(words)) * score) / 10.0

  @staticmethod
  def dbs(words, keywords):
      if (len(words) == 0):
          return 0
      summ = 0
      first = []
      second = []

      for i, word in enumerate(words):
          if word in keywords:
              score = keywords[word]
              if first == []:
                  first = [i, score]
              else:
                  second = first
                  first = [i, score]
                  dif = first[0] - second[0]
                  summ += (first[1] * second[1]) / (dif ** 2)
      # Number of intersections
      k = len(set(keywords.keys()).intersection(set(words))) + 1
      return (1 / (k * (k + 1.0)) * summ)
  
  def split_words(self, text, lang):
    """Split a string into array of words
    """
    try:
      text = re.sub(r'https?://\S+|www\.\S+', '', text)  # remove urls
      text = re.sub(r'[^\w ]', '', text)  # strip special chars
      text = [x.strip('.').lower() for x in text.split()]
      text = [x for x in text if x not in self.stopwords[lang]]
      #Update lemma_file
      lemas_no_calculados = set(text) - set(self.lemma_file.keys())
      if lemas_no_calculados:
          for word in lemas_no_calculados:
              doc = self.nlps[lang](word)
              lema = doc[0].lemma_
              self.lemma_file[word] = lema
          with open(self.lemma_directory, 'w') as f:
              json.dump(self.lemma_file, f)
    
      lemas = [self.lemma_file[word] for word in text]
      return lemas
    except TypeError:
        return None
    
  def keywords(self, text, lang):
    """Get the top 10 keywords and their frequency scores ignores blacklisted
    words in stopwords, counts the number of occurrences of each word, and
    sorts them in reverse natural order (so descending) by number of
    occurrences.
    """
    text = self.split_words(text, lang)
    # of words before removing blacklist words
    if text:
        num_words = len(text)
        text = [x for x in text if x not in self.stopwords[lang]]
        freq = {}
        for word in text:
            if word in freq:
                freq[word] += 1
            else:
                freq[word] = 1

        min_size = min(self.NUM_KEYWORDS, len(freq))
        keywords = sorted(freq.items(),
                          key=lambda x: (x[1], x[0]),
                          reverse=True)
        keywords = keywords[:min_size]
        keywords = dict((x, y) for x, y in keywords)

        for k in keywords:
            articleScore = keywords[k] * 1.0 / max(num_words, 1)
            keywords[k] = articleScore * 1.5 + 1
        return dict(keywords)
    else:
        return dict()
  
  def split_sentences(self, text, lang):
    """Split a large string into sentences
    """
    sentences = self.tokenizers[lang].tokenize(text)
    sentences = [x.replace('\n', '') for x in sentences if len(x) > 10]
    return sentences

  def length_score(self, sentence_len):
    return 1 - math.fabs(self.ideal - sentence_len) / self.ideal

  def title_score(self, title, sentence, lang):
    if title:
        title = [x for x in title if x not in self.stopwords[lang]]
        count = 0.0
        for word in sentence:
            if (word not in self.stopwords[lang] and word in title):
                count += 1.0
        return count / max(len(title), 1)
    else:
        return 0
    
  @staticmethod
  def sentence_position(i, size):
    """Different sentence positions indicate different
    probability of being an important sentence.
    """
    normalized = i * 1.0 / size
    if (normalized > 1.0):
        return 0
    elif (normalized > 0.9):
        return 0.15
    elif (normalized > 0.8):
        return 0.04
    elif (normalized > 0.7):
        return 0.04
    elif (normalized > 0.6):
        return 0.06
    elif (normalized > 0.5):
        return 0.04
    elif (normalized > 0.4):
        return 0.05
    elif (normalized > 0.3):
        return 0.08
    elif (normalized > 0.2):
        return 0.14
    elif (normalized > 0.1):
        return 0.23
    elif (normalized > 0):
        return 0.17
    else:
        return 0