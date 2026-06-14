from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Depends
from psycopg2.extras import RealDictCursor
import psycopg2
from datetime import datetime, date, timezone, timedelta
import os, uuid, json
import httpx
from pydantic import BaseModel

YOLO_URL = f"http://{os.getenv('YOLO_HOST','127.0.0.1')}:{os.getenv('YOLO_PORT','8002')}"
PHOTOS_BASE_URL = os.getenv("PHOTOS_BASE_URL", "https://birds.garden/photos")

import anthropic
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

analyzer = Analyzer()

# ── Biology + story context ────────────────────────────────────────────────

BIRD_BIO = {
    'Eurasian Blackbird': {
        'pl': 'Kos', 'sci': 'Turdus merula',
        'diet_pl': 'dżdżownice, jagody, owady',
        'breeding_pl': 'marzec–lipiec',
        'diet_en': 'earthworms, berries, insects',
        'breeding_en': 'March–July',
        'unique_pl': 'śpiewa jako pierwszy ptak o świcie; samiec ma jaskrawożółty dziób; alarm call ostrzega wszystkie ptaki w okolicy; chodzi po ziemi i dosłownie nasłuchuje dżdżownic pod powierzchnią',
        'unique_en': 'first bird to sing at dawn; male has bright yellow beak; alarm call warns all nearby birds; walks on ground and literally listens for earthworms underground',
    },
    'Common Starling': {
        'pl': 'Szpak', 'sci': 'Sturnus vulgaris',
        'diet_pl': 'owady, dżdżownice, owoce',
        'breeding_pl': 'kwiecień–czerwiec',
        'diet_en': 'insects, earthworms, fruit',
        'breeding_en': 'April–June',
        'unique_pl': 'jeden z najlepszych mimów ptasiego świata — potrafi naśladować inne gatunki, telefony i samochody; upierzenie połyskuje metalicznie zielono-fioletowo w słońcu; tworzy murmuracje liczące miliony osobników',
        'unique_en': 'one of the best avian mimics — can imitate other birds, phones and cars; plumage shimmers metallic green-purple in sunlight; forms murmurations of millions',
    },
    'Great Tit': {
        'pl': 'Sikora bogatka', 'sci': 'Parus major',
        'diet_pl': 'owady, nasiona, orzechy',
        'breeding_pl': 'kwiecień–czerwiec',
        'diet_en': 'insects, seeds, nuts',
        'breeding_en': 'April–June',
        'unique_pl': 'najagresywniejsza sikora w Europie; zimą chowa setki nasion i pamięta każdy schowek; ma kilkadziesiąt wariacji śpiewu; historycznie otwierała butelki mleka dziobem',
        'unique_en': 'most aggressive tit in Europe; caches hundreds of seeds and remembers every hiding spot; has dozens of song variations; historically opened milk bottles with its beak',
    },
    'Blue Tit': {
        'pl': 'Sikora modra', 'sci': 'Cyanistes caeruleus',
        'diet_pl': 'owady, nasiona, orzechy',
        'breeding_pl': 'kwiecień–czerwiec',
        'diet_en': 'insects, seeds, nuts',
        'breeding_en': 'April–June',
        'unique_pl': 'akrobata — zwisa głową w dół szukając owadów pod liśćmi; niebieska czapeczka odbija UV niewidoczne dla ludzi; zostaje z tobą przez cały rok, nie migruje',
        'unique_en': 'acrobat — hangs upside-down hunting insects under leaves; blue cap reflects UV invisible to humans; stays with you all year, does not migrate',
    },
    'European Robin': {
        'pl': 'Rudzik', 'sci': 'Erithacus rubecula',
        'diet_pl': 'owady, dżdżownice, jagody',
        'breeding_pl': 'marzec–lipiec',
        'diet_en': 'insects, earthworms, berries',
        'breeding_en': 'March–July',
        'unique_pl': 'chodzi za ogrodnikami kopiącymi ziemię i czeka na odsłonięte dżdżownice; śpiewa nocą pod latarniami; walczy z własnym odbiciem w lustrze; czerwona pierś to groźba dla rywali',
        'unique_en': 'follows gardeners digging soil and waits for exposed earthworms; sings at night under street lights; fights its own reflection; red breast is a threat display to rivals',
    },
    'House Sparrow': {
        'pl': 'Wróbel', 'sci': 'Passer domesticus',
        'diet_pl': 'nasiona, owady, resztki',
        'breeding_pl': 'kwiecień–sierpień',
        'diet_en': 'seeds, insects, scraps',
        'breeding_en': 'April–August',
        'unique_pl': 'kąpie się w piasku, nie w wodzie; jest z ludźmi od 10 000 lat — przyszedł z pierwszymi rolnikami; wróble w mieście szczebiotają inaczej niż wiejskie — adaptują pieśń do hałasu otoczenia',
        'unique_en': 'bathes in dust not water; has been with humans for 10,000 years since first farmers; urban sparrows chirp differently than rural ones — they adapt their song to ambient noise',
    },
    'Common Chaffinch': {
        'pl': 'Zięba', 'sci': 'Fringilla coelebs',
        'diet_pl': 'nasiona, owady',
        'breeding_pl': 'kwiecień–czerwiec',
        'diet_en': 'seeds, insects',
        'breeding_en': 'April–June',
        'unique_pl': 'samiec to jeden z najbarwniejszych ptaków ogrodu — różowy brzuch, niebieskawa głowa; śpiew ma regionalne dialekty jak ludzkie gwary; zimą przybywają do nas ziębice ze Skandynawii',
        'unique_en': 'male is one of the most colourful garden birds — pink breast, bluish head; song has regional dialects like human accents; female chaffinches from Scandinavia visit in winter',
    },
    'European Greenfinch': {
        'pl': 'Dzwoniec', 'sci': 'Chloris chloris',
        'diet_pl': 'nasiona, jagody',
        'breeding_pl': 'kwiecień–sierpień',
        'diet_en': 'seeds, berries',
        'breeding_en': 'April–August',
        'unique_pl': 'uwielbia nasiona słonecznika — może opróżnić karmnik w jeden ranek; populacja maleje przez epidemię trichomonezy; melodyjne "driu-driu" z czubka drzewa — to on',
        'unique_en': 'loves sunflower seeds — can empty a feeder in one morning; population declining due to trichomonosis; melodic "driu-driu" from tree top — that is this bird',
    },
    'Song Thrush': {
        'pl': 'Drozd śpiewak', 'sci': 'Turdus philomelos',
        'diet_pl': 'ślimaki, dżdżownice, jagody',
        'breeding_pl': 'marzec–lipiec',
        'diet_en': 'snails, earthworms, berries',
        'breeding_en': 'March–July',
        'unique_pl': 'jedyny ptak który tłucze ślimaki o kamień — ma swój ulubiony kamień "kowadełko"; powtarza każdą frazę śpiewu 2-3 razy; śpiewa nawet w deszczu',
        'unique_en': 'only bird to smash snails on a stone — has its favourite anvil rock; repeats each song phrase 2-3 times; sings even in the rain',
    },
    'Common Wood Pigeon': {
        'pl': 'Grzywacz', 'sci': 'Columba palumbus',
        'diet_pl': 'nasiona, liście, zboże', 'breeding_pl': 'kwiecień–październik',
        'diet_en': 'seeds, leaves, grain', 'breeding_en': 'April–October',
        'unique_pl': 'jedyny gołąb który pije zasysając — wszystkie inne ptaki muszą unosić głowę; może mieć 3 lęgi rocznie; to on robi "gruchanie" które słyszysz z drzew',
        'unique_en': 'only pigeon that drinks by sucking — all other birds must tilt head back; can have 3 broods per year; responsible for the cooing you hear from trees',
    },
    'Eurasian Jay': {
        'pl': 'Sójka', 'sci': 'Garrulus glandarius',
        'diet_pl': 'żołędzie, owady, jaja', 'breeding_pl': 'kwiecień–czerwiec',
        'diet_en': 'acorns, insects, eggs', 'breeding_en': 'April–June',
        'unique_pl': 'zakopuje do 5000 żołędzi rocznie i pamięta każdy schowek — jest głównym sadzicielem dębów w Europie; potrafi naśladować głos jastrzębia żeby przepędzić inne ptaki',
        'unique_en': "buries up to 5000 acorns per year and remembers every cache — Europe's main oak planter; can mimic a hawk's call to frighten other birds away",
    },
    'Eurasian Magpie': {
        'pl': 'Sroka', 'sci': 'Pica pica',
        'diet_pl': 'owady, padlina, jaja', 'breeding_pl': 'marzec–czerwiec',
        'diet_en': 'insects, carrion, eggs', 'breeding_en': 'March–June',
        'unique_pl': 'jeden z niewielu nieludzkich gatunków rozpoznających się w lustrze; buduje gniazdo z dachem z gałęzi; para pozostaje razem przez całe życie',
        'unique_en': 'one of very few non-human species that recognises itself in a mirror; builds a roofed nest; pair stays together for life',
    },
    'Blackcap': {
        'pl': 'Kapturka', 'sci': 'Sylvia atricapilla',
        'diet_pl': 'owady, jagody, nektar', 'breeding_pl': 'maj–lipiec',
        'diet_en': 'insects, berries, nectar', 'breeding_en': 'May–July',
        'unique_pl': 'jeden z najpiękniejszych śpiewaków Europy; populacja brytyjska zimuje w Polsce zamiast Afryki — ewolucja w czasie rzeczywistym; śpiewa nawet w nocy',
        'unique_en': "one of Europe's finest singers; British population winters in Poland instead of Africa — evolution in real time; sings even at night",
    },
    'Dunnock': {
        'pl': 'Pokrzywnica', 'sci': 'Prunella modularis',
        'diet_pl': 'owady, nasiona, pająki', 'breeding_pl': 'marzec–lipiec',
        'diet_en': 'insects, seeds, spiders', 'breeding_en': 'March–July',
        'unique_pl': 'wygląda jak wróbel ale to zupełnie inny gatunek; ma wyjątkowo skomplikowany system kojarzenia — samica często ma kilku partnerów jednocześnie; chodzi nisko kuląc się przy ziemi',
        'unique_en': 'looks like a sparrow but is a completely different species; has an unusually complex mating system — female often has several partners at once; walks in a low, shuffling crouch',
    },
    'Common Swift': {
        'pl': 'Jerzyk', 'sci': 'Apus apus',
        'diet_pl': 'owady (wyłącznie w locie)', 'breeding_pl': 'czerwiec–lipiec',
        'diet_en': 'insects (only in flight)', 'breeding_en': 'June–July',
        'unique_pl': 'przez 10 miesięcy w roku nigdy nie ląduje — śpi, je i kopuluje w powietrzu; może przelecieć 200 000 km zanim pierwszy raz usiądzie; żyje do 21 lat',
        'unique_en': 'for 10 months of the year never lands — sleeps, eats and mates in the air; may fly 200,000 km before first landing; lives up to 21 years',
    },
    'Eurasian Wren': {
        'pl': 'Strzyżyk', 'sci': 'Troglodytes troglodytes',
        'diet_pl': 'owady, pająki, larwy', 'breeding_pl': 'kwiecień–lipiec',
        'diet_en': 'insects, spiders, larvae', 'breeding_en': 'April–July',
        'unique_pl': 'jeden z najgłośniejszych ptaków Europy względem masy ciała — śpiew słyszalny z 500 m; samiec buduje do 12 gniazd i zaprasza samicę żeby wybrała; zimą stłaczają się grupowo dla ciepła',
        'unique_en': "one of Europe's loudest birds relative to body size — song carries 500m; male builds up to 12 nests and invites female to choose; huddle together in groups for warmth in winter",
    },
    'Long-tailed Tit': {
        'pl': 'Raniuszek', 'sci': 'Aegithalos caudatus',
        'diet_pl': 'owady, pająki, jaja owadów', 'breeding_pl': 'marzec–maj',
        'diet_en': 'insects, spiders, insect eggs', 'breeding_en': 'March–May',
        'unique_pl': 'buduje kuliste gniazdo z ponad 2000 piór i 1500 kawałków porostu — trwa miesiąc; porusza się familijnymi grupkami cały rok; ciało 6 cm, ogon kolejne 8 cm',
        'unique_en': 'builds a ball-shaped nest from over 2000 feathers and 1500 pieces of lichen — takes a month; moves in family groups year-round; body is 6cm, tail another 8cm',
    },
    'Eurasian Nuthatch': {
        'pl': 'Kowalik', 'sci': 'Sitta europaea',
        'diet_pl': 'owady, orzechy, nasiona', 'breeding_pl': 'kwiecień–czerwiec',
        'diet_en': 'insects, nuts, seeds', 'breeding_en': 'April–June',
        'unique_pl': 'jedyny europejski ptak chodzący głową w dół po pniu bez podpierania ogonem; zamurowuje wejście do dziupli błotem żeby dopasować do siebie; zakopuje orzechy na zimę i pamięta gdzie',
        'unique_en': 'only European bird to walk headfirst down tree trunks without tail support; plasters nest hole with mud to fit its exact size; caches nuts for winter and remembers every spot',
    },
    'Short-toed Treecreeper': {
        'pl': 'Pełzacz ogrodowy', 'sci': 'Certhia brachydactyla',
        'diet_pl': 'owady, pająki, larwy', 'breeding_pl': 'kwiecień–lipiec',
        'diet_en': 'insects, spiders, larvae', 'breeding_en': 'April–July',
        'unique_pl': 'zawsze wspina się w górę spiralą, nigdy w dół; dziób zakrzywiony jak igła sięga w szczeliny kory; śpi przyklejony do kory — wygląda jak kawałek drewna',
        'unique_en': 'always climbs upward in a spiral, never down; curved bill probes every bark crevice; sleeps pressed flat against bark — looks like a piece of wood',
    },
    'European Goldfinch': {
        'pl': 'Szczygieł', 'sci': 'Carduelis carduelis',
        'diet_pl': 'nasiona ostów, łopianów, słonecznika', 'breeding_pl': 'kwiecień–sierpień',
        'diet_en': 'thistle seeds, burdock, sunflower', 'breeding_en': 'April–August',
        'unique_pl': 'najbarwniejszy łuszczak ogrodu — czerwona maska, złote pasy; długi dziób stworzony do wyciągania nasion z głęboko ukrytych główek ostów; śpiewa w locie melodyjnym trelem',
        'unique_en': 'most colourful garden finch — red face mask, gold wing bars; long bill evolved to extract seeds from deep inside thistle heads; sings in flight with a tinkling trill',
    },
    'Common Linnet': {
        'pl': 'Makolągwa', 'sci': 'Linaria cannabina',
        'diet_pl': 'nasiona chwastów, owady', 'breeding_pl': 'kwiecień–sierpień',
        'diet_en': 'weed seeds, insects', 'breeding_en': 'April–August',
        'unique_pl': 'samiec ma jaskrawoczerwoną pierś i czoło tylko latem — zimą jest brązowy; śpiewa w złożonym chórze z innymi; populacja spada przez zanik chwastów polnych',
        'unique_en': 'male has bright crimson breast and forehead only in summer — brown in winter; sings in complex communal choruses; population falling due to loss of farmland weeds',
    },
    'Eurasian Bullfinch': {
        'pl': 'Gil', 'sci': 'Pyrrhula pyrrhula',
        'diet_pl': 'pąki drzew, nasiona, jagody', 'breeding_pl': 'kwiecień–czerwiec',
        'diet_en': 'tree buds, seeds, berries', 'breeding_en': 'April–June',
        'unique_pl': 'samiec Gila ma najbardziej nasycony kolor różowo-czerwony wśród europejskich ptaków śpiewających; zjada pąki drzew owocowych wiosną; para jest nierozłączna — jeśli widzisz jednego, drugi jest obok',
        'unique_en': 'male Bullfinch has the most saturated pink-red of any European songbird; eats fruit tree buds in spring; pair is inseparable year-round — if you see one, the other is always nearby',
    },
    'Hawfinch': {
        'pl': 'Grubodziób', 'sci': 'Coccothraustes coccothraustes',
        'diet_pl': 'pestki wiśni, nasiona twardopestkowe', 'breeding_pl': 'kwiecień–czerwiec',
        'diet_en': 'cherry stones, hard seeds', 'breeding_en': 'April–June',
        'unique_pl': 'dziób Grubodzioba generuje siłę 50 kg — kruszy pestki wiśni które wymagają imadła maszynowego; jeden z najskrytszych ptaków ogrodu, rzadko widziany mimo regularnych wizyt; sylwetka z charakterystyczną "szyją byka"',
        'unique_en': "Hawfinch bill generates 50kg of force — cracks cherry stones that need a machine vice; one of the most secretive garden birds, rarely seen despite regular visits; stocky bull-necked silhouette",
    },
    'Yellowhammer': {
        'pl': 'Trznadel', 'sci': 'Emberiza citrinella',
        'diet_pl': 'nasiona, owady, zboże', 'breeding_pl': 'kwiecień–sierpień',
        'diet_en': 'seeds, insects, grain', 'breeding_en': 'April–August',
        'unique_pl': 'jego śpiew to po angielsku "a-little-bit-of-bread-and-no-cheese"; głowa samca jest intensywnie cytrynowożółta; śpiewa niestrudzenie przez całe lato z tego samego miejsca',
        'unique_en': '"a-little-bit-of-bread-and-no-cheese" — the English mnemonic for its song; male\'s head is intensely lemon-yellow; sings tirelessly all summer from the same perch',
    },
    'Spotted Flycatcher': {
        'pl': 'Muchołówka szara', 'sci': 'Muscicapa striata',
        'diet_pl': 'owady chwytane w locie', 'breeding_pl': 'maj–lipiec',
        'diet_en': 'insects caught in flight', 'breeding_en': 'May–July',
        'unique_pl': 'wylatuje z gałęzi, chwyta owada i wraca dokładnie na to samo miejsce; przylata jako jeden z ostatnich ptaków wędrownych w maju; mistrz akrobatyki — skręca w ułamku sekundy',
        'unique_en': 'sallies from perch, catches insect and returns to exact same spot; arrives as one of the last migrants in May; aerial acrobat — turns in a fraction of a second',
    },
    'Common Redstart': {
        'pl': 'Pleszka', 'sci': 'Phoenicurus phoenicurus',
        'diet_pl': 'owady, pająki, jagody', 'breeding_pl': 'maj–lipiec',
        'diet_en': 'insects, spiders, berries', 'breeding_en': 'May–July',
        'unique_pl': 'charakterystycznie drży rdzawym ogonem — stąd nazwa; samiec ma efektowne czarne gardło i pomarańczowy brzuch; przylatuje z Afryki Subsaharyjskiej na sezon lęgowy',
        'unique_en': 'constantly quivers its rusty-red tail — hence "redstart"; male has striking black throat and orange breast; migrates from sub-Saharan Africa for the breeding season',
    },
    'Barn Swallow': {
        'pl': 'Jaskółka dymówka', 'sci': 'Hirundo rustica',
        'diet_pl': 'owady chwytane w locie', 'breeding_pl': 'maj–sierpień',
        'diet_en': 'insects caught in flight', 'breeding_en': 'May–August',
        'unique_pl': 'przelatuje 10 000 km do Afryki i wraca do tego samego gniazda rok po roku; może złapać 850 owadów dziennie nie lądując; lot nisko nad ziemią oznacza zmianę pogody',
        'unique_en': 'flies 10,000 km to Africa and returns to the same nest year after year; can catch 850 insects per day without landing; flying low signals incoming rain',
    },
    'Hooded Crow': {
        'pl': 'Wrona siwa', 'sci': 'Corvus cornix',
        'diet_pl': 'padlina, gryzonie, jaja, resztki', 'breeding_pl': 'marzec–czerwiec',
        'diet_en': 'carrion, rodents, eggs, scraps', 'breeding_en': 'March–June',
        'unique_pl': 'jeden z najinteligentniejszych ptaków świata — używa narzędzi, planuje, rozpoznaje twarze; upuszcza muszle na asfalt żeby je rozbić; pamięta ludzi którzy je skrzywdzili przez lata',
        'unique_en': 'one of the most intelligent birds on Earth — uses tools, plans ahead, recognises faces; drops shells onto tarmac to crack them; remembers people who wronged them for years',
    },
    'Jackdaw': {
        'pl': 'Kawka', 'sci': 'Coloeus monedula',
        'diet_pl': 'owady, nasiona, resztki', 'breeding_pl': 'kwiecień–czerwiec',
        'diet_en': 'insects, seeds, scraps', 'breeding_en': 'April–June',
        'unique_pl': 'para kawek pozostaje razem do śmierci; srebrne oczy nadają charakterystyczne spojrzenie; gniezdzi się w kominie lub skrzynce pocztowej; woła "czak-czak" przy lądowaniu',
        'unique_en': 'jackdaw pairs stay together until death; silvery eyes give a distinctive piercing gaze; nests in chimneys and letterboxes; calls "chak-chak" when landing',
    },
    'Collared Dove': {
        'pl': 'Sierpówka', 'sci': 'Streptopelia decaocto',
        'diet_pl': 'nasiona, zboże, jagody', 'breeding_pl': 'marzec–październik',
        'diet_en': 'seeds, grain, berries', 'breeding_en': 'March–October',
        'unique_pl': 'w 1950 roku nie było jej w Europie Zachodniej — w 50 lat skolonizowała cały kontynent; gniezdzi się przez 8 miesięcy i może mieć 6 lęgów; jej gruchanie to charakterystyczne "hu-HUU-hu"',
        'unique_en': 'absent from western Europe in 1950 — colonised the entire continent in 50 years; breeds for 8 months and can have 6 broods; its call is the distinctive "hu-HUU-hu" coo',
    },
    'Eurasian Siskin': {
        'pl': 'Czyżyk', 'sci': 'Spinus spinus',
        'diet_pl': 'nasiona olszy, brzozy, słonecznik', 'breeding_pl': 'marzec–lipiec',
        'diet_en': 'alder seeds, birch, sunflower', 'breeding_en': 'March–July',
        'unique_pl': 'zwisa głową w dół jak sikora żeby jeść nasiona z gałązek; przylatuje masowo zimą gdy w lesie brakuje nasion olszy; samiec ma czarną czapeczkę i żółte pasy',
        'unique_en': 'hangs upside-down like a tit to feed from branches; arrives in flocks in winter when alder seeds fail; male has black cap and yellow wing stripes',
    },
    'Fieldfare': {
        'pl': 'Kwiczoł', 'sci': 'Turdus pilaris',
        'diet_pl': 'jagody jarzębiny, dżdżownice', 'breeding_pl': 'maj–lipiec (Skandynawia)',
        'diet_en': 'rowan berries, earthworms', 'breeding_en': 'May–July (Scandinavia)',
        'unique_pl': 'przylatuje ze Skandynawii zimą w hałaśliwych stadach; agresywnie broni drzew jarzębiny przed innymi ptakami; obrzuca drapieżniki ekskrementami jako obroną — skutecznie',
        'unique_en': 'arrives from Scandinavia in winter in noisy flocks; aggressively defends rowan trees from other birds; pelts predators with droppings as defence — it works',
    },
    'Tree Sparrow': {
        'pl': 'Mazurek', 'sci': 'Passer montanus',
        'diet_pl': 'nasiona, owady, zboże', 'breeding_pl': 'kwiecień–sierpień',
        'diet_en': 'seeds, insects, grain', 'breeding_en': 'April–August',
        'unique_pl': 'odróżnij od wróbla po czarnej plamce na policzku i kasztanowej czapeczce; zarówno samiec jak i samica wyglądają identycznie; populacja spadła o 95% w UK przez intensywne rolnictwo',
        'unique_en': 'distinguished from house sparrow by black cheek spot and chestnut cap; male and female look identical; population fell 95% in UK due to intensive farming',
    },
    'Common Redpoll': {
        'pl': 'Czeczotka', 'sci': 'Acanthis flammea',
        'diet_pl': 'nasiona brzozy, olszy, ziół', 'breeding_pl': 'maj–lipiec',
        'diet_en': 'birch seeds, alder, herbs', 'breeding_en': 'May–July',
        'unique_pl': 'ma czerwoną "czapeczkę" od której pochodzi nazwa; przylatuje z dalekiej północy tylko zimą gdy brakuje nasion brzozy; akrobatycznie wisi na gałązkach jak czyżyk',
        'unique_en': 'has a red "poll" (cap) from which it gets its name; arrives from the far north only in winter when birch seeds fail; hangs acrobatically from twigs like a siskin',
    },
    'Marsh Tit': {
        'pl': 'Sikora uboga', 'sci': 'Poecile palustris',
        'diet_pl': 'owady, nasiona, jagody', 'breeding_pl': 'kwiecień–czerwiec',
        'diet_en': 'insects, seeds, berries', 'breeding_en': 'April–June',
        'unique_pl': 'wbrew nazwie nie mieszka na mokradłach — woli stare lasy liściaste; zakopuje setki nasion i pamięta dokładne lokalizacje; od czarnogłówki odróżnia ją tylko okrzyk "pitczu"',
        'unique_en': 'despite the name does not live in marshes — prefers old deciduous woodland; caches hundreds of seeds and remembers exact locations; distinguished from willow tit only by its "pitchou" call',
    },
}

