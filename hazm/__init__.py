
from .word_tokenizer import WordTokenizer
from .sentence_tokenizer import SentenceTokenizer
from .token_splitter import TokenSplitter
from .hamshahri_reader import HamshahriReader
from .persica_reader import PersicaReader
from .bijankhan_reader import BijankhanReader
from .peykare_reader import PeykareReader
from .verb_valency_reader import VerbValencyReader
from .dadegan_reader import DadeganReader
from .treebank_reader import TreebankReader
from .wikipedia_reader import WikipediaReader
from .senti_pers_reader import SentiPersReader
from .degarbayan_reader import DegarbayanReader
from .quran_corpus_reader import QuranCorpusReader
from .tnews_reader import TNewsReader
from .miras_text_reader import MirasTextReader
from .normalizer import Normalizer
from .informal_normalizer import InformalNormalizer, InformalLemmatizer
from .stemmer import Stemmer
from .lemmatizer import Lemmatizer
from .sequence_tagger import SequenceTagger, IOBTagger
from .pos_tagger import POSTagger, StanfordPOSTagger
from .chunker import Chunker, RuleBasedChunker, tree2brackets
from .dependency_parser import DependencyParser, MaltParser, TurboParser


from .utils import words_list, stopwords_list


def sent_tokenize(text):
	if not hasattr(sent_tokenize, 'tokenizer'):
		sent_tokenize.tokenizer = SentenceTokenizer()
	return sent_tokenize.tokenizer.tokenize(text)


def word_tokenize(sentence):
	if not hasattr(word_tokenize, 'tokenizer'):
		word_tokenize.tokenizer = WordTokenizer()
	return word_tokenize.tokenizer.tokenize(sentence)
