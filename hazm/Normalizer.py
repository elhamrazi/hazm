# coding: utf-8

"""این ماژول شامل کلاس‌ها و توابعی برای نرمال‌سازی متن است.
"""

from __future__ import unicode_literals
import re
from .Lemmatizer import Lemmatizer
from .utils import maketrans, regex_replace


class Normalizer(object):
    """این کلاس شامل توابعی برای نرمال‌سازی متن است. 

    Args:
        remove_extra_spaces (bool, optional): اگر `True‍` باشد فواصل اضافهٔ متن را حذف می‌کند.
        remove_diacritics (bool, optional): اگر `True` باشد اعرابِ حروف را حذف می‌کند.
        remove_specials_chars (bool, optional): اگر `True` باشد برخی از کاراکترها و نشانه‌های خاص را که کاربردی در پردازش متن ندارند حذف می‌کند.
        decrease_repeated_chars (bool, optional): اگر `True` باشد تکرارهای بیش از ۲ بار را به ۲ بار کاهش می‌دهد. مثلاً «سلاممم» را به «سلامم» تبدیل می‌کند.
        affix_spacing (bool, optional): اگر `True` باشد فواصل را در پیشوندها و پسوندها اصلاح می‌کند.
        punctuation_spacing (bool, optional): اگر `True` باشد فواصل را در نشانه‌های سجاوندی اصلاح می‌کند.
        persian_style (bool, optional): اگر `True` باشد اصلاحات مخصوص زبان فارسی را انجام می‌دهد؛ مثلاً جایگزین‌کردن کوتیشن با گیومه.
        persian_numbers (bool, optional): اگر `True` باشد ارقام انگلیسی را با فارسی جایگزین می‌کند.
        unicodes_replacement (bool, optional): اگر `True` باشد برخی از کاراکترهای یونیکد را با معادل نرمال‌شدهٔ آن جایگزین می‌کند.
        seperate_mi (bool, optional): اگر `True` باشد پیشوند «می» و «نمی» را در افعال جدا می‌کند.
    """

    def __init__(self, remove_extra_spaces=True, remove_diacritics=True, remove_specials_chars=True, decrease_repeated_chars=True, affix_spacing=True, punctuation_spacing=True, persian_style=True, persian_numbers=True, unicodes_replacement=True, seperate_mi=True):
        self._remove_extra_spaces = remove_extra_spaces
        self._remove_diacritics = remove_diacritics
        self._remove_specials_chars = remove_specials_chars
        self._decrease_repeated_chars = decrease_repeated_chars
        self._affix_spacing = affix_spacing
        self._punctuation_spacing = punctuation_spacing
        self._persian_style = persian_style
        self._persian_number = persian_numbers
        self._unicodes_replacement = unicodes_replacement
        self._seperate_mi = seperate_mi

        self.translation_src = 'ؠػػؽؾؿكيٮٯٷٸٹٺٻټٽٿڀځٵٶٷٸٹٺٻټٽٿڀځڂڅڇڈډڊڋڌڍڎڏڐڑڒړڔڕږڗڙښڛڜڝڞڟڠڡڢڣڤڥڦڧڨڪګڬڭڮڰڱڲڳڴڵڶڷڸڹںڻڼڽھڿہۂۃۄۅۆۇۈۉۊۋۏۍێېۑےۓەۮۯۺۻۼۿݐݑݒݓݔݕݖݗݘݙݚݛݜݝݞݟݠݡݢݣݤݥݦݧݨݩݪݫݬݭݮݯݰݱݲݳݴݵݶݷݸݹݺݻݼݽݾݿࢠࢡࢢࢣࢤࢥࢦࢧࢨࢩࢪࢫࢮࢯࢰࢱࢬࢲࢳࢴࢶࢷࢸࢹࢺࢻࢼࢽﭐﭑﭒﭓﭔﭕﭖﭗﭘﭙﭚﭛﭜﭝﭞﭟﭠﭡﭢﭣﭤﭥﭦﭧﭨﭩﭮﭯﭰﭱﭲﭳﭴﭵﭶﭷﭸﭹﭺﭻﭼﭽﭾﭿﮀﮁﮂﮃﮄﮅﮆﮇﮈﮉﮊﮋﮌﮍﮎﮏﮐﮑﮒﮓﮔﮕﮖﮗﮘﮙﮚﮛﮜﮝﮞﮟﮠﮡﮢﮣﮤﮥﮦﮧﮨﮩﮪﮫﮬﮭﮮﮯﮰﮱﺀﺁﺃﺄﺅﺆﺇﺈﺉﺊﺋﺌﺍﺎﺏﺐﺑﺒﺕﺖﺗﺘﺙﺚﺛﺜﺝﺞﺟﺠﺡﺢﺣﺤﺥﺦﺧﺨﺩﺪﺫﺬﺭﺮﺯﺰﺱﺲﺳﺴﺵﺶﺷﺸﺹﺺﺻﺼﺽﺾﺿﻀﻁﻂﻃﻄﻅﻆﻇﻈﻉﻊﻋﻌﻍﻎﻏﻐﻑﻒﻓﻔﻕﻖﻗﻘﻙﻚﻛﻜﻝﻞﻟﻠﻡﻢﻣﻤﻥﻦﻧﻨﻩﻪﻫﻬﻭﻮﻯﻰﻱﻲﻳﻴىكي“” '
        self.translation_dst = 'یککیییکیبقویتتبتتتبحاوویتتبتتتبحححچدددددددددررررررررسسسصصطعففففففققکککککگگگگگللللنننننهچهههوووووووووییییییهدرشضغهبببببببححددرسعععففکککممنننلررسححسرحاایییووییحسسکببجطفقلمییرودصگویزعکبپتریفقنااببببپپپپببببتتتتتتتتتتتتففففححححححححچچچچچچچچددددددددژژررککککگگگگگگگگگگگگننننننههههههههههییییءاااووااییییااببببتتتتثثثثججججححححخخخخددذذررززسسسسششششصصصصضضضضططططظظظظععععغغغغففففققققککککللللممممننننههههوویییییییکی"" '

        if self._persian_number:
            self.number_translation_src = '0123456789%٠١٢٣٤٥٦٧٨٩'
            self.number_translation_dst = '۰۱۲۳۴۵۶۷۸۹٪۰۱۲۳۴۵۶۷۸۹'

        if self._remove_extra_spaces:
            self.extra_space_patterns = [
                (r' {2,}', ' '),  # remove extra spaces
                (r'\n{3,}', '\n\n'),  # remove extra newlines
                (r'\u200c{2,}', '\u200c'),  # remove extra ZWNJs
                (r'\u200c{1,} ', ' '),  # remove unneded ZWNJs before space
                (r' \u200c{1,}', ' '),  # remove unneded ZWNJs after space
                (r'[ـ\r]', ''),  # remove keshide, carriage returns
            ]

        if self._persian_style:
            self.persian_style_patterns = [
                ('"([^\n"]+)"', r'«\1»'),  # replace quotation with gyoome
                ('([\d+])\.([\d+])', r'\1٫\2'),  # replace dot with momayez
                (r' ?\.\.\.', ' …'),  # replace 3 dots
            ]

        if self._decrease_repeated_chars:
            self.repeated_chars_patterns = [
                (r'([آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی])\1{2,}', r'\1\1')
            ]

        if self._remove_diacritics:
            self.diacritics_patterns = [
                # remove FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SHADDA, SUKUN
                ('[\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652]', ''),
            ]

        if self._remove_specials_chars:
            self.specials_chars_patterns = [
                # Remove almoast all arabic unicode superscript and subscript characters in the ranges of 00600-06FF, 08A0-08FF, FB50-FDFF, and FE70-FEFF
                ('[\u0605\u0653\u0654\u0655\u0656\u0657\u0658\u0659\u065A\u065B\u065C\u065D\u065E\u065F\u0670\u0610\u0611\u0612\u0613\u0614\u0615\u0616\u0618\u0619\u061A\u061E\u06D4\u06D6\u06D7\u06D8\u06D9\u06DA\u06DB\u06DC\u06DD\u06DE\u06DF\u06E0\u06E1\u06E2\u06E3\u06E4\u06E5\u06E6\u06E7\u06E8\u06E9\u06EA\u06EB\u06EC\u06ED\u06FD\u06FE\u08AD\u08D4\u08D5\u08D6\u08D7\u08D8\u08D9\u08DA\u08DB\u08DC\u08DD\u08DE\u08DF\u08E0\u08E1\u08E2\u08E3\u08E4\u08E5\u08E6\u08E7\u08E8\u08E9\u08EA\u08EB\u08EC\u08ED\u08EE\u08EF\u08F0\u08F1\u08F2\u08F3\u08F4\u08F5\u08F6\u08F7\u08F8\u08F9\u08FA\u08FB\u08FC\u08FD\u08FE\u08FF\uFBB2\uFBB3\uFBB4\uFBB5\uFBB6\uFBB7\uFBB8\uFBB9\uFBBA\uFBBB\uFBBC\uFBBD\uFBBE\uFBBF\uFBC0\uFBC1\uFC5E\uFC5F\uFC60\uFC61\uFC62\uFC63\uFCF2\uFCF3\uFCF4\uFD3E\uFD3F\uFE70\uFE71\uFE72\uFE76\uFE77\uFE78\uFE79\uFE7A\uFE7B\uFE7C\uFE7D\uFE7E\uFE7F\uFDFA\uFDFB]', ''),
            ]

        if self._affix_spacing or self._punctuation_spacing:
            punc_after, punc_before = r'\.:!،؛؟»\]\)\}', r'«\[\(\{'

        if self._punctuation_spacing:
            self.punctuation_spacing_patterns = [
                # remove space before and after quotation
                ('" ([^\n"]+) "', r'"\1"'),
                (' ([' + punc_after + '])', r'\1'),  # remove space before
                ('([' + punc_before + ']) ', r'\1'),  # remove space after
                # put space after . and :
                ('([' + punc_after[:3] + '])([^ ' + \
                 punc_after + '\d۰۱۲۳۴۵۶۷۸۹])', r'\1 \2'),
                ('([' + punc_after[3:] + '])([^ ' + punc_after + '])',
                 r'\1 \2'),  # put space after
                ('([^ ' + punc_before + '])([' + punc_before + '])',
                 r'\1 \2'),  # put space before
                # put space after number; e.g., به طول ۹متر -> به طول ۹ متر
                ('(\d)([آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی])', r'\1 \2'),
                # put space after number; e.g., به طول۹ -> به طول ۹
                ('([آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی])(\d)', r'\1 \2'),
            ]

        if self._affix_spacing:
            self.affix_spacing_patterns = [
                (r'([^ ]ه) ی ', r'\1‌ی '),  # fix ی space
                (r'(^| )(ن?می) ', r'\1\2‌'),  # put zwnj after می, نمی
                # put zwnj before تر, تری, ترین, گر, گری, ها, های
                (r'(?<=[^\n\d ' + punc_after + punc_before + \
                 ']{2}) (تر(ین?)?|گری?|های?)(?=[ \n' + punc_after + punc_before + ']|$)', r'‌\1'),
                # join ام, ایم, اش, اند, ای, اید, ات
                (r'([^ ]ه) (ا(م|یم|ش|ند|ی|ید|ت))(?=[ \n' + \
                 punc_after + ']|$)', r'\1‌\2'),

                # شنبهها => شنبه‌ها
                ('(ه)(ها)', r'\1‌\2')
            ]

        if self._seperate_mi:
            self.verbs = Lemmatizer().verbs
            self.joint_mi_patterns = r'ن?می[آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی]+'

        if self._unicodes_replacement:
            self.replacements = [
                ('﷽', 'بسم الله الرحمن الرحیم'),
                ('﷼', 'ریال'),
                ('(ﷰ|ﷹ)', 'صلی'),
                ('ﷲ', 'الله'),
                ('ﷳ', 'اکبر'),
                ('ﷴ', 'محمد'),
                ('ﷵ', 'صلعم'),
                ('ﷶ', 'رسول'),
                ('ﷷ', 'علیه'),
                ('ﷸ', 'وسلم'),
                ('ﻵ|ﻶ|ﻷ|ﻸ|ﻹ|ﻺ|ﻻ|ﻼ', 'لا'),
            ]

    def normalize(self, text):
        """متن را نرمال‌سازی می‌کند.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.normalize('اِعلام کَرد : « زمین لرزه ای به بُزرگیِ 6 دهم ریشتر ...»')
            'اعلام کرد: «زمین‌لرزه‌ای به بزرگی ۶ دهم ریشتر…»'

        Args:
            text (str): متنی که باید نرمال‌سازی شود.

        Returns:
            (str): متنِ نرمال‌سازی‌شده.
        """

        translations = maketrans(
            self.translation_src, self.translation_dst)
        text = text.translate(translations)

        if self._remove_extra_spaces:
            text = self.remove_extra_spaces(text)

        if self._persian_style:
            text = self.persian_style(text)

        if self._persian_number:
            text = self.persian_number(text)

        if self._remove_diacritics:
            text = self.remove_diacritics(text)

        if self._affix_spacing:
            text = self.affix_spacing(text)

        if self._punctuation_spacing:
            text = self.punctuation_spacing(text)

        if self._unicodes_replacement:
            text = self.unicodes_replacement(text)

        if self._remove_specials_chars:
            text = self.remove_specials_chars(text)

        if self._decrease_repeated_chars:
            text = self.decrease_repeated_chars(text)

        if self._seperate_mi:
            text = self.seperate_mi(text)

        return text

    def remove_extra_spaces(self, text):
        """فواصل اضافه را حذف و کشــــــــیدگی حروف را برطرف می‌کند.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.remove_extra_spaces('ســـــلام     به همه')
            'سلام به همه'

        Args:
            text (str): متنی که باید فواصل اضافه و کشیدگی حروف در آن برطرف شود.

        Returns:
            (str): متنی بدون فواصل اضافه و بدون کشیدگی حروف.
        """
        return regex_replace(self.extra_space_patterns, text)
    
    def remove_diacritics(self, text):
        """اِعراب را از متن حذف می‌کند.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.remove_diacritics('حَذفِ اِعراب')
            'حذف اعراب'

        Args:
            text (str): متنی که باید اعراب آن حذف شود.

        Returns:
            (str): متنی بدون اعراب.
        """
        return regex_replace(self.diacritics_patterns, text)

    def remove_specials_chars(self, text):
        """برخی از کاراکترها و نشانه‌های خاص را که کاربردی در پردازش متن ندارند حذف می‌کند.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.remove_specials_chars('پیامبر اکرم ﷺ')
            'پیامبر اکرم'
        Args:
            text (str): متنی که باید کاراکترها و نشانه‌های اضافهٔ آن حذف شود.

        Returns:
            (str): متنی بدون کاراکترها و نشانه‌های اضافه.
        """
        return regex_replace(self.specials_chars_patterns, text)

    def decrease_repeated_chars(self, text):
        """تکرارهای زائد حروف فارسی را به دو تکرار کاهش می‌دهد. حالا چرا فقط دو تکرار؟ 
        چون تشخیصِ تکرارهای زائد کار دشواری است و به  معنا و ساختار جمله گره خورده است؛ 
        به عنوان مثال در جملهٔ «سلامم دوستان»، تکرار در واژهٔ سلام غیرضروری است 
        ولی در جملهٔ «سلامم را برسان» خیر! بنابراین فعلاً به کاهش تکرارها به دو تکرار بسنده کرده‌ایم. 
        در این حالت لااقل مطمئن هستیم که آسیبی به معنای متن نمی‌رسد.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.decrease_repeated_chars('سلامممم سلامممممم سلامم')
            'سلامم سلامم سلامم'
        Args:
            text (str): متنی که باید تکرارهای اضافهٔ حروف آن کاهش یابد.

        Returns:
            (str): متنی با حداقل تکرار حروف.
        """
        return regex_replace(self.repeated_chars_patterns, text)

    def affix_spacing(self, text):
        """فاصله‌گذاری‌های اشتباه را در پسوندها و پیشوندها اصلاح می‌کند.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.affix_spacing('خانه ی پدری')
            'خانه‌ی پدری'

            >>> normalizer.affix_spacing('فاصله میان پیشوند ها و پسوند ها را اصلاح می کند.')
            'فاصله میان پیشوند‌ها و پسوند‌ها را اصلاح می‌کند.'

            >>> normalizer.affix_spacing('می روم')
            'می‌روم'

            >>> normalizer.affix_spacing('حرفه ای')
            'حرفه‌ای'

            >>> normalizer.affix_spacing('محبوب ترین ها')
            'محبوب‌ترین‌ها'

        Args:
            text (str): متنی که باید فاصله‌گذاری‌های اشتباهِ آن در پسوندها و پیشوندها اصلاح شود.

        Returns:
            (str): متنی با فاصله‌گذاری صحیحِ پیشوندها و پسوندها.
        """
        return regex_replace(self.affix_spacing_patterns, text)

    def punctuation_spacing(self, text):
        """فاصله‌گذاری‌های اشتباه را در نشانه‌های سجاوندی اصلاح می‌کند. 

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.punctuation_spacing('اصلاح ( پرانتزها ) در متن .')
            'اصلاح (پرانتزها) در متن.'

            >>> normalizer.punctuation_spacing('نسخه 0.5 در ساعت 22:00 تهران،1396')
            'نسخه 0.5 در ساعت 22:00 تهران، 1396'

            >>> normalizer.punctuation_spacing('اتریش ۷.۹ میلیون.')
            'اتریش ۷.۹ میلیون.'

        Args:
            text (str): متنی که باید فاصله‌گذاری‌های اشتباه آن در نشانه‌های سجاوندی اصلاح شود.

        Returns:
            (str): متنی با فاصله‌گذاری صحیحِ‌ نشانه‌های سجاوندی.
        """
        return regex_replace(self.punctuation_spacing_patterns, text)

    def persian_style(self, text):
        """برخی از حروف و نشانه‌ها را با حروف و نشانه‌های فارسی جایگزین می‌کند.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.persian_style('"نرمال‌سازی"')
            '«نرمال‌سازی»'

        Args:
            text (str): متنی که باید حروف و نشانه‌های آن با حروف و نشانه‌های فارسی جایگزین شود.

        Returns:
            (str): متنی با حروف و نشانه‌های فارسی‌سازی شده.
        """
        return regex_replace(self.persian_style_patterns, text)

    def persian_number(self, text):
        """اعداد لاتین و علامت % را با معادل فارسی آن جایگزین می‌کند

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.persian_number('5% رشد داشته است.')
            '۵٪ رشد داشته است.'

        Args:
            text (str): متنی که باید اعداد لاتین و علامت % آن با معادل فارسی جایگزین شود.

        Returns:
            (str): متنی با اعداد و علامت ٪ فارسی.
        """
        translations = maketrans(
            self.number_translation_src, self.number_translation_dst)
        return text.translate(translations)
    

    def unicodes_replacement(self, text):
        """برخی از کاراکترهای خاص یونیکد را با معادلِ نرمال آن جایگزین می‌کند. غالباً این کار فقط در مواردی صورت می‌گیرد که یک کلمه در قالب یک کاراکتر یونیکد تعریف شده است.

        **فهرست این کاراکترها و نسخهٔ جایگزین آن:**

        |کاراکتر|نسخهٔ جایگزین|
        |--------|------------------|
        |﷽|بسم الله الرحمن الرحیم|
        |﷼|ریال|
        |ﷰ، ﷹ|صلی|
        |ﷲ|الله|
        |ﷳ|اکبر|
        |ﷴ|محمد|
        |ﷵ|صلعم|
        |ﷶ|رسول|
        |ﷷ|علیه|
        |ﷸ|وسلم|
        |ﻵ، ﻶ، ﻷ، ﻸ، ﻹ، ﻺ، ﻻ، ﻼ|لا|

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.unicodes_replacement('حضرت ﷴ صلوات الله علیه)')
            'حضرت محمد صلوات الله علیه'

        Args:
            text (str): متنی که باید برخی از کاراکترهای یونیکد آن (جدول بالا)، با شکل استاندارد، جایگزین شود.

        Returns:
            (str): متنی که برخی از کاراکترهای یونیکد آن با شکل استاندارد جایگزین شده است.
        """

        for old, new in self.replacements:
            text = re.sub(old, new, text)

        return text    

    def seperate_mi(self, text):
        """پیشوند «می» و «نمی» را در افعال جدا کرده و با نیم‌فاصله می‌چسباند.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.seperate_mi('نمیدانم چه میگفت')
            'نمی‌دانم چه می‌گفت'
        Args:
            text (str): متنی که باید پیشوند «می» و «نمی» در آن جدا شود.

        Returns:
            (str): متنی با «می» و «نمی» جدا شده.
        """
        matches = re.findall(self.joint_mi_patterns, text)
        for m in matches:
            r = re.sub("^(ن?می)", r'\1‌', m)
            if r in self.verbs:
                text = text.replace(m, r)

        return text