_BLOCK_PL = ['Świt 5-8', 'Rano 8-11', 'Południe 11-14', 'Popołudnie 14-17', 'Wieczór 17-20']
_BLOCK_EN = ['Dawn 5-8', 'Morning 8-11', 'Midday 11-14', 'Afternoon 14-17', 'Evening 17-20']
_MONTH_PL = ['', 'stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca',
             'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia']


def _hour_to_block(h: int) -> int:
    if 5  <= h < 8:  return 0
    if 8  <= h < 11: return 1
    if 11 <= h < 14: return 2
    if 14 <= h < 17: return 3
    if 17 <= h < 20: return 4
    return -1

import re  # dodaj na górze jeśli nie ma

def _extract_json(raw: str) -> dict | None:
    """Wielopoziomowy parser — radzi sobie z cudzysłowami w tekście."""
    # 1. Próba bezpośrednia
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 2. Wyciągnij z bloku ```json ... ```
    if '```' in raw:
        for part in raw.split('```'):
            part = part.strip().lstrip('json').strip()
            if part.startswith('{'):
                try:
                    return json.loads(part)
                except json.JSONDecodeError:
                    pass

    # 3. Regex — wyciągnij story_pl i story_en wprost ze stringa
    pl = re.search(r'"story_pl"\s*:\s*"((?:[^"\\]|\\.)*)"\s*[,}]', raw, re.DOTALL)
    en = re.search(r'"story_en"\s*:\s*"((?:[^"\\]|\\.)*)"\s*[,}]', raw, re.DOTALL)
    if pl:
        return {
            'story_pl': pl.group(1),
            'story_en': en.group(1) if en else pl.group(1),
        }

    return None


