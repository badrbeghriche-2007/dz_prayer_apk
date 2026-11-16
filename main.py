import asyncio
import ctypes
from datetime import datetime, timedelta, timezone
import inspect
import json
import os
import ssl
import tempfile
import threading
import urllib.parse
import urllib.request
import flet as ft

# توقيت الجزائر الرسمي الدائم (UTC+1) يعمل على Windows و Android بدون مكتبات إضافية
DZ_TZ = timezone(timedelta(hours=1))

# توافق تام مع إصدارات Flet 0.28 و Flet 1.0+
Padding = getattr(ft, "Padding", getattr(ft, "padding", None))
Border = getattr(ft, "Border", getattr(ft, "border", None))
Alignment = getattr(ft, "Alignment", getattr(ft, "alignment", None))
TOP_LEFT = getattr(Alignment, "TOP_LEFT", getattr(Alignment, "top_left", None))
BOTTOM_RIGHT = getattr(Alignment, "BOTTOM_RIGHT", getattr(Alignment, "bottom_right", None))
CENTER = getattr(Alignment, "CENTER", getattr(Alignment, "center", None))
DropdownOption = getattr(
    ft, "DropdownOption", getattr(getattr(ft, "dropdown", None), "Option", None)
)


def http_get_json(url: str, params: dict = None, timeout: int = 12) -> dict:
    """جلب بيانات JSON باستخدام مكتبة Python المدمجة (urllib) للعمل على الأندرويد بدون requests."""
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Linux; Android 14) RafiqAlMuslim/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))


