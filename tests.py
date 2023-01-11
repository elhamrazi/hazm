# coding: utf-8

from __future__ import unicode_literals
import sys, inspect, doctest, unittest
from hazm import *

modules = {
	'persica': persica_reader,
	'hamshahri': hamshahri_reader,
	'bijankhan': bijankhan_reader,
	'peykare': peykare_reader,
	'dadegan': dadegan_reader,
	'valency': verb_valency_reader,
	'treebank': treebank_reader,
	'sentipers': senti_pers_reader,
	'degarbayan': degarbayan_reader,
	'tnews': tnews_reader,
	'quran': quran_corpus_reader,
	'miras_text': miras_text_reader,
	'sentence_tokenizer': sentence_tokenizer,
	'word_tokenizer': word_tokenizer,
	'splitter': token_splitter,
	'normalizer': normalizer,
	'stemmer': stemmer,
	'lemmatizer': lemmatizer,
	'tagger': sequence_tagger,
	'postagger': pos_tagger,
	'chunker': chunker,
	'parser': dependency_parser,
	'informal_normalizer': informal_normalizer
}


class UnicodeOutputChecker(doctest.OutputChecker):

	def check_output(self, want, got, optionflags):
		try:
			want, got = eval(want), eval(got)
		except:
			pass

		try:
			got = got.decode('unicode-escape')
			want = want.replace('آ', 'ا')  # decode issue
		except:
			pass

		if type(want) == unicode:
			want = want.replace('٫', '.')  # eval issue

		return want == got


if __name__ == '__main__':
	# test all modules if no one specified
	all_modules = len(sys.argv) < 2

	suites = []
	checker = UnicodeOutputChecker() if utils.PY2 else None
	for name, object in modules.items():
		if all_modules or name in sys.argv:
			suites.append(doctest.DocTestSuite(inspect.getmodule(object), checker=checker))

	if not utils.PY2 and all_modules:
		suites.append(doctest.DocFileSuite('README.md'))

	failure = False
	runner = unittest.TextTestRunner(verbosity=2)
	for suite in suites:
		if not runner.run(suite).wasSuccessful():
			failure = True

	if failure:
		exit(1)