def _generate_story(species_name: str, stats: dict) -> dict:
    bio   = BIRD_BIO.get(species_name, {})
    fav_h = stats.get('favorite_hour', 8)
    blk   = _hour_to_block(fav_h)
    first = stats.get('first_seen')

    first_pl = f"{first.day} {_MONTH_PL[first.month]} {first.year}" if first else "niedawno"
    first_en = first.strftime('%B %d, %Y') if first else "recently"
    blk_pl   = _BLOCK_PL[blk] if 0 <= blk <= 4 else f'o {fav_h}:00'
    blk_en   = _BLOCK_EN[blk] if 0 <= blk <= 4 else f'at {fav_h}:00'

    prompt = f"""Write a 2-3 sentence story card for a garden bird app.
Return ONLY valid JSON with this exact structure:
{{"story_pl": "...", "story_en": "..."}}

CRITICAL: Inside the JSON strings use only straight double quotes escaped as \\". 
Do NOT use curly quotes or typographic quotes inside strings.
Do NOT mention: breeding season, food searching, regular visitor.

SURPRISING FACT about {bio.get('pl', species_name)} ({species_name}):
PL: {bio.get('unique_pl', species_name)}
EN: {bio.get('unique_en', species_name)}

USER DATA:
- Visits: {stats.get('visits', 0)}
- Favorite time: PL="{blk_pl}" / EN="{blk_en}"
- First seen: PL="{first_pl}" / EN="{first_en}"
- Days in garden: {stats.get('days_in_garden', 1)}
- Current month: {datetime.now().strftime('%B')}"""

    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))
    msg = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=400,
        messages=[{'role': 'user', 'content': prompt}],
    )

    raw = msg.content[0].text.strip()
    result = _extract_json(raw)

    if result and 'story_pl' in result:
        return result

    # Ostatni fallback — zwróć czysty tekst bez JSON-wrappera
    clean = raw.replace('{"story_pl":', '').replace('"story_en":', '').strip(' {}"')
    return {'story_pl': clean[:400], 'story_en': clean[:400]}
    bio   = BIRD_BIO.get(species_name, {})
    fav_h = stats.get('favorite_hour', 8)
    blk   = _hour_to_block(fav_h)
    first = stats.get('first_seen')

    first_pl = f"{first.day} {_MONTH_PL[first.month]} {first.year}" if first else "niedawno"
    first_en = first.strftime('%B %d, %Y') if first else "recently"
    blk_pl   = _BLOCK_PL[blk] if 0 <= blk <= 4 else f'o {fav_h}:00'
    blk_en   = _BLOCK_EN[blk] if 0 <= blk <= 4 else f'at {fav_h}:00'

    prompt = f"""Write a 2-3 sentence story card for a garden bird app.
Return ONLY valid JSON: {{"story_pl": "...", "story_en": "..."}}

RULE: The story MUST open with the surprising fact below — connect it to the user's timing data.
Do NOT mention: breeding season, food searching, regular visitor.

SURPRISING FACT about {bio.get('pl', species_name)}:
PL: {bio.get('unique_pl', species_name)}
EN: {bio.get('unique_en', species_name)}

USER DATA:
- Visits: {stats.get('visits', 0)}
- Favorite time: PL="{blk_pl}" / EN="{blk_en}"
- First seen: PL="{first_pl}" / EN="{first_en}"
- Days in garden: {stats.get('days_in_garden', 1)}
- Current month: {datetime.now().strftime('%B')}"""

    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))
    msg = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=300,
        messages=[{'role': 'user', 'content': prompt}],
    )

    raw = msg.content[0].text.strip()
    if '```' in raw:
        for part in raw.split('```'):
            part = part.strip().lstrip('json').strip()
            if part.startswith('{'):
                raw = part
                break

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {'story_pl': raw[:250], 'story_en': raw[:250]}