def http_get_bytes(url: str, timeout: int = 15) -> bytes:
    """تحميل ملفات الصوت باستخدام مكتبة Python المدمجة بدون الحاجة لمكتبة requests."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Linux; Android 14) RafiqAlMuslim/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read()


def make_dropdown(label: str, value: str, option_labels: list, callback):
    """إنشاء قائمة منسدلة متوافقة تلقائياً مع Flet 1.0 (on_select) و Flet 0.28 (on_change)."""
    sig_params = inspect.signature(ft.Dropdown.__init__).parameters
    opts = [DropdownOption(key=item, text=item) for item in option_labels]
    kwargs = {
        "label": label,
        "value": value,
        "options": opts,
        "color": "#FFFFFF",
        "border_color": "#D4AF37",
    }
    if "on_select" in sig_params:
        kwargs["on_select"] = callback
    elif "on_change" in sig_params:
        kwargs["on_change"] = callback

    if "fill_color" in sig_params:
        kwargs["filled"] = True
        kwargs["fill_color"] = "#0A2E1C"
    elif "bgcolor" in sig_params:
        kwargs["bgcolor"] = "#0A2E1C"

    if "width" in sig_params:
        kwargs["width"] = 390

    return ft.Dropdown(**kwargs)


ADHAN_AUDIO_URL = "https://cdn.aladhan.com/audio/adhans/a1.mp3"

# قائمة ولايات الجزائر الـ 58 (قسنطينة افتراضياً)
WILAYAS = {
    "25 - قسنطينة (Constantine)": "Constantine",
    "16 - الجزائر العاصمة (Algiers)": "Algiers",
    "43 - ميلة (Mila)": "Mila",
    "34 - برج بوعريريج (Bordj Bou Arreridj)": "Bordj Bou Arreridj",
    "31 - وهران (Oran)": "Oran",
    "19 - سطيف (Setif)": "Setif",
    "23 - عنابة (Annaba)": "Annaba",
    "01 - أدرار (Adrar)": "Adrar",
    "02 - الشلف (Chlef)": "Chlef",
    "03 - الأغواط (Laghouat)": "Laghouat",
    "04 - أم البواقي (Oum El Bouaghi)": "Oum El Bouaghi",
    "05 - باتنة (Batna)": "Batna",
    "06 - بجاية (Bejaia)": "Bejaia",
    "07 - بسكرة (Biskra)": "Biskra",
    "08 - بشار (Bechar)": "Bechar",
    "09 - البليدة (Blida)": "Blida",
    "10 - البويرة (Bouira)": "Bouira",
    "11 - تمنراست (Tamanrasset)": "Tamanrasset",
    "12 - تبسة (Tebessa)": "Tebessa",
    "13 - تلمسان (Tlemcen)": "Tlemcen",
    "14 - تيارت (Tiaret)": "Tiaret",
    "15 - تيزي وزو (Tizi Ouzou)": "Tizi Ouzou",
    "17 - الجلفة (Djelfa)": "Djelfa",
    "18 - جيجل (Jijel)": "Jijel",
    "20 - سعيدة (Saida)": "Saida",
    "21 - سكيكدة (Skikda)": "Skikda",
    "22 - سيدي بلعباس (Sidi Bel Abbes)": "Sidi Bel Abbes",
    "24 - قالمة (Guelma)": "Guelma",
    "26 - المدية (Medea)": "Medea",
    "27 - مستغانم (Mostaganem)": "Mostaganem",
    "28 - المسيلة (M'Sila)": "M'Sila",
    "29 - معسكر (Mascara)": "Mascara",
    "30 - ورقلة (Ouargla)": "Ouargla",
    "32 - البيض (El Bayadh)": "El Bayadh",
    "33 - إليزي (Illizi)": "Illizi",
    "35 - بومرداس (Boumerdes)": "Boumerdes",
    "36 - الطارف (El Tarf)": "El Tarf",
    "37 - تندوف (Tindouf)": "Tindouf",
    "38 - تيسمسيلت (Tissemsilt)": "Tissemsilt",
    "39 - الوادي (El Oued)": "El Oued",
    "40 - خنشلة (Khenchela)": "Khenchela",
    "41 - سوق أهراس (Souk Ahras)": "Souk Ahras",
    "42 - تيبازة (Tipaza)": "Tipaza",
    "44 - عين الدفلى (Ain Defla)": "Ain Defla",
    "45 - النعامة (Naama)": "Naama",
    "46 - عين تموشنت (Ain Temouchent)": "Ain Temouchent",
    "47 - غرداية (Ghardaia)": "Ghardaia",
    "48 - غليزان (Relizane)": "Relizane",
    "49 - تيميمون (Timimoun)": "Timimoun",
    "50 - برج باجي مختار (Bordj Badji Mokhtar)": "Bordj Badji Mokhtar",
    "51 - أولاد جلال (Ouled Djellal)": "Ouled Djellal",
    "52 - بني عباس (Beni Abbes)": "Beni Abbes",
    "53 - عين صالح (In Salah)": "In Salah",
    "54 - عين قزام (In Guezzam)": "In Guezzam",
    "55 - تقرت (Touggourt)": "Touggourt",
    "56 - جانت (Djanet)": "Djanet",
    "57 - المغير (El M'Ghair)": "El M'Ghair",
    "58 - المنيعة (El Meniaa)": "El Meniaa",
}

PRAYER_NAMES_AR = {
    "Fajr": ("الفجر", ft.Icons.WB_TWILIGHT),
    "Sunrise": ("الشروق", ft.Icons.WB_SUNNY_OUTLINED),
    "Dhuhr": ("الظهر", ft.Icons.LIGHT_MODE),
    "Asr": ("العصر", ft.Icons.WB_CLOUDY_OUTLINED),
    "Maghrib": ("المغرب", ft.Icons.NIGHTLIGHT_ROUND),
    "Isha": ("العشاء", ft.Icons.BEDTIME),
}

# موسوعة الأحاديث النبوية الشريفة
HADITH_COLLECTION = [
    {
        "title": "الحديث الأول: الأعمال بالنيات",
        "text": "عن أمير المؤمنين أبي حفص عمر بن الخطاب رضي الله عنه قال: سمعت رسول الله ﷺ يقول: «إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى، فمن كانت هجرته إلى الله ورسوله فهجرته إلى الله ورسوله، ومن كانت هجرته لدنيا يصيبها أو امرأة ينكحها فهجرته إلى ما هاجر إليه».",
        "source": "رواه البخاري ومسلم",
    },
    {
        "title": "الحديث الثاني: فضل الصلاة على وقتها",
        "text": "عن عبد الله بن مسعود رضي الله عنه قال: سألت النبي ﷺ: أي العمل أحب إلى الله؟ قال: «الصلاة على وقتها»، قال: ثم أي؟ قال: «ثم بر الوالدين»، قال: ثم أي؟ قال: «الجهاد في سبيل الله».",
        "source": "متفق عليه (البخاري ومسلم)",
    },
    {
        "title": "الحديث الثالث: فضل قراءة القرآن",
        "text": "عن عثمان بن عفان رضي الله عنه عن النبي ﷺ قال: «خيركم من تعلم القرآن وعلمه».",
        "source": "رواه البخاري",
    },
    {
        "title": "الحديث الرابع: الصلوات الخمس كفارة للخطايا",
        "text": "عن أبي هريرة رضي الله عنه أنه سمع رسول الله ﷺ يقول: «أرأيتم لو أن نهراً بباب أحدكم يغتسل فيه كل يوم خمس مرات، ما تقول ذلك يبقي من درنه؟» قالوا: لا يبقي من درنه شيئاً، قال: «فذلك مثل الصلوات الخمس، يمحو الله بهن الخطايا».",
        "source": "متفق عليه",
    },
    {
        "title": "الحديث الخامس: أركان الإسلام",
        "text": "عن ابن عمر رضي الله عنهما قال: قال رسول الله ﷺ: «بني الإسلام على خمس: شهادة أن لا إله إلا الله وأن محمداً رسول الله، وإقام الصلاة، وإيتاء الزكاة، والحج، وصوم رمضان».",
        "source": "رواه البخاري ومسلم",
    },
    {
        "title": "الحديث السادس: النصيحة في الدين",
        "text": "عن تميم الداري رضي الله عنه أن النبي ﷺ قال: «الدين النصيحة» قلنا: لمن؟ قال: «لله ولكتابه ولرسوله ولأئمة المسلمين وعامتهم».",
        "source": "رواه مسلم",
    },
    {
        "title": "الحديث السابع: من حسن إسلام المرء",
        "text": "عن أبي هريرة رضي الله عنه قال: قال رسول الله ﷺ: «من حسن إسلام المرء تركه ما لا يعنيه».",
        "source": "رواه الترمذي",
    },
    {
        "title": "الحديث الثامن: لا يؤمن أحدكم حتى يحب لأخيه",
        "text": "عن أنس بن مالك رضي الله عنه عن النبي ﷺ قال: «لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه».",
        "source": "رواه البخاري ومسلم",
    },
    {
        "title": "الحديث التاسع: الكلمة الطيبة والذكر",
        "text": "عن أبي مالك الأشعري رضي الله عنه قال: قال رسول الله ﷺ: «الطهور شطر الإيمان، والحمد لله تملأ الميزان، وسبحان الله والحمد لله تملآن ما بين السماوات والأرض، والصلاة نور، والصدقة برهان، والصبر ضياء، والقرآن حجة لك أو عليك».",
        "source": "رواه مسلم",
    },
    {
        "title": "الحديث العاشر: حفظ الله للعبد",
        "text": "عن ابن عباس رضي الله عنهما قال: كنت خلف رسول الله ﷺ يوماً فقال: «يا غلام إني أعلمك كلمات: احفظ الله يحفظك، احفظ الله تجده تجاهك، إذا سألت فاسأل الله، وإذا استعنت فاستعن بالله».",
        "source": "رواه الترمذي",
    },
]

# قائمة تسبيحات المسبحة الإلكترونية
TASBIH_PHRASES = [
    "سبحان الله",
    "الحمد لله",
    "الله أكبر",
    "لا إله إلا الله وحده لا شريك له",
    "سبحان الله وبحمده، سبحان الله العظيم",
    "أستغفر الله وأتوب إليه",
    "اللهم صلِّ وسلم على نبينا محمد",
    "لا حول ولا قوة إلا بالله",
]

# أذكار الصباح والمساء مع عدد التكرار والفضل
MORNING_ADHKAR = [
    {
        "title": "آية الكرسي",
        "text": "﴿اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ مَنْ ذَا الَّذِي يَشْفَعُ عِنْدَهُ إِلَّا بِإِذْنِهِ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ وَلَا يُحِيطُونَ بِشَيْءٍ مِنْ عِلْمِهِ إِلَّا بِمَا شَاءَ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ وَلَا يَئُودُهُ حِفْظُهُمَا وَهُوَ الْعَلِيُّ الْعَظِيمُ﴾",
        "count": 1,
        "virtue": "من قالها حين يصبح أجير من الجن حتى يمسي",
    },
    {
        "title": "سيد الاستغفار",
        "text": "«اللهم أنت ربي لا إله إلا أنت، خلقتني وأنا عبدك، وأنا على عهدك ووعدك ما استطعت، أعوذ بك من شر ما صنعت، أبوء لك بنعمتك عليّ، وأبوء بذنبي فاغفر لي فإنه لا يغفر الذنوب إلا أنت».",
        "count": 1,
        "virtue": "من قالها موقناً بها حين يصبح فمات من يومه دخل الجنة",
    },
    {
        "title": "أصبحنا وأصبح الملك لله",
        "text": "«أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير، ربِّ أسألك خير ما في هذا اليوم وخير ما بعده، وأعوذ بك من شر ما في هذا اليوم وشر ما بعده».",
        "count": 1,
        "virtue": "رواه مسلم",
    },
    {
        "title": "بسم الله الذي لا يضر مع اسمه شيء",
        "text": "«بسم الله الذي لا يضر مع اسمه شيء في الأرض ولا في السماء وهو السميع العليم».",
        "count": 3,
        "virtue": "لم يضره من الله شيء",
    },
    {
        "title": "رضيت بالله رباً",
        "text": "«رضيت بالله رباً، وبالإسلام ديناً، وبمحمد ﷺ نبياً ورسولاً».",
        "count": 3,
        "virtue": "كان حقاً على الله أن يرضيه يوم القيامة",
    },
    {
        "title": "يا حي يا قيوم برحمتك أستغيث",
        "text": "«يا حي يا قيوم برحمتك أستغيث، أصلح لي شأني كله، ولا تكلني إلى نفسي طرفة عين».",
        "count": 3,
        "virtue": "رواه الحاكم وصححه الألباني",
    },
    {
        "title": "حسبي الله لا إله إلا هو",
        "text": "«حسبي الله لا إله إلا هو عليه توكلت وهو رب العرش العظيم».",
        "count": 7,
        "virtue": "من قالها سبع مرات كفاه الله ما أهمه من أمر الدنيا والآخرة",
    },
]

EVENING_ADHKAR = [
    {
        "title": "آية الكرسي",
        "text": "﴿اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ مَنْ ذَا الَّذِي يَشْفَعُ عِنْدَهُ إِلَّا بِإِذْنِهِ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ وَلَا يُحِيطُونَ بِشَيْءٍ مِنْ عِلْمِهِ إِلَّا بِمَا شَاءَ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ وَلَا يَئُودُهُ حِفْظُهُمَا وَهُوَ الْعَلِيُّ الْعَظِيمُ﴾",
        "count": 1,
        "virtue": "من قالها حين يمسي أجير من الجن حتى يصبح",
    },
    {
        "title": "أمسينا وأمسى الملك لله",
        "text": "«أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير، ربِّ أسألك خير ما في هذه الليلة وخير ما بعدها، وأعوذ بك من شر ما في هذه الليلة وشر ما بعدها».",
        "count": 1,
        "virtue": "رواه مسلم",
    },
    {
        "title": "سيد الاستغفار في المساء",
        "text": "«اللهم أنت ربي لا إله إلا أنت، خلقتني وأنا عبدك، وأنا على عهدك ووعدك ما استطعت، أعوذ بك من شر ما صنعت، أبوء لك بنعمتك عليّ، وأبوء بذنبي فاغفر لي فإنه لا يغفر الذنوب إلا أنت».",
        "count": 1,
        "virtue": "من قالها موقناً بها حين يمسي فمات من ليلته دخل الجنة",
    },
    {
        "title": "أعوذ بكلمات الله التامات",
        "text": "«أعوذ بكلمات الله التامات من شر ما خلق».",
        "count": 3,
        "virtue": "لم تضره حُمَة تلك الليلة (رواه مسلم)",
    },
    {
        "title": "بسم الله الذي لا يضر مع اسمه شيء",
        "text": "«بسم الله الذي لا يضر مع اسمه شيء في الأرض ولا في السماء وهو السميع العليم».",
        "count": 3,
        "virtue": "لم يضره فجأة بلاء حتى يصبح",
    },
    {
        "title": "اللهم بك أمسينا وبك أصبحنا",
        "text": "«اللهم بك أمسينا، وبك أصبحنا، وبك نحيا، وبك نموت، وإليك المصير».",
        "count": 1,
        "virtue": "رواه الترمذي",
    },
    {
        "title": "حسبي الله لا إله إلا هو",
        "text": "«حسبي الله لا إله إلا هو عليه توكلت وهو رب العرش العظيم».",
        "count": 7,
        "virtue": "كفاه الله ما أهمه من أمر الدنيا والآخرة",
    },
]


class AudioController:
    """مشغل صوتيات مدمج لتشغيل الأذان وتلاوة القرآن على Windows و Android."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.is_playing = False
        self.temp_dir = tempfile.gettempdir()

    def play_url(self, url: str, tag: str = "islamic_audio"):
        if hasattr(ctypes, "windll"):
            def _worker():
                try:
                    self.stop()
                    local_file = os.path.join(self.temp_dir, f"{tag}.mp3")
                    if not os.path.exists(local_file) or tag != "adhan":
                        audio_bytes = http_get_bytes(url, timeout=15)
                        with open(local_file, "wb") as f:
                            f.write(audio_bytes)

                    try:
                        import winsound
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    except Exception:
                        pass
                    mci = ctypes.windll.winmm.mciSendStringW
                    mci("close islamic_player", None, 0, 0)
                    mci(
                        f'open "{local_file}" type mpegvideo alias islamic_player',
                        None,
                        0,
                        0,
                    )
                    mci("play islamic_player", None, 0, 0)
                    self.is_playing = True
                except Exception:
                    pass

            threading.Thread(target=_worker, daemon=True).start()
        else:
            # على هاتف الأندرويد: تشغيل ملف الصوت مباشرة عبر مشغل النظام أو UrlLauncher
            try:
                if hasattr(self.page, "launch_url"):
                    self.page.launch_url(url)
                elif hasattr(ft, "UrlLauncher"):
                    self.page.run_task(ft.UrlLauncher().launch_url, url)
            except Exception:
                pass

    def stop(self):
        try:
            if hasattr(ctypes, "windll"):
                mci = ctypes.windll.winmm.mciSendStringW
                mci("stop islamic_player", None, 0, 0)
                mci("close islamic_player", None, 0, 0)
            self.is_playing = False
        except Exception:
            pass


