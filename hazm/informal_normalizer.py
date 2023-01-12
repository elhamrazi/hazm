# coding: utf-8

"""این ماژول شامل کلاس‌ها و توابعی برای نرمال‌سازی متن‌های محاوره‌ای است.
"""

from __future__ import unicode_literals
import codecs
from .utils import informal_verbs, informal_words, NUMBERS, default_verbs
from .normalizer import Normalizer
from .lemmatizer import Lemmatizer
from .stemmer import Stemmer
from .word_tokenizer import *
from .sentence_tokenizer import *


class InformalNormalizer(Normalizer):
    """این کلاس شامل توابعی برای نرمال‌سازی متن‌های محاوره‌ای است.

    Args:
            verb_file (str, optional): فایل حاوی افعال محاوره‌ای.
            word_file (str, optional): فایل حاوی کلمات محاوره‌ای.
            seperation_flag (bool, optional): اگر `True` باشد و در بخشی از متن به فاصله نیاز بود آن فاصله درج می‌شود.
            **kargs: پارامترهای نامدارِ اختیاری

    """

    def __init__(
        self,
        verb_file=informal_verbs,
        word_file=informal_words,
        seperation_flag=False,
        **kargs
    ):
        self.seperation_flag = seperation_flag
        self.lemmatizer = Lemmatizer()
        self.ilemmatizer = InformalLemmatizer()
        self.stemmer = Stemmer()
        super(InformalNormalizer, self).__init__(**kargs)

        self.sent_tokenizer = SentenceTokenizer()
        self.word_tokenizer = WordTokenizer()

        with codecs.open(verb_file, encoding="utf8") as vf:
            self.past_verbs = {}
            self.present_verbs = {}
            for f, i, flag in map(lambda x: x.strip().split(" ", 2), vf):
                splited_f = f.split("#")
                self.present_verbs.update({i: splited_f[1]})
                self.past_verbs.update({splited_f[0]: splited_f[0]})
        with codecs.open(default_verbs, encoding="utf8") as vf:
            for f, i in map(lambda x: x.strip().split("#", 2), vf):
                self.present_verbs.update({i: i})
                self.past_verbs.update({f: f})

        def informal_to_formal_conjucation(i, f, flag):
            iv = self.informal_conjugations(i)
            fv = self.lemmatizer.conjugations(f)
            res = {}
            if flag:
                for i, j in zip(iv, fv[48:]):
                    res[i] = j
                    if "‌" in i:
                        res[i.replace("‌", "")] = j
                        res[i.replace("‌", " ")] = j
                    if i.endswith("ین"):
                        res[i[:-1] + "د"] = j
            else:
                for i, j in zip(iv[8:], fv[56:]):
                    res[i] = j
                    if "‌" in i:
                        res[i.replace("‌", "")] = j
                        res[i.replace("‌", " ")] = j
                    if i.endswith("ین"):
                        res[i[:-1] + "د"] = j

            return res

        with codecs.open(verb_file, encoding="utf8") as vf:
            self.iverb_map = {}
            for f, i, flag in map(lambda x: x.strip().split(" ", 2), vf):
                self.iverb_map.update(informal_to_formal_conjucation(i, f, flag))

        with codecs.open(word_file, encoding="utf8") as wf:
            self.iword_map = dict(map(lambda x: x.strip().split(" ", 1), wf))

        self.words = set()
        if self.seperation_flag:
            self.words.update(self.iword_map.keys())
            self.words.update(self.iword_map.values())
            self.words.update(self.iverb_map.keys())
            self.words.update(self.iverb_map.values())
            self.words.update(self.lemmatizer.words)
            self.words.update(self.lemmatizer.verbs.keys())
            self.words.update(self.lemmatizer.verbs.values())

    def split_token_words(self, token):
        """هرجایی در متن فاصله نیاز بود قرار می‌دهد.

        متأسفانه در برخی از متن‌ها، به بهانهٔ صرفه‌جویی در زمان یا از سرِ تنبلی،
        فاصله‌گذاری‌ها درست رعایت نمی‌شود. مثلاً جملهٔ «تو را دوست دارم.» به این
        شکل نوشته می‌شود: «تورادوست دارم.» این تابع فواصل ضروری را در متن
        ایجاد می‌کند و آن را به شکل صحیح برمی‌گرداند.

        Args:
                token (str): توکنی که باید فاصله‌گذاری شود.

        Returns:
                (str): توکنی با فاصله‌گذاری صحیح.
        """

        def shekan(token):
            res = [""]
            for i in token:
                res[-1] += i
                if i in set(["ا", "د", "ذ", "ر", "ز", "ژ", "و"] + list(NUMBERS)):
                    res.append("")
            while "" in res:
                res.remove("")
            return res

        def perm(lst):
            if len(lst) > 1:
                up = perm(lst[1:])
            else:
                return [lst]
            res = []
            for i in up:
                res.append([lst[0]] + i)
                res.append([lst[0] + i[0]] + i[1:])
            res.sort(key=len)
            return res

        token = re.sub(r"(.)\1{2,}", r"\1", token)
        ps = perm(shekan(token))
        for c in ps:
            if set(map(lambda x: self.ilemmatizer.lemmatize(x), c)).issubset(
                self.words
            ):
                return " ".join(c)
        return token

    def normalized_word(self, word):
        """اشکال مختلف نرمالایزشدهٔ کلمه را برمی‌گرداند.

        Examples:
                >>> normalizer = InformalNormalizer()
                >>> normalizer.normalized_word('می‌رم')
                ['می‌روم', 'می‌رم']

                >>> normalizer = InformalNormalizer(seperation_flag=True)
                >>> normalizer.normalized_word('صداوسیماجمهوری')
                ['صداوسیما جمهوری', 'صداوسیماجمهوری']

        Args:
                word(str): کلمه‌ای که باید نرمال‌سازی شود.

        Returns:
                (List[str]): اشکال نرمالایزشدهٔ کلمه.
        """

        def analyze_word(word):
            endWordsList = [
                "هاست",
                "هایی",
                "هایم",
                "ترین",
                "ایی",
                "انی",
                "شان",
                "شون",
                "است",
                "تان",
                "تون",
                "مان",
                "مون",
                "هام",
                "هاش",
                "های",
                "طور",
                "ها",
                "تر",
                "ئی",
                "یی",
                "یم",
                "ام",
                "ای",
                "ان",
                "هم",
                "رو",
                "یت",
                "ه",
                "ی",
                "ش",
                "و",
                "ا",
                "ت",
                "م",
            ]

            return_list = []

            collectionOfWordAndSuffix = []

            FoundEarly = False

            midWordCondidate = []

            if word.endswith("‌") or word.endswith("‎"):
                word = word[:-1]

            if word in self.lemmatizer.words or word in self.iword_map:
                if word in self.lemmatizer.words:
                    collectionOfWordAndSuffix.append({"word": word, "suffix": []})
                if word in self.iword_map:
                    collectionOfWordAndSuffix.append(
                        {"word": selsliceWordf.iword_map[word], "suffix": []}
                    )
                FoundEarly = True

            if not FoundEarly:
                for endWord in endWordsList:
                    if word.endswith(endWord):
                        slice_word = word[: -1 * len(endWord)]
                        if (
                            slice_word in self.lemmatizer.words
                            or slice_word in self.iword_map
                        ):
                            if slice_word in self.lemmatizer.words:
                                collectionOfWordAndSuffix.append(
                                    {"word": slice_word, "suffix": [endWord]}
                                )
                            if slice_word in self.iword_map:
                                collectionOfWordAndSuffix.append(
                                    {
                                        "word": self.iword_map[slice_word],
                                        "suffix": [endWord],
                                    }
                                )
                        else:
                            midWordCondidate.append(slice_word)
                            midWordCondidate.append([endWord])

                for endWord in endWordsList:
                    for i in range(len(midWordCondidate) - 1):
                        if i % 2 == 1:
                            continue
                        mid_word = midWordCondidate[i]
                        midWordEndWordList = midWordCondidate[i + 1]
                        if mid_word.endswith(endWord):
                            slice_word = mid_word[: -1 * len(endWord)]
                            if (
                                slice_word in self.lemmatizer.words
                                or slice_word in self.iword_map
                            ):
                                if slice_word in self.lemmatizer.words:
                                    collectionOfWordAndSuffix.append(
                                        {
                                            "word": slice_word,
                                            "suffix": [endWord] + midWordEndWordList,
                                        }
                                    )
                                if slice_word in self.iword_map:
                                    collectionOfWordAndSuffix.append(
                                        {
                                            "word": self.iword_map[slice_word],
                                            "suffix": [endWord] + midWordEndWordList,
                                        }
                                    )

            for i in range(len(collectionOfWordAndSuffix)):
                newPossibelWordList = append_suffix_to_word(
                    collectionOfWordAndSuffix[i]
                )
                for j in range(len(newPossibelWordList)):
                    newPossibelWord = newPossibelWordList[j]
                    if newPossibelWord not in return_list:
                        return_list.append(newPossibelWord)

            return return_list

        def analyze_verb_word(word):

            if word in self.past_verbs:
                word = self.past_verbs[word]
                return [word]

            if word in self.iword_map:
                return []

            if word in self.lemmatizer.words:
                if word[-1] == "ن":
                    None
                else:
                    return []

            return_list = []

            collectionOfVerbList = []

            endVerbList = [
                "یم",
                "دم",
                "دیم",
                "ید",
                "دی",
                "دید",
                "ند",
                "دن",
                "دند",
                "ین",
                "دین",
                "ست",
                "ستم",
                "ستی",
                "ستیم",
                "ستید",
                "ستند",
                "م",
                "ی",
                "ه",
                "د",
                "ن",
            ]

            for end_verb in endVerbList:
                if word.endswith(end_verb):
                    if end_verb == "ین":
                        collectionOfVerbList.append({"word": word[:-2], "suffix": "ید"})
                    elif end_verb == "ن":
                        collectionOfVerbList.append({"word": word[:-1], "suffix": "ن"})
                        collectionOfVerbList.append({"word": word[:-1], "suffix": "ند"})
                    elif end_verb == "ه":
                        if len(word) > 1:
                            if word[-2] != "د":
                                collectionOfVerbList.append(
                                    {"word": word[:-1], "suffix": "د"}
                                )
                            collectionOfVerbList.append(
                                {"word": word[:-1], "suffix": "ه"}
                            )
                        else:
                            collectionOfVerbList.append(
                                {"word": word[:-1], "suffix": "ه"}
                            )
                    else:
                        collectionOfVerbList.append(
                            {"word": word[: -1 * len(end_verb)], "suffix": end_verb}
                        )
            collectionOfVerbList.append({"word": word, "suffix": ""})
            collectionOfVerbList2 = []
            for i in range(len(collectionOfVerbList)):
                main_word = collectionOfVerbList[i]["word"]
                collectionOfVerbList[i]["preffix"] = ""
                if main_word.startswith("بر"):
                    modified_word = main_word[2:]
                    newMainWord = ""
                    if modified_word.startswith("نمی"):
                        collectionOfVerbList[i]["preffix"] = "برنمی"
                        newMainWord = modified_word[3:]
                    elif modified_word.startswith("می"):
                        collectionOfVerbList[i]["preffix"] = "برمی"
                        newMainWord = modified_word[2:]
                    elif modified_word.startswith("ن"):
                        collectionOfVerbList[i]["preffix"] = "برن"
                        newMainWord = modified_word[1:]
                    elif modified_word.startswith("بی"):
                        collectionOfVerbList[i]["preffix"] = "بربی"
                        newMainWord = modified_word[2:]
                    elif modified_word.startswith("ب"):
                        collectionOfVerbList[i]["preffix"] = "برب"
                        newMainWord = modified_word[1:]
                    else:
                        collectionOfVerbList[i]["preffix"] = "بر"
                        newMainWord = modified_word
                        collectionOfVerbList2.append(
                            {
                                "word": main_word,
                                "preffix": "",
                                "suffix": collectionOfVerbList[i]["suffix"],
                            }
                        )

                    if newMainWord != "":
                        collectionOfVerbList[i]["word"] = newMainWord
                elif main_word.startswith("نمی"):
                    collectionOfVerbList[i]["preffix"] = "نمی"
                    collectionOfVerbList[i]["word"] = main_word[3:]
                elif main_word.startswith("می"):
                    collectionOfVerbList[i]["preffix"] = "می"
                    collectionOfVerbList[i]["word"] = main_word[2:]
                elif main_word.startswith("ن"):
                    collectionOfVerbList[i]["preffix"] = "ن"
                    collectionOfVerbList[i]["word"] = main_word[1:]
                    collectionOfVerbList2.append(
                        {
                            "word": main_word,
                            "preffix": "",
                            "suffix": collectionOfVerbList[i]["suffix"],
                        }
                    )

                elif main_word.startswith("بی"):
                    collectionOfVerbList[i]["preffix"] = "بی"
                    collectionOfVerbList[i]["word"] = main_word[2:]
                elif main_word.startswith("ب"):
                    collectionOfVerbList[i]["preffix"] = "ب"
                    collectionOfVerbList[i]["word"] = main_word[1:]
                    collectionOfVerbList2.append(
                        {
                            "word": main_word,
                            "preffix": "",
                            "suffix": collectionOfVerbList[i]["suffix"],
                        }
                    )

            for i in range(len(collectionOfVerbList2)):
                collectionOfVerbList.append(collectionOfVerbList2[i])

            collectionOfRealVerbList = []
            for i in range(len(collectionOfVerbList)):
                main_word = collectionOfVerbList[i]["word"]
                if main_word.startswith("‌") or main_word.startswith("‎"):
                    main_word = main_word[1:]

                if main_word in self.past_verbs:
                    collectionOfVerbList[i]["word"] = self.past_verbs[main_word]
                    collectionOfRealVerbList.append(collectionOfVerbList[i])
                if main_word in self.present_verbs:
                    collectionOfVerbList[i]["word"] = self.present_verbs[main_word]
                    collectionOfRealVerbList.append(collectionOfVerbList[i])

            for i in range(len(collectionOfRealVerbList)):
                preffix = collectionOfRealVerbList[i]["preffix"]
                suffix = collectionOfRealVerbList[i]["suffix"]
                main_word = collectionOfRealVerbList[i]["word"]
                return_word = preffix
                if preffix.endswith("می"):
                    return_word += "‌"
                return_word += main_word
                return_word += suffix
                if main_word != "":
                    if return_word not in return_list:
                        return_list.append(return_word)

            return return_list

        def append_suffix_to_word(OneCollectionOfWordAndSuffix):
            main_word = OneCollectionOfWordAndSuffix["word"]
            suffix_list = OneCollectionOfWordAndSuffix["suffix"]
            adhesive_alphabet = {
                "ب": "ب",
                "پ": "پ",
                "ت": "ت",
                "ث": "ث",
                "ج": "ج",
                "چ": "چ",
                "ح": "ح",
                "خ": "خ",
                "س": "س",
                "ش": "ش",
                "ص": "ص",
                "ض": "ض",
                "ع": "ع",
                "غ": "غ",
                "ف": "ف",
                "ق": "ق",
                "ک": "ک",
                "گ": "گ",
                "ل": "ل",
                "م": "م",
                "ن": "ن",
                "ه": "ه",
                "ی": "ی",
            }
            return_list = []
            return_word = main_word
            returnWord2 = None
            returnWord3 = None
            if len(suffix_list) == 0:
                return [return_word]
            if len(suffix_list) > 1:
                if suffix_list[0] == "ه" and suffix_list[1] == "ا":
                    suffix_list[0] = "ها"
                    suffix_list.remove(suffix_list[1])
                if suffix_list[0] == "ه" and suffix_list[1] == "است":
                    suffix_list[0] = "هاست"
                    suffix_list.remove(suffix_list[1])
                if suffix_list[0] == "ت" and suffix_list[1] == "ا":
                    suffix_list[0] = "تا"
                    suffix_list.remove(suffix_list[1])
            for i in range(len(suffix_list)):
                if suffix_list[i] == "شون":
                    return_word += "شان"
                elif suffix_list[i] == "تون":
                    return_word += "تان"
                elif suffix_list[i] == "مون":
                    return_word += "مان"
                elif suffix_list[i] == "هام":
                    try:
                        var = adhesive_alphabet[return_word[-1]]
                        return_word += "‌"
                    except:
                        None
                    return_word += "هایم"
                elif suffix_list[i] == "ها":
                    try:
                        var = adhesive_alphabet[return_word[-1]]
                        return_word += "‌"
                    except:
                        None
                    return_word += "ها"
                elif (
                    suffix_list[i] == "ا"
                    and suffix_list[len(suffix_list) - 1] == "ا"
                    and not return_word.endswith("ه")
                ):
                    try:
                        var = adhesive_alphabet[return_word[-1]]
                        return_word += "‌"
                    except:
                        None
                    return_word += "ها"
                elif suffix_list[i] == "و" and suffix_list[len(suffix_list) - 1] == "و":
                    returnWord2 = return_word
                    returnWord2 += " و"
                    return_word += " را"

                elif (
                    suffix_list[i] == "رو" and suffix_list[len(suffix_list) - 1] == "رو"
                ):
                    return_word += " را"

                elif suffix_list[i] == "ه" and suffix_list[len(suffix_list) - 1] == "ه":
                    returnWord2 = return_word
                    returnWord2 += "ه"
                    returnWord3 = return_word
                    returnWord3 += " است"
                    return_word += "ه است"
                else:
                    return_word += suffix_list[i]
            return_list.append(return_word)
            if returnWord2 != None:
                return_list.append(returnWord2)
            if returnWord3 != None:
                return_list.append(returnWord3)
            return return_list

        def straight_forward_result(word):
            straightForwardDic = {
                "ب": ["به"],
                "ک": ["که"],
                "ش": ["اش"],
                "بش": ["بهش"],
                "رو": ["را", "رو"],
                "پایتون": ["پایتون"],
                "دست": ["دست"],
                "دستی": ["دستی"],
                "دستم": ["دستم"],
                "دین": ["دین"],
                "شین": ["شین"],
                "سراتو": ["سراتو"],
                "فالو": ["فالو"],
                "هرجا": ["هرجا"],
                "میدان": ["میدان"],
                "میدون": ["میدان"],
                "کفا": ["کفا"],
                "ویا": ["و یا"],
                "نشد": ["نشد"],
                "شو": ["شو"],
                "مشیا": ["مشیا"],
                "پلاسما": ["پلاسما"],
                "فیلیمو": ["فیلیمو"],
                "پاشو": ["پاشو"],
                "میر": ["میر"],
                "بارم": ["بار هم", "بارم"],
                "برند": ["برند"],
                "کنه": ["کند"],
                "بتونه": ["بتواند"],
                "باشه": ["باشد"],
                "بخوان": ["بخوان"],
                "بدم": ["بدم"],
                "برم": ["برم"],
                "بده": ["بده"],
                "نده": ["نده"],
                "شهرو": ["شهرو"],
                "شیرو": ["شیرو"],
                "نگذاشته": ["نگذاشته"],
                "نگرفته": ["نگرفته"],
                "نمیشناخته": ["نمی‌شناخته"],
                "نمی‌شناخته": ["نمی‌شناخته"],
                "بشین": ["بشین"],
                "هارو": ["ها را"],
                "مارو": ["ما را"],
                "میخواسته": ["می‌خواسته"],
                "می‌خواسته": ["می‌خواسته"],
                "نمیخواسته": ["نمی‌خواسته"],
                "نمی‌خواسته": ["نمی‌خواسته"],
                "میتوانسته": ["می‌توانسته"],
                "می‌توانسته": ["می‌توانسته"],
                "میرفته": ["می‌رفته"],
                "می‌رفته": ["می‌رفته"],
                "نشین": ["نشین"],
                "انا": ["انا"],
                "خونی": ["خونی"],
                "خون": ["خون"],
                "یالا": ["یالا"],
                "میخواند": ["می‌خواند"],
                "می‌خواند": ["می‌خواند"],
                "نمیخواند": ["نمی‌خواند"],
                "نمی‌خواند": ["نمی‌خواند"],
                "میده": ["می‌دهد"],
                "می‌ده": ["می‌دهد"],
                "میشه": ["می‌شود"],
                "می‌شه": ["می‌شود"],
                "میشد": ["می‌شد"],
                "می‌شد": ["می‌شد"],
                "میشدم": ["می‌شدم"],
                "می‌شدم": ["می‌شدم"],
                "نمیشد": ["نمی‌شد"],
                "نمی‌شد": ["نمی‌شد"],
                "بردم": ["بردم"],
                "بره": ["بره", "برود"],
                "شم": ["بشوم"],
                "اوست": ["اوست"],
                "بیا": ["بیا"],
                "نیا": ["نیا"],
                "میاد": ["می‌آید"],
                "نشدی": ["نشدی"],
                "بخواند": ["بخواند"],
                "سیا": ["سیا"],
                "میدید": ["می‌دید"],
                "می‌دید": ["می‌دید"],
                "وا": ["وا"],
                "برگشته": ["برگشته"],
                "میخواست": ["می‌خواست"],
                "می‌خواست": ["می‌خواست"],
            }
            try:
                return straightForwardDic[word]
            except:
                return []

        straightForwardWords = straight_forward_result(word)
        if len(straightForwardWords) > 0:
            return straightForwardWords

        verbWordsList = analyze_verb_word(word)
        if len(verbWordsList) > 0:
            return verbWordsList
        possible_words = analyze_word(word)

        main_word = word
        if main_word in possible_words:
            possible_words.remove(main_word)
            possible_words.append(main_word)
        else:
            if len(possible_words) == 0:
                possible_words.append(main_word)

        return possible_words

    def normalize(self, text):
        """متن محاوره‌ای را به متن فارسی معیار تبدیل می‌کند.

        Examples:
                >>> normalizer = InformalNormalizer()
                >>> normalizer.normalize('بابا یه شغل مناسب واسه بچه هام پیدا کردن که به جایی برنمیخوره !')
                [[['بابا'], ['یک'], ['شغل'], ['مناسب'], ['برای'], ['بچه'], ['هایم'], ['پیدا'], ['کردن'], ['که'], ['به'], ['جایی'], ['برنمی\u200cخورد', 'برنمی\u200cخوره'], ['!']]]

                >>> normalizer = InformalNormalizer()
                >>> normalizer.normalize('اجازه بدیم همسرمون در جمع خانواده‌اش احساس آزادی کنه و فکر نکنه که ما دائم هواسمون بهش هست .')
                [[['اجازه'], ['بدهیم'], ['همسرمان'], ['در'], ['جمع'], ['خانواده\u200cاش'], ['احساس'], ['آزادی'], ['کند'], ['و'], ['فکر'], ['نکند', 'نکنه'], ['که'], ['ما'], ['دائم'], ['حواسمان'], ['بهش'], ['هست'], ['.']]]

        Args:
                text (str): متن محاوره‌ای که باید تبدیل به متن فارسی معیار شود.

        Returns:
                (List[List[List[str]]]): متن فارسی معیار.

        """

        text = super(InformalNormalizer, self).normalize(text)
        sents = [
            self.word_tokenizer.tokenize(sentence)
            for sentence in self.sent_tokenizer.tokenize(text)
        ]

        return [[self.normalized_word(word) for word in sent] for sent in sents]

    def informal_conjugations(self, verb):
        """صورت‌های صرفی فعل را در شکل محاوره‌ای تولید می‌کند.

        Args:
                verb (str): فعلی که باید صرف شود.

        Returns:
                (List[str]): صورت‌های صرفی فعل.
        """
        ends = ["م", "ی", "", "یم", "ین", "ن"]
        present_simples = [verb + end for end in ends]
        if verb.endswith("ا"):
            present_simples[2] = verb + "د"
        else:
            present_simples[2] = verb + "ه"
        present_not_simples = ["ن" + item for item in present_simples]
        present_imperfects = ["می‌" + item for item in present_simples]
        present_not_imperfects = ["ن" + item for item in present_imperfects]
        present_subjunctives = [
            item if item.startswith("ب") else "ب" + item for item in present_simples
        ]
        present_not_subjunctives = ["ن" + item for item in present_simples]
        return (
            present_simples
            + present_not_simples
            + present_imperfects
            + present_not_imperfects
            + present_subjunctives
            + present_not_subjunctives
        )