# ── App setup ──────────────────────────────────────────────────────────────

app = FastAPI()

PHOTO_DIR = "/opt/bird-api/photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

API_KEY = "bird-secret-2026-xK9mP"


def verify_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


def get_db():
    return psycopg2.connect(
        host="localhost", dbname="birddb", user="bird", password="bird123"
    )


def save_detection(species, confidence, det_type, audio_path=None):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO detections (timestamp, species, confidence, type, audio_path) "
        "VALUES (NOW(), %s, %s, %s, %s) RETURNING id",
        (species, confidence, det_type, audio_path),
    )
    det_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return det_id


# ── Health ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


# ── Audio (BirdNET) ────────────────────────────────────────────────────────

@app.post("/audio")
async def receive_audio(
    file: UploadFile = File(...), _: str = Depends(verify_key)
):
    tmp_path = f"/tmp/{uuid.uuid4()}.wav"
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    try:
        rec = Recording(
            analyzer, tmp_path,
            lat=52.0, lon=21.0,
            date=date.today(),
            min_conf=0.7,
        )
        rec.analyze()
        results = []
        for d in rec.detections:
            det_id = save_detection(
                d["common_name"], d["confidence"], "audio", audio_path=tmp_path
            )
            results.append({
                "id": det_id,
                "species": d["common_name"],
                "confidence": round(d["confidence"], 3),
            })

        # Zachowaj nagranie dla gatunku z najwyższym confidence
        if results:
            top     = max(results, key=lambda x: x["confidence"])
            sp_dir  = "/opt/bird-api/recordings/{}".format(
                top["species"].lower().replace(" ", "_")
            )
            os.makedirs(sp_dir, exist_ok=True)
            dest    = f"{sp_dir}/{uuid.uuid4()}.wav"
            os.rename(tmp_path, dest)

            # Zaktualizuj audio_path dla wszystkich detekcji z tego nagrania
            conn2 = get_db()
            cur2  = conn2.cursor()
            for r in results:
                cur2.execute(
                    "UPDATE detections SET audio_path = %s WHERE id = %s",
                    (dest, r["id"])
                )
            conn2.commit()
            cur2.close()
            conn2.close()
        else:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return {"detections": results, "count": len(results)}
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise e


