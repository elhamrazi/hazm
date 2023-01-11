
from .word_tokenizer import word_tokenizer
from .sentence_tokenizer import sentence_tokenizer
from .token_splitter import token_splitter
from .hamshahri_reader import hamshahri_reader
from .persica_reader import persica_reader
from .bijankhan_reader import bijankhan_reader
from .peykare_reader import peykare_reader
from .verb_valency_reader import verb_valency_reader
from .dadegan_reader import dadegan_reader
from .treebank_reader import treebank_reader
from .wikipedia_reader import wikipedia_reader
from .senti_pers_reader import senti_pers_reader
from .degarbayan_reader import degarbayan_reader
from .quran_corpus_reader import quran_corpus_reader
from .tnews_reader import tnews_reader
from .miras_text_reader import miras_text_reader
from .normalizer import normalizer
from .informal_normalizer import informal_normalizer, InformalLemmatizer
from .stemmer import stemmer
from .lemmatizer import lemmatizer
from .sequence_tagger import sequence_tagger, IOBTagger
from .pos_tagger import pos_tagger, StanfordPOSTagger
from .chunker import chunker, RuleBasedchunker, tree2brackets
from .dependency_parser import dependency_parser, MaltParser, TurboParser


from .utils import words_list, stopwords_list


def sent_tokenize(text):
	if not hasattr(sent_tokenize, 'tokenizer'):
		sent_tokenize.tokenizer = sentence_tokenizer()
	return sent_tokenize.tokenizer.tokenize(text)


def word_tokenize(sentence):
	if not hasattr(word_tokenize, 'tokenizer'):
		word_tokenize.tokenizer = word_tokenizer()
	return word_tokenize.tokenizer.tokenize(sentence)