def fetch_prayer_times(city: str):
    url = "https://api.aladhan.com/v1/timingsByCity"
    params = {"city": city, "country": "Algeria", "method": 19}
    return http_get_json(url, params=params, timeout=10)["data"]


def get_next_prayer(timings: dict, now_dz: datetime):
    ordered_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    for key in ordered_keys:
        raw_time = timings[key].split(" ")[0]
        hour, minute = map(int, raw_time.split(":"))
        prayer_dt = now_dz.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if prayer_dt > now_dz:
            return key, prayer_dt

    raw_fajr = timings["Fajr"].split(" ")[0]
    hour, minute = map(int, raw_fajr.split(":"))
    tomorrow_fajr = (now_dz + timedelta(days=1)).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
    return "Fajr", tomorrow_fajr


def build_islamic_star(size: int, color: str = "#D4AF37", opacity: float = 0.12):
    """بناء نجمة إسلامية ثمانية هندسية (Rub el Hizb ۞) قابلة للدوران بالأنميشن."""
    sq1 = ft.Container(
        width=size,
        height=size,
        border=Border.all(1.8, ft.Colors.with_opacity(opacity, color)),
        border_radius=4,
    )
    sq2 = ft.Container(
        width=size,
        height=size,
        rotate=0.785398,  # 45 degrees in radians
        border=Border.all(1.8, ft.Colors.with_opacity(opacity, color)),
        border_radius=4,
    )
    inner_circle = ft.Container(
        width=size * 0.45,
        height=size * 0.45,
        border=Border.all(1.2, ft.Colors.with_opacity(opacity * 1.2, color)),
        border_radius=size,
    )
    return ft.Stack(
        width=size * 1.35,
        height=size * 1.35,
        alignment=CENTER,
        controls=[sq1, sq2, inner_circle],
    )