# ── Snapshot (YOLOv8 — osobny serwis, coming soon) ─────────────────────────

@app.post("/snapshot")
async def receive_snapshot(
    file: UploadFile = File(...), _: str = Depends(verify_key)
):
    data = await file.read()
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{YOLO_URL}/detect",
            files={"file": ("frame.jpg", data, "image/jpeg")},
        )
    resp.raise_for_status()
    r = resp.json()
    if not r["detected"]:
        return {"detected": False}
    conn = get_db()
    cur = conn.cursor()
    birds = []
    for b in r["birds"]:                      # jeden wiersz na ptaka
        cur.execute(
            "INSERT INTO detections (timestamp, species, confidence, type, "
            "photo_path, species_confidence) "
            "VALUES (NOW(), %s, %s, 'vision', %s, %s) RETURNING id",
            (b.get("species"), b["confidence"], b["photo_path"],
             b.get("species_confidence")),
        )
        det_id = cur.fetchone()[0]
        birds.append({
            "id": det_id,
            "confidence": b["confidence"],
            "species": b.get("species"),
            "species_confidence": b.get("species_confidence"),
            "photo_url": (f"{PHOTOS_BASE_URL}/{b['photo_path']}"
                          if b.get("photo_path") else None),
        })
    conn.commit()
    cur.close()
    conn.close()
    return {
        "detected": True,
        "count": r["count"],   # ptaków wykrytych łącznie
        "saved": r["saved"],   # cropów/wierszy zapisanych (limit MAX_CROPS)
        "birds": birds,
    }