class InformalLemmatizer(Lemmatizer):
    def __init__(self, **kargs):
        super(InformalLemmatizer, self).__init__(**kargs)

        temp = []
        self.words = set(self.words.keys())
        for word in self.words:
            if word.endswith("ً"):
                temp.append(word[:-1])

        self.words.update(temp)

        temp = {}
        for verb in self.verbs:
            if verb.endswith("د"):
                temp[verb[:-1] + "ن"] = self.verbs[verb]

        self.verbs.update(temp)

        with codecs.open(informal_verbs, encoding="utf8") as vf:
            for f, i, flag in map(lambda x: x.strip().split(" ", 2), vf):
                self.verbs.update(dict(map(lambda x: (x, f), self.iconjugations(i))))

        with codecs.open(informal_words, encoding="utf8") as wf:
            self.words.update(map(lambda x: x.strip().split(" ", 1)[0], wf))

    def iconjugations(self, verb):
        ends = ["م", "ی", "", "یم", "ین", "ن"]
        present_simples = [verb + end for end in ends]
        if verb.endswith("ا"):
            present_simples[2] = verb + "د"
        else:
            present_simples[2] = verb + "ه"
        present_not_simples = ["ن" + item for item in present_simples]
        present_imperfects = ["می‌" + item for item in present_simples]
        present_not_imperfects = ["ن" + item for item in present_imperfects]
        present_subjunctives = [
            item if item.startswith("ب") else "ب" + item for item in present_simples
        ]
        present_not_subjunctives = ["ن" + item for item in present_simples]
        return (
            present_simples
            + present_not_simples
            + present_imperfects
            + present_not_imperfects
            + present_subjunctives
            + present_not_subjunctives
        )