def main(page: ft.Page):
    page.title = "رفيق المسلم الجزائري - مواقيت، قرآن، أحاديث، أذكار"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#051F14"
    page.padding = 0
    page.window.width = 440
    page.window.height = 880

    audio_ctrl = AudioController(page)

    state = {
        "target_dt": None,
        "next_key": "Fajr",
        "running": True,
        "last_notified_minute": None,
        "hadith_index": 0,
        "hadiths": list(HADITH_COLLECTION),
        "rotation_step": 0.0,
        "pulse_toggle": False,
        "tasbih_count": 0,
        "tasbih_total": 0,
        "tasbih_target": 33,
        "tasbih_rotate": 0.0,
        "adhkar_mode": "morning",
    }

    # --- 1. طبقة الزخرفة الإسلامية المتحركة في الخلفية (Background Ornament Layer) ---
    star_top_right = ft.Container(
        content=build_islamic_star(170, "#D4AF37", 0.13),
        top=-45,
        right=-45,
        rotate=0.0,
        animate_rotation=2500,
    )
    star_top_left = ft.Container(
        content=build_islamic_star(130, "#D4AF37", 0.10),
        top=60,
        left=-40,
        rotate=0.0,
        animate_rotation=2500,
    )
    star_mid_right = ft.Container(
        content=build_islamic_star(220, "#20C997", 0.07),
        top=310,
        right=-75,
        rotate=0.0,
        animate_rotation=2500,
    )
    star_bottom_left = ft.Container(
        content=build_islamic_star(190, "#D4AF37", 0.12),
        bottom=-50,
        left=-50,
        rotate=0.0,
        animate_rotation=2500,
    )
    star_bottom_right = ft.Container(
        content=build_islamic_star(120, "#D4AF37", 0.10),
        bottom=90,
        right=-30,
        rotate=0.0,
        animate_rotation=2500,
    )

    ornament_watermark = ft.Container(
        alignment=CENTER,
        expand=True,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "۞  ﷽  ۞",
                    size=26,
                    color=ft.Colors.with_opacity(0.07, "#D4AF37"),
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "❁ ۞ ❁ ۞ ❁",
                    size=34,
                    color=ft.Colors.with_opacity(0.05, "#D4AF37"),
                ),
                ft.Text(
                    "۞  أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ  ۞",
                    size=22,
                    color=ft.Colors.with_opacity(0.06, "#D4AF37"),
                ),
            ],
        ),
    )

    # --- 2. إشعار الأذان المتحرك في أعلى الشاشة (Adhan Notification Banner) ---
    adhan_banner_title = ft.Text(
        "🕌 حان الآن موعد الأذان",
        size=16,
        weight=ft.FontWeight.BOLD,
        color="#051F14",
    )
    adhan_banner_sub = ft.Text(
        "حيّ على الصلاة.. حيّ على الفلاح",
        size=13,
        color="#0A3622",
        weight=ft.FontWeight.W_600,
    )

    def dismiss_adhan_alert(e=None):
        audio_ctrl.stop()
        adhan_alert_card.visible = False
        adhan_alert_card.scale = 0.9
        page.update()

    stop_adhan_btn = ft.Container(
        bgcolor="#051F14",
        padding=Padding.symmetric(horizontal=12, vertical=6),
        border_radius=20,
        on_click=dismiss_adhan_alert,
        content=ft.Text(
            "⏹️ إيقاف الأذان",
            size=12,
            color="#FFD43B",
            weight=ft.FontWeight.BOLD,
        ),
    )

    adhan_alert_card = ft.Container(
        visible=False,
        scale=0.95,
        animate_scale=350,
        animate_opacity=350,
        padding=14,
        border_radius=16,
        gradient=ft.LinearGradient(
            begin=TOP_LEFT,
            end=BOTTOM_RIGHT,
            colors=["#FFD43B", "#F59F00"],
        ),
        border=Border.all(2, "#FFF3BF"),
        shadow=ft.BoxShadow(
            blur_radius=18,
            color=ft.Colors.with_opacity(0.45, "#FFD43B"),
        ),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.NOTIFICATIONS_ACTIVE,
                            color="#051F14",
                            size=30,
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[adhan_banner_title, adhan_banner_sub],
                        ),
                    ],
                ),
                stop_adhan_btn,
            ],
        ),
    )

    def trigger_adhan_alert(prayer_name_ar: str):
        adhan_banner_title.value = f"🕌 حان الآن موعد أذان {prayer_name_ar}"
        adhan_banner_sub.value = "جاري رفع الأذان.. حيّ على الصلاة، حيّ على الفلاح"
        adhan_alert_card.visible = True
        adhan_alert_card.scale = 1.0
        audio_ctrl.play_url(ADHAN_AUDIO_URL, tag="adhan")
        page.update()

    # --- 3. الترويسة الإسلامية المزخرفة (Illuminated Header) ---
    header_emblem = ft.Container(
        scale=1.0,
        animate_scale=700,
        padding=8,
        border_radius=50,
        bgcolor=ft.Colors.with_opacity(0.15, "#FFD43B"),
        border=Border.all(1.5, "#D4AF37"),
        content=ft.Icon(ft.Icons.MOSQUE, color="#FFD43B", size=30),
    )

    date_text = ft.Text(
        "جاري تحميل التاريخ الهجري والميلادي...",
        size=12,
        color="#E9ECEF",
        text_align=ft.TextAlign.CENTER,
    )

    header_banner = ft.Container(
        width=float("inf"),
        padding=Padding.symmetric(horizontal=16, vertical=12),
        border_radius=20,
        gradient=ft.LinearGradient(
            begin=TOP_LEFT,
            end=BOTTOM_RIGHT,
            colors=["#0B3B24", "#145A38", "#0A2E1C"],
        ),
        border=Border.all(1.5, "#D4AF37"),
        shadow=ft.BoxShadow(
            blur_radius=16,
            color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
        ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Text(
                    "۞  بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ  ۞",
                    size=13,
                    color="#FFD43B",
                    weight=ft.FontWeight.BOLD,
                ),
                header_emblem,
                ft.Text(
                    "رفيق المسلم في الجزائر",
                    size=19,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                ),
                date_text,
            ],
        ),
    )

    # =========================================================================
    # التبويب 1: مواقيت الصلاة والأذان (Prayer Times & Adhan Tab)
    # =========================================================================
    next_prayer_label = ft.Text(
        "الصلاة القادمة",
        size=14,
        color="#FFD43B",
        weight=ft.FontWeight.W_600,
    )

    countdown_text = ft.Text(
        "--:--:--",
        size=30,
        color="#FFFFFF",
        weight=ft.FontWeight.BOLD,
    )

    countdown_card = ft.Container(
        width=float("inf"),
        padding=14,
        border_radius=16,
        scale=1.0,
        animate_scale=500,
        gradient=ft.LinearGradient(
            begin=TOP_LEFT,
            end=BOTTOM_RIGHT,
            colors=["#0F5132", "#08331E"],
        ),
        border=Border.all(1.8, "#D4AF37"),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                next_prayer_label,
                countdown_text,
                ft.Container(
                    margin=Padding.only(top=4) if hasattr(Padding, "only") else 4,
                    bgcolor=ft.Colors.with_opacity(0.2, "#FFD43B"),
                    border=Border.all(1, "#FFD43B"),
                    border_radius=20,
                    padding=Padding.symmetric(horizontal=14, vertical=6),
                    on_click=lambda e: trigger_adhan_alert(
                        PRAYER_NAMES_AR.get(state["next_key"], ("الصلاة", None))[0]
                    ),
                    content=ft.Row(
                        tight=True,
                        spacing=6,
                        controls=[
                            ft.Icon(
                                ft.Icons.VOLUME_UP, color="#FFD43B", size=18
                            ),
                            ft.Text(
                                "تجربة إشعار وصوت الأذان الآن",
                                size=12,
                                color="#FFD43B",
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    cards_column = ft.Column(spacing=8)

    def load_city_data(city_name: str):
        try:
            data = fetch_prayer_times(city_name)
            timings = data["timings"]
            hijri = data["date"]["hijri"]
            greg = data["date"]["gregorian"]

            date_text.value = (
                f"{hijri['weekday']['ar']} | {hijri['day']} {hijri['month']['ar']} "
                f"{hijri['year']} هـ • {greg['date']} م"
            )

            now_dz = datetime.now(DZ_TZ)
            next_key, next_dt = get_next_prayer(timings, now_dz)
            state["target_dt"] = next_dt
            state["next_key"] = next_key
            next_name_ar, _ = PRAYER_NAMES_AR[next_key]
            next_prayer_label.value = f"۞ الوقت المتبقي لأذان {next_name_ar} ۞"

            cards_column.controls.clear()
            for key, (name_ar, icon_name) in PRAYER_NAMES_AR.items():
                clean_time = timings[key].split(" ")[0]
                is_next = key == next_key

                card = ft.Container(
                    bgcolor="#145A38" if is_next else ft.Colors.with_opacity(0.88, "#0A2E1C"),
                    border_radius=14,
                    padding=Padding.symmetric(horizontal=16, vertical=12),
                    border=Border.all(
                        2 if is_next else 1,
                        "#FFD43B" if is_next else ft.Colors.with_opacity(0.35, "#D4AF37"),
                    ),
                    animate_scale=300,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Icon(
                                        icon_name,
                                        color="#FFD43B" if is_next else "#20C997",
                                        size=24,
                                    ),
                                    ft.Text(
                                        name_ar,
                                        size=17,
                                        weight=ft.FontWeight.BOLD,
                                        color="#FFFFFF",
                                    ),
                                    ft.Container(
                                        visible=is_next,
                                        bgcolor="#FFD43B",
                                        padding=Padding.symmetric(
                                            horizontal=8, vertical=2
                                        ),
                                        border_radius=20,
                                        content=ft.Text(
                                            "القادمة",
                                            size=11,
                                            weight=ft.FontWeight.BOLD,
                                            color="#051F14",
                                        ),
                                    ),
                                ],
                            ),
                            ft.Text(
                                clean_time,
                                size=19,
                                weight=ft.FontWeight.BOLD,
                                color="#FFD43B" if is_next else "#E9ECEF",
                            ),
                        ],
                    ),
                )
                cards_column.controls.append(card)

            page.update()
        except Exception as err:
            date_text.value = f"تعذر الاتصال بالخادم: {err}"
            page.update()

    wilaya_dropdown = make_dropdown(
        label="اختر الولاية",
        value="25 - قسنطينة (Constantine)",
        option_labels=list(WILAYAS.keys()),
        callback=lambda e: load_city_data(WILAYAS[wilaya_dropdown.value]),
    )

    prayers_view = ft.Column(
        spacing=10,
        controls=[wilaya_dropdown, countdown_card, cards_column],
    )

    # =========================================================================
    # التبويب 2: المصحف الشريف والقرآن الكريم (Holy Quran Tab)
    # =========================================================================
    surah_title_text = ft.Text(
        "۞ سورة الفاتحة ۞",
        size=19,
        weight=ft.FontWeight.BOLD,
        color="#FFD43B",
        text_align=ft.TextAlign.CENTER,
    )
    surah_verses_text = ft.Text(
        "جاري تحميل الآيات الكريمة...",
        size=18,
        color="#FFFFFF",
        text_align=ft.TextAlign.CENTER,
        selectable=True,
    )
    current_surah_num = {"num": 1}

    quran_card = ft.Container(
        width=float("inf"),
        padding=18,
        border_radius=18,
        opacity=1.0,
        animate_opacity=350,
        bgcolor=ft.Colors.with_opacity(0.92, "#082919"),
        border=Border.all(1.8, "#D4AF37"),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                surah_title_text,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Container(
                            bgcolor="#FFD43B",
                            padding=Padding.symmetric(horizontal=14, vertical=6),
                            border_radius=20,
                            on_click=lambda e: audio_ctrl.play_url(
                                f"https://cdn.islamic.network/quran/audio-surah/128/ar.alafasy/{current_surah_num['num']}.mp3",
                                tag=f"surah_{current_surah_num['num']}",
                            ),
                            content=ft.Row(
                                tight=True,
                                spacing=6,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.PLAY_CIRCLE_FILL,
                                        color="#051F14",
                                        size=18,
                                    ),
                                    ft.Text(
                                        "استماع للتلاوة",
                                        size=12,
                                        color="#051F14",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                        ),
                        ft.Container(
                            bgcolor="#0F5132",
                            border=Border.all(1, "#FFD43B"),
                            padding=Padding.symmetric(horizontal=12, vertical=6),
                            border_radius=20,
                            on_click=lambda e: audio_ctrl.stop(),
                            content=ft.Text(
                                "⏹️ إيقاف",
                                size=12,
                                color="#FFD43B",
                                weight=ft.FontWeight.BOLD,
                            ),
                        ),
                    ],
                ),
                ft.Divider(color=ft.Colors.with_opacity(0.3, "#D4AF37")),
                surah_verses_text,
            ],
        ),
    )

    def load_surah_content(surah_number: int):
        try:
            current_surah_num["num"] = surah_number
            quran_card.opacity = 0.3
            surah_verses_text.value = "جاري جلب الآيات الكريمة..."
            page.update()

            s_data = http_get_json(
                f"https://api.alquran.cloud/v1/surah/{surah_number}", timeout=12
            )["data"]

            surah_title_text.value = (
                f"۞ {s_data['name']} ({s_data['numberOfAyahs']} آية) ۞"
            )
            ayah_parts = []
            for ayah in s_data["ayahs"]:
                ayah_parts.append(f"{ayah['text']} ﴿{ayah['numberInSurah']}﴾")

            surah_verses_text.value = "  ".join(ayah_parts)
            quran_card.opacity = 1.0
            page.update()
        except Exception as err:
            surah_verses_text.value = f"تعذر تحميل السورة، تحقق من الإنترنت: {err}"
            quran_card.opacity = 1.0
            page.update()

    DEFAULT_SURAHS = [
        "1 - سورة الفاتحة",
        "2 - سورة البقرة",
        "18 - سورة الكهف",
        "36 - سورة يس",
        "55 - سورة الرحمن",
        "56 - سورة الواقعة",
        "67 - سورة الملك",
        "112 - سورة الإخلاص",
        "113 - سورة الفلق",
        "114 - سورة الناس",
    ]

    surah_dropdown = make_dropdown(
        label="اختر السورة الكريمة (114 سورة)",
        value="1 - سورة الفاتحة",
        option_labels=DEFAULT_SURAHS,
        callback=lambda e: load_surah_content(
            int(surah_dropdown.value.split(" - ")[0])
        ),
    )

    def load_all_surahs_list():
        try:
            all_s = http_get_json(
                "https://api.alquran.cloud/v1/surah", timeout=10
            )["data"]
            surah_dropdown.options = [
                DropdownOption(
                    key=f"{s['number']} - {s['name']}",
                    text=f"{s['number']} - {s['name']}",
                )
                for s in all_s
            ]
            surah_dropdown.value = "1 - سورة الفاتحة"
            page.update()
        except Exception:
            pass

    quran_view = ft.Column(
        visible=False,
        spacing=12,
        controls=[surah_dropdown, quran_card],
    )

    # =========================================================================
    # التبويب 3: الأحاديث النبوية الشريفة (Prophetic Hadiths Tab)
    # =========================================================================
    hadith_title = ft.Text(
        HADITH_COLLECTION[0]["title"],
        size=18,
        weight=ft.FontWeight.BOLD,
        color="#FFD43B",
        text_align=ft.TextAlign.CENTER,
    )
    hadith_body = ft.Text(
        HADITH_COLLECTION[0]["text"],
        size=18,
        color="#FFFFFF",
        text_align=ft.TextAlign.CENTER,
        selectable=True,
    )
    hadith_source = ft.Text(
        f"📚 {HADITH_COLLECTION[0]['source']}",
        size=13,
        color="#20C997",
        weight=ft.FontWeight.BOLD,
    )
    hadith_counter = ft.Text(
        f"1 / {len(HADITH_COLLECTION)}",
        size=13,
        color="#E9ECEF",
    )

    hadith_card = ft.Container(
        width=float("inf"),
        padding=20,
        border_radius=18,
        scale=1.0,
        opacity=1.0,
        animate_scale=300,
        animate_opacity=300,
        bgcolor=ft.Colors.with_opacity(0.92, "#082919"),
        border=Border.all(1.8, "#D4AF37"),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Text("۞ قول النبي ﷺ ۞", size=14, color="#D4AF37"),
                hadith_title,
                ft.Divider(color=ft.Colors.with_opacity(0.3, "#D4AF37")),
                hadith_body,
                hadith_source,
                hadith_counter,
            ],
        ),
    )

    def update_hadith_display(delta: int):
        total = len(state["hadiths"])
        state["hadith_index"] = (state["hadith_index"] + delta) % total
        item = state["hadiths"][state["hadith_index"]]

        hadith_card.scale = 0.95
        hadith_card.opacity = 0.4
        page.update()

        hadith_title.value = item["title"]
        hadith_body.value = item["text"]
        hadith_source.value = f"📚 {item['source']}"
        hadith_counter.value = f"{state['hadith_index'] + 1} / {total}"

        hadith_card.scale = 1.0
        hadith_card.opacity = 1.0
        page.update()

    def fetch_more_nawawi_hadiths():
        try:
            url = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-nawawi.min.json"
            items = http_get_json(url, timeout=10).get("hadiths", [])
            if items:
                loaded = []
                for h in items:
                    num = h.get("hadithnumber", "")
                    txt = h.get("text", "").strip()
                    if txt:
                        loaded.append(
                            {
                                "title": f"الحديث رقم {num} من الأربعين النووية",
                                "text": txt,
                                "source": "الأربعون النووية - الإمام النووي",
                            }
                        )
                if loaded:
                    state["hadiths"] = HADITH_COLLECTION + loaded
                    hadith_counter.value = (
                        f"{state['hadith_index'] + 1} / {len(state['hadiths'])}"
                    )
                    page.update()
        except Exception:
            pass

    hadith_nav_row = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        controls=[
            ft.Container(
                bgcolor="#0F5132",
                border=Border.all(1.5, "#D4AF37"),
                border_radius=14,
                padding=Padding.symmetric(horizontal=20, vertical=10),
                on_click=lambda e: update_hadith_display(-1),
                content=ft.Text(
                    "➡️ الحديث السابق",
                    size=14,
                    color="#FFD43B",
                    weight=ft.FontWeight.BOLD,
                ),
            ),
            ft.Container(
                bgcolor="#FFD43B",
                border_radius=14,
                padding=Padding.symmetric(horizontal=20, vertical=10),
                on_click=lambda e: update_hadith_display(1),
                content=ft.Text(
                    "الحديث التالي ⬅️",
                    size=14,
                    color="#051F14",
                    weight=ft.FontWeight.BOLD,
                ),
            ),
        ],
    )

    hadith_view = ft.Column(
        visible=False,
        spacing=14,
        controls=[hadith_card, hadith_nav_row],
    )

    # =========================================================================
    # التبويب 4: المسبحة الإلكترونية وأذكار الصباح والمساء (Tasbih & Adhkar Tab)
    # =========================================================================
    tasbih_count_text = ft.Text(
        "0",
        size=38,
        weight=ft.FontWeight.BOLD,
        color="#FFD43B",
    )
    tasbih_cycle_text = ft.Text(
        "الهدف: 0 / 33  •  المجموع الكلي: 0",
        size=13,
        color="#E9ECEF",
        weight=ft.FontWeight.W_600,
    )
    tasbih_status_badge = ft.Text(
        "اضغط على الدائرة الذهبية للتسبيح",
        size=12,
        color="#20C997",
    )

    tasbih_star_ring = ft.Container(
        content=build_islamic_star(125, "#FFD43B", 0.45),
        rotate=0.0,
        animate_rotation=350,
    )

    def on_tasbih_tap(e):
        state["tasbih_count"] += 1
        state["tasbih_total"] += 1
        state["tasbih_rotate"] += 0.3927  # 22.5 degrees per tap

        tasbih_star_ring.rotate = state["tasbih_rotate"]
        tasbih_circle_btn.scale = 0.92
        page.update()

        if state["tasbih_count"] > state["tasbih_target"]:
            state["tasbih_count"] = 1

        tasbih_count_text.value = str(state["tasbih_count"])
        tasbih_cycle_text.value = (
            f"الهدف: {state['tasbih_count']} / {state['tasbih_target']}  •  "
            f"المجموع الكلي: {state['tasbih_total']}"
        )

        if state["tasbih_count"] == state["tasbih_target"]:
            tasbih_status_badge.value = "✨ ما شاء الله! أتممت دورة تسبيح كاملة (33) ✨"
            tasbih_status_badge.color = "#FFD43B"
            if hasattr(ctypes, "windll"):
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_OK)
                except Exception:
                    pass
        else:
            tasbih_status_badge.value = f"الذكر الحالي: {tasbih_dropdown.value}"
            tasbih_status_badge.color = "#20C997"

        tasbih_circle_btn.scale = 1.0
        page.update()

    def reset_tasbih(e):
        state["tasbih_count"] = 0
        tasbih_count_text.value = "0"
        tasbih_cycle_text.value = (
            f"الهدف: 0 / {state['tasbih_target']}  •  "
            f"المجموع الكلي: {state['tasbih_total']}"
        )
        tasbih_status_badge.value = "تم تصفير عداد الدورة الحالية"
        tasbih_status_badge.color = "#E9ECEF"
        page.update()

    tasbih_circle_btn = ft.Container(
        width=136,
        height=136,
        border_radius=100,
        scale=1.0,
        animate_scale=150,
        alignment=CENTER,
        gradient=ft.LinearGradient(
            begin=TOP_LEFT,
            end=BOTTOM_RIGHT,
            colors=["#198754", "#0B3B24"],
        ),
        border=Border.all(3, "#FFD43B"),
        shadow=ft.BoxShadow(
            blur_radius=20,
            color=ft.Colors.with_opacity(0.4, "#FFD43B"),
        ),
        on_click=on_tasbih_tap,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                tasbih_count_text,
                ft.Text(
                    "سبّح",
                    size=13,
                    color="#FFFFFF",
                    weight=ft.FontWeight.BOLD,
                ),
            ],
        ),
    )

    tasbih_dropdown = make_dropdown(
        label="اختر صيغة التسبيح والذكر",
        value=TASBIH_PHRASES[0],
        option_labels=TASBIH_PHRASES,
        callback=lambda e: reset_tasbih(e),
    )

    tasbih_card = ft.Container(
        width=float("inf"),
        padding=18,
        border_radius=18,
        bgcolor=ft.Colors.with_opacity(0.92, "#082919"),
        border=Border.all(1.8, "#D4AF37"),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Text(
                    "📿 المسبحة الإلكترونية التفاعلية",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color="#FFD43B",
                ),
                tasbih_dropdown,
                ft.Stack(
                    width=175,
                    height=175,
                    alignment=CENTER,
                    controls=[tasbih_star_ring, tasbih_circle_btn],
                ),
                tasbih_cycle_text,
                tasbih_status_badge,
                ft.Container(
                    bgcolor="#0F5132",
                    border=Border.all(1, "#D4AF37"),
                    border_radius=20,
                    padding=Padding.symmetric(horizontal=16, vertical=6),
                    on_click=reset_tasbih,
                    content=ft.Text(
                        "🔄 تصفير العداد",
                        size=12,
                        color="#FFD43B",
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
            ],
        ),
    )

    # --- قسم أذكار الصباح والمساء مع عداد تفاعلي لكل ذكر ---
    adhkar_list_column = ft.Column(spacing=10)

    def build_adhkar_cards(mode: str):
        state["adhkar_mode"] = mode
        is_morning = mode == "morning"
        morning_tab_btn.bgcolor = "#FFD43B" if is_morning else "#0A2E1C"
        morning_tab_btn.content.color = "#051F14" if is_morning else "#FFD43B"
        evening_tab_btn.bgcolor = "#FFD43B" if not is_morning else "#0A2E1C"
        evening_tab_btn.content.color = "#051F14" if not is_morning else "#FFD43B"

        source_list = MORNING_ADHKAR if is_morning else EVENING_ADHKAR
        adhkar_list_column.controls.clear()

        for item in source_list:
            remaining = {"val": item["count"]}
            counter_btn_text = ft.Text(
                f"اضغط للقراءة ({remaining['val']} / {item['count']})",
                size=13,
                weight=ft.FontWeight.BOLD,
                color="#051F14",
            )
            counter_btn = ft.Container(
                bgcolor="#FFD43B",
                border_radius=20,
                padding=Padding.symmetric(horizontal=16, vertical=7),
                animate_scale=200,
                content=counter_btn_text,
            )
            card_container = ft.Container(
                width=float("inf"),
                padding=16,
                border_radius=16,
                animate_scale=250,
                bgcolor=ft.Colors.with_opacity(0.90, "#0A2E1C"),
                border=Border.all(1.4, ft.Colors.with_opacity(0.5, "#D4AF37")),
            )

            def make_tap_handler(rem_ref, total_cnt, btn_txt, btn_box, card_box):
                def _on_tap(e):
                    if rem_ref["val"] > 0:
                        rem_ref["val"] -= 1
                        card_box.scale = 0.98
                        page.update()
                        if rem_ref["val"] == 0:
                            btn_txt.value = "✅ تم إتمام هذا الذكر بحمد الله"
                            btn_txt.color = "#FFFFFF"
                            btn_box.bgcolor = "#198754"
                            card_box.border = Border.all(2, "#20C997")
                        else:
                            btn_txt.value = (
                                f"اضغط للقراءة (المتبقي: {rem_ref['val']} من {total_cnt})"
                            )
                        card_box.scale = 1.0
                        page.update()

                return _on_tap

            tap_fn = make_tap_handler(
                remaining, item["count"], counter_btn_text, counter_btn, card_container
            )
            counter_btn.on_click = tap_fn
            card_container.on_click = tap_fn

            card_container.content = ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Text(
                        f"۞ {item['title']} ۞",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#FFD43B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        item["text"],
                        size=16,
                        color="#FFFFFF",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"✨ {item['virtue']}",
                        size=12,
                        color="#20C997",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    counter_btn,
                ],
            )
            adhkar_list_column.controls.append(card_container)

        page.update()

    morning_tab_btn = ft.Container(
        expand=1,
        bgcolor="#FFD43B",
        border=Border.all(1.5, "#D4AF37"),
        border_radius=12,
        padding=Padding.symmetric(horizontal=10, vertical=10),
        alignment=CENTER,
        on_click=lambda e: build_adhkar_cards("morning"),
        content=ft.Text(
            "☀️ أذكار الصباح",
            size=14,
            weight=ft.FontWeight.BOLD,
            color="#051F14",
        ),
    )

    evening_tab_btn = ft.Container(
        expand=1,
        bgcolor="#0A2E1C",
        border=Border.all(1.5, "#D4AF37"),
        border_radius=12,
        padding=Padding.symmetric(horizontal=10, vertical=10),
        alignment=CENTER,
        on_click=lambda e: build_adhkar_cards("evening"),
        content=ft.Text(
            "🌙 أذكار المساء",
            size=14,
            weight=ft.FontWeight.BOLD,
            color="#FFD43B",
        ),
    )

    adhkar_view = ft.Column(
        visible=False,
        spacing=12,
        controls=[
            tasbih_card,
            ft.Row(spacing=8, controls=[morning_tab_btn, evening_tab_btn]),
            adhkar_list_column,
        ],
    )

    # =========================================================================
    # شريط التنقل بين الأقسام الأربعة (Animated 4-Tab Navigation Bar)
    # =========================================================================
    def switch_tab(tab_idx: int):
        prayers_view.visible = tab_idx == 0
        quran_view.visible = tab_idx == 1
        hadith_view.visible = tab_idx == 2
        adhkar_view.visible = tab_idx == 3

        for idx, btn in enumerate(nav_buttons):
            is_active = idx == tab_idx
            btn.bgcolor = "#FFD43B" if is_active else "#0A2E1C"
            btn.scale = 1.04 if is_active else 1.0
            btn.content.controls[0].color = "#051F14" if is_active else "#FFD43B"
            btn.content.controls[1].color = "#051F14" if is_active else "#FFFFFF"

        if tab_idx == 1 and surah_verses_text.value.startswith("جاري تحميل"):
            load_surah_content(1)
            threading.Thread(target=load_all_surahs_list, daemon=True).start()

        if tab_idx == 3 and len(adhkar_list_column.controls) == 0:
            build_adhkar_cards("morning")

        page.update()

    def make_nav_btn(idx: int, label: str, icon_name):
        is_first = idx == 0
        return ft.Container(
            expand=1,
            bgcolor="#FFD43B" if is_first else "#0A2E1C",
            border=Border.all(1.2, "#D4AF37"),
            border_radius=12,
            padding=Padding.symmetric(horizontal=4, vertical=8),
            scale=1.04 if is_first else 1.0,
            animate_scale=250,
            on_click=lambda e: switch_tab(idx),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                controls=[
                    ft.Icon(
                        icon_name,
                        color="#051F14" if is_first else "#FFD43B",
                        size=19,
                    ),
                    ft.Text(
                        label,
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color="#051F14" if is_first else "#FFFFFF",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

    nav_buttons = [
        make_nav_btn(0, "المواقيت", ft.Icons.ACCESS_TIME_FILLED),
        make_nav_btn(1, "القرآن", ft.Icons.MENU_BOOK),
        make_nav_btn(2, "الأحاديث", ft.Icons.AUTO_AWESOME),
        make_nav_btn(3, "الأذكار والمسبحة", ft.Icons.SPA),
    ]

    nav_bar = ft.Row(spacing=6, controls=nav_buttons)

    # حاوية المحتوى الرئيسية فوق طبقة الزخرفة الإسلامية
    foreground_scroll = ft.Container(
        expand=True,
        padding=14,
        content=ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=10,
            controls=[
                adhan_alert_card,
                header_banner,
                nav_bar,
                prayers_view,
                quran_view,
                hadith_view,
                adhkar_view,
            ],
        ),
    )

    page.add(
        ft.Stack(
            expand=True,
            controls=[
                # طبقة التدرج الخلفي الزمردي الإسلامي
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=TOP_LEFT,
                        end=BOTTOM_RIGHT,
                        colors=["#041B11", "#09301E", "#051F14"],
                    ),
                ),
                # طبقة الزخارف والنجوم الإسلامية المتحركة
                ornament_watermark,
                star_top_right,
                star_top_left,
                star_mid_right,
                star_bottom_left,
                star_bottom_right,
                # طبقة التطبيق التفاعلية
                foreground_scroll,
            ],
        )
    )

    # حلقة العد التنازلي والأنميشن المستمر وتنبيه الأذان التلقائي
    async def timer_and_animation_loop():
        tick = 0
        while state["running"]:
            if state["target_dt"] is not None:
                now_dz = datetime.now(DZ_TZ)
                diff = max(0, int((state["target_dt"] - now_dz).total_seconds()))
                hrs = diff // 3600
                mins = (diff % 3600) // 60
                secs = diff % 60
                countdown_text.value = f"{hrs:02d}:{mins:02d}:{secs:02d}"

                # إطلاق الأذان والإشعار تلقائياً عند وصول العد التنازلي إلى الصفر
                current_min_key = now_dz.strftime("%Y-%m-%d %H:%M")
                if (
                    diff == 0
                    and state["last_notified_minute"] != current_min_key
                ):
                    state["last_notified_minute"] = current_min_key
                    prayer_ar = PRAYER_NAMES_AR.get(
                        state["next_key"], ("الصلاة", None)
                    )[0]
                    trigger_adhan_alert(prayer_ar)
                    load_city_data(WILAYAS[wilaya_dropdown.value])

            # تحريك الزخرفة الإسلامية والنبض البصري كل بضع ثوانٍ
            tick += 1
            if tick % 3 == 0:
                state["rotation_step"] += 0.15
                star_top_right.rotate = state["rotation_step"]
                star_bottom_left.rotate = -state["rotation_step"]
                star_top_left.rotate = -state["rotation_step"] * 0.7
                star_mid_right.rotate = state["rotation_step"] * 0.5
                state["pulse_toggle"] = not state["pulse_toggle"]
                header_emblem.scale = 1.12 if state["pulse_toggle"] else 1.0

            page.update()
            await asyncio.sleep(1)

    load_city_data("Constantine")
    threading.Thread(target=fetch_more_nawawi_hadiths, daemon=True).start()
    page.run_task(timer_and_animation_loop)


if __name__ == "__main__":
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)