# ── Detections ─────────────────────────────────────────────────────────────

@app.get("/detections")
def get_detections(limit: int = 50, _: str = Depends(verify_key)):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "SELECT id, timestamp, species, confidence, type, "
        "photo_path, species_confidence, verified_species "
        "FROM detections ORDER BY timestamp DESC LIMIT %s",
        (limit,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0],
            "timestamp": r[1].isoformat(),
            "species": r[2],
            "confidence": r[3],
            "type": r[4],
            "photo_path": r[5],
            "species_confidence": r[6],
            "verified_species": r[7],
            "photo_url": f"{PHOTOS_BASE_URL}/{r[5]}" if r[5] else None,
        }
        for r in rows
    ]


# ── Label correction (flywheel) ────────────────────────────────────────────

class LabelIn(BaseModel):
    species: str


@app.post("/detections/{det_id}/label")
def label_detection(det_id: int, body: LabelIn, _: str = Depends(verify_key)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE detections SET species=%s, verified_species=%s, "
        "verified_at=NOW() WHERE id=%s RETURNING id",
        (body.species, body.species, det_id),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(404, "detection not found")
    return {"ok": True, "id": det_id, "species": body.species}


# ── Species list ───────────────────────────────────────────────────────────

@app.get("/species")
def get_species(_: str = Depends(verify_key)):
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                WITH visit_starts AS (
                    SELECT species, timestamp,
                        timestamp - LAG(timestamp)
                            OVER (PARTITION BY species ORDER BY timestamp) AS gap
                    FROM detections
                    WHERE species IS NOT NULL
                ),
                visits AS (
                    SELECT species, timestamp
                    FROM visit_starts
                    WHERE gap IS NULL OR gap > INTERVAL '15 minutes'
                ),
                hour_counts AS (
                    SELECT species,
                           EXTRACT(HOUR FROM timestamp)::int AS hour,
                           COUNT(*) AS cnt
                    FROM visits
                    GROUP BY species, EXTRACT(HOUR FROM timestamp)
                ),
                fav_hours AS (
                    SELECT DISTINCT ON (species)
                           species, hour AS favorite_hour
                    FROM hour_counts
                    ORDER BY species, cnt DESC
                )
                SELECT v.species,
                       COUNT(*)::int                          AS visits,
                       MAX(d.timestamp)                       AS last_seen,
                       MIN(d.timestamp)                       AS first_seen,
                       COUNT(DISTINCT d.timestamp::date)::int AS days_in_garden,
                       COALESCE(f.favorite_hour, 8)           AS favorite_hour
                FROM visits v
                JOIN detections d ON d.species = v.species
                LEFT JOIN fav_hours f ON f.species = v.species
                GROUP BY v.species, f.favorite_hour
                ORDER BY visits DESC
            """)
            return cur.fetchall()
    finally:
        conn.close()


# ── Species detail ─────────────────────────────────────────────────────────

@app.get("/species/{species_name}/story")
def get_species_story(
    species_name: str,
    lang: str = "pl",
    _: str = Depends(verify_key),
):
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT story_pl, story_en, generated_at, visits_at_gen "
                "FROM species_info WHERE species = %s",
                (species_name,),
            )
            cached = cur.fetchone()

            cur.execute(
                "SELECT COUNT(*)::int AS visits FROM detections WHERE species = %s",
                (species_name,),
            )
            current_visits = cur.fetchone()["visits"]

            if cached and cached["generated_at"]:
                age_h = (datetime.now(timezone.utc) - cached["generated_at"]).total_seconds() / 3600
                visits_ok = current_visits <= (cached["visits_at_gen"] or 0) * 1.3
                if age_h < 24 and visits_ok:
                    story = cached.get(f"story_{lang}") or cached.get("story_pl", "")
                    return {
                        "story": story,
                        "generated_at": cached["generated_at"].isoformat(),
                        "cached": True,
                    }

            cur.execute("""
                SELECT COUNT(*)::int AS visits,
                       MAX(timestamp) AS last_seen,
                       MIN(timestamp) AS first_seen,
                       COUNT(DISTINCT timestamp::date)::int AS days_in_garden
                FROM detections WHERE species = %s
            """, (species_name,))
            stats = dict(cur.fetchone() or {})

            cur.execute("""
                SELECT EXTRACT(HOUR FROM timestamp)::int AS hour, COUNT(*) AS cnt
                FROM detections WHERE species = %s
                GROUP BY hour ORDER BY cnt DESC LIMIT 1
            """, (species_name,))
            fav = cur.fetchone()
            stats["favorite_hour"] = fav["hour"] if fav else 8
            stats["visits"] = current_visits

            try:
                stories  = _generate_story(species_name, stats)
                story_pl = stories.get("story_pl", "")
                story_en = stories.get("story_en", "")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

            cur.execute("""
                INSERT INTO species_info
                    (species, story_pl, story_en, generated_at, visits_at_gen)
                VALUES (%s, %s, %s, NOW(), %s)
                ON CONFLICT (species) DO UPDATE SET
                    story_pl      = EXCLUDED.story_pl,
                    story_en      = EXCLUDED.story_en,
                    generated_at  = NOW(),
                    visits_at_gen = EXCLUDED.visits_at_gen
            """, (species_name, story_pl, story_en, current_visits))
            conn.commit()

            return {
                "story": story_pl if lang == "pl" else story_en,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "cached": False,
            }
    finally:
        conn.close()


@app.get("/species/{species_name}")
def get_species_detail(species_name: str, _: str = Depends(verify_key)):
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT species,
                       COUNT(*)::int                          AS visits,
                       MAX(timestamp)                         AS last_seen,
                       MIN(timestamp)                         AS first_seen,
                       COUNT(DISTINCT timestamp::date)::int   AS days_in_garden
                FROM detections
                WHERE species = %s
                GROUP BY species
            """, (species_name,))
            stats = cur.fetchone()
            if not stats:
                raise HTTPException(status_code=404, detail="Species not found")

            cur.execute("""
                SELECT EXTRACT(HOUR FROM timestamp)::int AS hour, COUNT(*) AS cnt
                FROM detections WHERE species = %s
                GROUP BY hour ORDER BY cnt DESC LIMIT 1
            """, (species_name,))
            fav = cur.fetchone()
            stats["favorite_hour"] = fav["hour"] if fav else 8

            cur.execute("""
                SELECT EXTRACT(HOUR FROM timestamp)::int AS hour,
                       COUNT(*)::int AS cnt
                FROM detections WHERE species = %s
                GROUP BY hour ORDER BY hour
            """, (species_name,))
            histogram = {r["hour"]: r["cnt"] for r in cur.fetchall()}
            stats["hourly_histogram"] = [histogram.get(h, 0) for h in range(24)]

            return stats
    finally:
        conn.close()

# ── GET /activity/daily ────────────────────────────────────────────────────

@app.get("/activity/daily")
def get_daily_activity(days: int = 7, _: str = Depends(verify_key)):
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT DATE(timestamp) AS day, COUNT(*)::int AS count
                FROM detections
                WHERE timestamp >= NOW() - (%s * INTERVAL '1 day')
                GROUP BY day
                ORDER BY day
            """, (days,))
            rows = {str(r["day"]): r["count"] for r in cur.fetchall()}

        # Wypełnij brakujące dni zerami
        result = []
        for i in range(days - 1, -1, -1):
            day = (datetime.now() - timedelta(days=i)).date()
            result.append({"date": str(day), "count": rows.get(str(day), 0)})
        return result
    finally:
        conn.close()


# ── GET /species/{name}/trend ──────────────────────────────────────────────

@app.get("/species/{species_name}/trend")
def get_species_trend(species_name: str, days: int = 7,
                      _: str = Depends(verify_key)):
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT DATE(timestamp) AS day, COUNT(*)::int AS count
                FROM detections
                WHERE species = %s
                    AND timestamp >= NOW() - (%s * INTERVAL '1 day')
                GROUP BY day
                ORDER BY day
            """, (species_name, days))
            rows = {str(r["day"]): r["count"] for r in cur.fetchall()}

        result = []
        for i in range(days - 1, -1, -1):
            day = (datetime.now() - timedelta(days=i)).date()
            result.append({"date": str(day), "count": rows.get(str(day), 0)})
        return result
    finally:
        conn.close()

# -- Species recording ------------------------
@app.get("/species/{species_name}/recordings")
def get_species_recordings(
    species_name: str,
    limit: int = 5,
    _: str = Depends(verify_key)
):
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, timestamp, confidence, audio_path
                FROM detections
                WHERE species = %s
                  AND audio_path IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT %s
            """, (species_name, limit))
            rows = cur.fetchall()
            return [{
                'id':         r['id'],
                'timestamp':  r['timestamp'].isoformat(),
                'confidence': round(r['confidence'], 3),
                'url':        '/recordings/{}'.format(
                    r['audio_path'].replace(
                        '/opt/bird-api/recordings/', ''
                    )
                ),
            } for r in rows]
    finally:
        conn.close()