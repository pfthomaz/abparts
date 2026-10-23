"""align AutoBoss maintenance checklists with the operator manual

Replaces the Start of Day, End of Day and Weekly Service protocols with the
checklists from the AutoBoss V3.1B Operators Manual, Section 9 (June 2025),
and adds a Monthly Maintenance protocol from the April 2019 edition (the only
edition that lists monthly operator tasks). Every protocol and checklist item
gets translations for el, tr, no, es and ar.

The old protocols are deactivated rather than edited: checklist completions
cascade-delete with their checklist items, so rewriting the items in place
would destroy recorded maintenance history.

Revision ID: autoboss_checklists_001
Revises: supplier_receive_001
Create Date: 2026-10-23 00:00:00.000000

"""
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'autoboss_checklists_001'
down_revision = 'supplier_receive_001'
branch_labels = None
depends_on = None


OLD_START_PROTOCOL_ID = 'f459363d-1dbf-443f-b988-ab43bab0f520'
OLD_END_PROTOCOL_ID = '674da9b0-6d6b-4f40-a5c2-20ecc4d25aac'

# Referenced by frontend/src/pages/DailyOperations.js
START_PROTOCOL_ID = 'd339f134-80f4-4f09-a872-be35b9d2e10a'
END_PROTOCOL_ID = '5fe2a19a-61a2-4bf4-b749-f2a2fb2b2a29'
WEEKLY_PROTOCOL_ID = 'a6d4a88b-ecd1-4474-b45a-ab3b72b7e404'
MONTHLY_PROTOCOL_ID = '1eddd2eb-c57c-4e11-ad60-3108deedb06c'

NEW_PROTOCOL_IDS = (START_PROTOCOL_ID, END_PROTOCOL_ID, WEEKLY_PROTOCOL_ID, MONTHLY_PROTOCOL_ID)
LANGUAGES = ('el', 'tr', 'no', 'es', 'ar')


# --- Categories -------------------------------------------------------------

CAT_BEFORE_START = {
    'en': 'Before starting the engine',
    'el': 'Πριν ξεκινήσει ο κινητήρας',
    'tr': 'Motoru çalıştırmadan önce',
    'no': 'Før motoren startes',
    'es': 'Antes de arrancar el motor',
    'ar': 'قبل تشغيل المحرك',
}
CAT_BEFORE_REVS = {
    'en': 'After starting, before increasing engine revs',
    'el': 'Μετά την εκκίνηση, πριν αυξηθούν οι στροφές',
    'tr': 'Çalıştırdıktan sonra, devir artırılmadan önce',
    'no': 'Etter start, før turtallet økes',
    'es': 'Tras arrancar, antes de subir las revoluciones',
    'ar': 'بعد التشغيل وقبل زيادة سرعة المحرك',
}
CAT_AFTER_OPS = {
    'en': 'After daily operations',
    'el': 'Μετά τις καθημερινές εργασίες',
    'tr': 'Günlük çalışmadan sonra',
    'no': 'Etter dagens drift',
    'es': 'Después de las operaciones del día',
    'ar': 'بعد العمليات اليومية',
}
CAT_FLUSHING = {
    'en': 'Freshwater flushing (in order)',
    'el': 'Ξέπλυμα με γλυκό νερό (με τη σειρά)',
    'tr': 'Tatlı su ile yıkama (sırayla)',
    'no': 'Ferskvannsspyling (i rekkefølge)',
    'es': 'Enjuague con agua dulce (en orden)',
    'ar': 'الشطف بالمياه العذبة (بالترتيب)',
}
CAT_DAILY_GREASING = {
    'en': 'Daily greasing',
    'el': 'Καθημερινή λίπανση',
    'tr': 'Günlük yağlama',
    'no': 'Daglig smøring',
    'es': 'Engrase diario',
    'ar': 'التشحيم اليومي',
}
CAT_WEEKLY = {
    'en': 'Weekly service',
    'el': 'Εβδομαδιαία συντήρηση',
    'tr': 'Haftalık bakım',
    'no': 'Ukentlig service',
    'es': 'Servicio semanal',
    'ar': 'الصيانة الأسبوعية',
}
CAT_MONTHLY = {
    'en': 'Monthly service',
    'el': 'Μηνιαία συντήρηση',
    'tr': 'Aylık bakım',
    'no': 'Månedlig service',
    'es': 'Servicio mensual',
    'ar': 'الصيانة الشهرية',
}

NOTE_LITHIUM_GREASE = {
    'en': 'Use lithium based grease (Section 9, page 12).',
    'el': 'Χρησιμοποιήστε γράσο με λίθιο (Κεφ. 9, σελ. 12).',
    'tr': 'Lityum bazlı gres kullanın (Bölüm 9, sayfa 12).',
    'no': 'Bruk litiumbasert fett (seksjon 9, side 12).',
    'es': 'Utilice grasa a base de litio (Sección 9, página 12).',
    'ar': 'استخدم شحمًا أساسه الليثيوم (القسم 9، الصفحة 12).',
}
NOTE_FLUSH_SAFETY = {
    'en': 'SAFETY: If the washing discs start to rotate during flushing, shut down the AutoBoss IMMEDIATELY. Failure to do so can cause catastrophic disc failure and serious harm.',
    'el': 'ΑΣΦΑΛΕΙΑ: Εάν οι δίσκοι αρχίσουν να περιστρέφονται κατά το ξέπλυμα, σβήστε αμέσως το AutoBoss. Κίνδυνος καταστροφής των δίσκων και σοβαρής βλάβης.',
    'tr': 'GÜVENLİK: Yıkama sırasında yıkama diskleri dönmeye başlarsa AutoBoss\'u DERHAL kapatın. Aksi takdirde disklerde ciddi hasar ve ağır yaralanmalar meydana gelebilir.',
    'no': 'SIKKERHET: Hvis vaskeskivene begynner å rotere under spylingen, stopp AutoBoss UMIDDELBART. Ellers kan skivene havarere og forårsake alvorlig skade.',
    'es': 'SEGURIDAD: Si los discos de lavado empiezan a girar durante el enjuague, apague el AutoBoss INMEDIATAMENTE. De lo contrario, los discos pueden fallar de forma catastrófica y causar lesiones graves.',
    'ar': 'السلامة: إذا بدأت أقراص الغسيل بالدوران أثناء الشطف، أوقف تشغيل AutoBoss فورًا. عدم القيام بذلك قد يؤدي إلى انهيار الأقراص وإلحاق ضرر جسيم.',
}


def item(item_type, critical, category, text, notes=None):
    return {
        'type': item_type,
        'critical': critical,
        'category': category,
        'text': text,
        'notes': notes or {},
    }


# --- Protocols --------------------------------------------------------------

START_OF_DAY = {
    'id': START_PROTOCOL_ID,
    'type': 'daily',
    'copy_from': [OLD_START_PROTOCOL_ID],
    'name': {
        'en': 'Start of Day',
        'el': 'Έναρξη ημέρας',
        'tr': 'Gün Başlangıcı',
        'no': 'Start av dagen',
        'es': 'Inicio del día',
        'ar': 'بداية اليوم',
    },
    'description': {
        'en': 'Every morning before starting. Source: AutoBoss V3.1B Operators Manual, Section 9 (June 2025), pages 6 and 11.',
        'el': 'Κάθε πρωί πριν από την εκκίνηση. Πηγή: AutoBoss V3.1B, Εγχειρίδιο χειριστή, Κεφ. 9 (Ιούνιος 2025), σελ. 6 και 11.',
        'tr': 'Her sabah çalıştırmadan önce. Kaynak: AutoBoss V3.1B Operatör Kılavuzu, Bölüm 9 (Haziran 2025), sayfa 6 ve 11.',
        'no': 'Hver morgen før oppstart. Kilde: AutoBoss V3.1B brukerhåndbok, seksjon 9 (juni 2025), side 6 og 11.',
        'es': 'Cada mañana antes de arrancar. Fuente: Manual del operador AutoBoss V3.1B, Sección 9 (junio de 2025), páginas 6 y 11.',
        'ar': 'كل صباح قبل التشغيل. المصدر: دليل مشغل AutoBoss V3.1B، القسم 9 (يونيو 2025)، الصفحتان 6 و11.',
    },
    'items': [
        item('check', True, CAT_BEFORE_START, {
            'en': 'Inspect the lifting strop for damage or wear. Inspect the lifting eye.',
            'el': 'Επιθεωρήστε τον ιμάντα ανύψωσης για βλάβη ή φθορά. Επιθεωρήστε και το μάτι ανύψωσης.',
            'tr': 'Kaldırma sapanını hasar veya aşınmaya karşı kontrol edin. Kaldırma mapasını kontrol edin.',
            'no': 'Kontroller løftestroppen for skade eller slitasje. Kontroller løfteøyet.',
            'es': 'Inspeccione la eslinga de elevación por si presenta daños o desgaste. Inspeccione la argolla de elevación.',
            'ar': 'افحص حمالة الرفع بحثًا عن أي تلف أو اهتراء. افحص عين الرفع.',
        }),
        item('check', True, CAT_BEFORE_START, {
            'en': 'Visually inspect the Power Pack Assembly, winch assembly, washing head assembly, umbilical and pontoon for damage or incorrect functioning.',
            'el': 'Οπτικός έλεγχος του Power Pack, του βαρούλκου, της κεφαλής πλύσης, του ομφαλού και του ποντονιού για ζημιά ή λανθασμένη λειτουργία.',
            'tr': 'Power Pack ünitesini, vinç ünitesini, yıkama kafası ünitesini, umbilikal hattı ve dubayı hasar veya hatalı çalışmaya karşı gözle kontrol edin.',
            'no': 'Kontroller kraftpakken (Power Pack), vinsjen, vaskehodet, umbilicalen og pongtongen visuelt for skade eller feil funksjon.',
            'es': 'Inspeccione visualmente el conjunto Power Pack, el cabrestante, el cabezal de lavado, el umbilical y el pontón por si presentan daños o un funcionamiento incorrecto.',
            'ar': 'افحص بالنظر مجموعة وحدة الطاقة (Power Pack) ومجموعة الونش ومجموعة رأس الغسيل والكابل السري (umbilical) والعوامة بحثًا عن أي تلف أو خلل في التشغيل.',
        }),
        item('check', True, CAT_BEFORE_START, {
            'en': 'Check for oil and water leaks: water in the pontoon or salt deposits on the power pack assembly and other components.',
            'el': 'Ελέγξτε για διαρροές λαδιού και νερού: νερό στο ποντόνιο ή συσσώρευση αλάτων στο Power Pack και στα εξαρτήματα.',
            'tr': 'Yağ ve su kaçaklarını kontrol edin: dubada su veya Power Pack ünitesinde ve diğer parçalarda tuz birikintisi.',
            'no': 'Se etter olje- og vannlekkasjer: vann i pongtongen eller saltavleiringer på kraftpakken og andre komponenter.',
            'es': 'Compruebe si hay fugas de aceite y agua: agua en el pontón o depósitos de sal en el Power Pack y otros componentes.',
            'ar': 'تحقق من وجود تسربات للزيت أو الماء: ماء داخل العوامة أو ترسبات ملحية على وحدة الطاقة والمكونات الأخرى.',
        }),
        item('service', False, CAT_BEFORE_START, {
            'en': 'Wipe down and clean the power pack assembly and pontoon so that leaks and other abnormalities are easy to see.',
            'el': 'Σκουπίστε και καθαρίστε το Power Pack και το ποντόνιο, ώστε να φαίνονται εύκολα διαρροές και ανωμαλίες.',
            'tr': 'Kaçakların ve diğer anormalliklerin kolayca görülebilmesi için Power Pack ünitesini ve dubayı silip temizleyin.',
            'no': 'Tørk av og rengjør kraftpakken og pongtongen slik at lekkasjer og andre avvik er lette å se.',
            'es': 'Limpie el Power Pack y el pontón para que las fugas y otras anomalías se vean con facilidad.',
            'ar': 'امسح ونظّف وحدة الطاقة والعوامة حتى يسهل ملاحظة التسربات وأي خلل آخر.',
        }),
        item('check', False, CAT_BEFORE_START, {
            'en': 'Check all engine and PTO belts for wear and tightness. Deflection should be approximately 15 mm midway between the pulleys.',
            'el': 'Ελέγξτε όλους τους ιμάντες κινητήρα και δυναμοδότη (PTO) για φθορά και τάση. Κάμψη περίπου 15 mm στο μέσον μεταξύ των τροχαλιών.',
            'tr': 'Tüm motor ve PTO kayışlarını aşınma ve gerginlik açısından kontrol edin. Kasnakların ortasında esneme yaklaşık 15 mm olmalıdır.',
            'no': 'Kontroller alle motor- og kraftuttaksreimer (PTO) for slitasje og stramming. Nedbøyningen skal være ca. 15 mm midt mellom reimskivene.',
            'es': 'Revise el desgaste y la tensión de todas las correas del motor y de la toma de fuerza (PTO). La flexión debe ser de aproximadamente 15 mm en el punto medio entre las poleas.',
            'ar': 'افحص جميع سيور المحرك ومأخذ القدرة (PTO) من حيث الاهتراء والشد. يجب أن يكون الانحراف نحو 15 مم في المنتصف بين البكرات.',
        }),
        item('check', True, CAT_BEFORE_START, {
            'en': 'Check the engine oil and water levels.',
            'el': 'Ελέγξτε τη στάθμη λαδιού και νερού του κινητήρα.',
            'tr': 'Motor yağı ve su seviyelerini kontrol edin.',
            'no': 'Kontroller motoroljenivået og vannivået.',
            'es': 'Compruebe los niveles de aceite y agua del motor.',
            'ar': 'افحص مستوى زيت المحرك ومستوى الماء.',
        }),
        item('service', True, CAT_BEFORE_START, {
            'en': 'Use a clean filter bag at the start of every day.',
            'el': 'Χρησιμοποιήστε καθαρό σακόφιλτρο στην αρχή κάθε ημέρας.',
            'tr': 'Her günün başında temiz bir filtre torbası kullanın.',
            'no': 'Bruk en ren filterpose ved starten av hver dag.',
            'es': 'Utilice una bolsa filtrante limpia al inicio de cada día.',
            'ar': 'استخدم كيس فلتر نظيفًا في بداية كل يوم.',
        }),
        item('check', False, CAT_BEFORE_START, {
            'en': 'Check the primary strainer and clean it if necessary.',
            'el': 'Ελέγξτε το πρωτεύον φίλτρο και καθαρίστε το εάν χρειάζεται.',
            'tr': 'Ana süzgeci kontrol edin ve gerekirse temizleyin.',
            'no': 'Kontroller primærsilen og rengjør den ved behov.',
            'es': 'Revise el colador primario y límpielo si es necesario.',
            'ar': 'افحص المصفاة الأولية ونظّفها عند الحاجة.',
        }),
        item('check', True, CAT_BEFORE_START, {
            'en': 'Check the HP water pump oil level through the sight glass.',
            'el': 'Ελέγξτε τη στάθμη λαδιού της αντλίας νερού HP μέσω του γυαλιού.',
            'tr': 'HP su pompası yağ seviyesini gözetleme camından kontrol edin.',
            'no': 'Kontroller oljenivået i HP-vannpumpen gjennom seglasset.',
            'es': 'Compruebe el nivel de aceite de la bomba de agua HP a través de la mirilla.',
            'ar': 'افحص مستوى زيت مضخة المياه عالية الضغط (HP) عبر زجاج المراقبة.',
        }),
        item('check', False, CAT_BEFORE_START, {
            'en': 'Inspect the walking wheels for wear or damage.',
            'el': 'Επιθεωρήστε τους περιστρεφόμενους δίσκους οδηγούς (walking wheels) για φθορά ή ζημιά.',
            'tr': 'Yürüme tekerleklerini aşınma veya hasara karşı kontrol edin.',
            'no': 'Kontroller gangehjulene for slitasje eller skade.',
            'es': 'Inspeccione las ruedas de desplazamiento por si presentan desgaste o daños.',
            'ar': 'افحص عجلات الحركة بحثًا عن أي اهتراء أو تلف.',
        }),
        item('check', True, CAT_BEFORE_REVS, {
            'en': 'Check that both thrusters turn, confirming that the hydraulic system is correctly connected and functioning.',
            'el': 'Βεβαιωθείτε ότι στρέφονται και οι δύο προωθητήρες, ώστε να επιβεβαιωθεί ότι το υδραυλικό σύστημα είναι σωστά συνδεδεμένο και λειτουργεί.',
            'tr': 'Her iki iticinin de döndüğünü kontrol ederek hidrolik sistemin doğru bağlandığını ve çalıştığını doğrulayın.',
            'no': 'Kontroller at begge thrusterne roterer, slik at det bekreftes at hydraulikksystemet er riktig tilkoblet og fungerer.',
            'es': 'Compruebe que ambos propulsores giran, lo que confirma que el sistema hidráulico está bien conectado y funciona.',
            'ar': 'تحقق من دوران الدافعتين كلتيهما، للتأكد من أن النظام الهيدروليكي موصول بشكل صحيح ويعمل.',
        }),
        item('check', True, CAT_BEFORE_REVS, {
            'en': 'Check that the operating gauges are functioning.',
            'el': 'Ελέγξτε ότι λειτουργούν τα όργανα μέτρησης.',
            'tr': 'Çalışma göstergelerinin çalıştığını kontrol edin.',
            'no': 'Kontroller at driftsmålerne fungerer.',
            'es': 'Compruebe que los manómetros de funcionamiento funcionan.',
            'ar': 'تحقق من أن عدادات التشغيل تعمل.',
        }),
        item('check', True, CAT_BEFORE_REVS, {
            'en': 'Observe water exiting the HP water umbilical BEFORE connecting the washing head assembly HP water QRC to it.',
            'el': 'Παρατηρήστε ότι βγαίνει νερό από τον ομφαλό νερού HP ΠΡΙΝ συνδέσετε σε αυτόν τον ταχυσύνδεσμο (QRC) νερού HP της κεφαλής πλύσης.',
            'tr': 'Yıkama kafası ünitesinin HP su hızlı bağlantısını (QRC) HP su umbilikal hattına bağlamadan ÖNCE hattan su çıktığını görün.',
            'no': 'Se at det kommer vann ut av HP-vannumbilicalen FØR vaskehodets HP-vannhurtigkobling (QRC) kobles til den.',
            'es': 'Observe que sale agua del umbilical de agua HP ANTES de conectarle el acople rápido (QRC) de agua HP del cabezal de lavado.',
            'ar': 'تأكد من خروج الماء من كابل المياه عالية الضغط (umbilical) قبل توصيل وصلة التحرير السريع (QRC) الخاصة برأس الغسيل به.',
        }),
    ],
}

END_OF_DAY = {
    'id': END_PROTOCOL_ID,
    'type': 'daily',
    'copy_from': [OLD_END_PROTOCOL_ID],
    'name': {
        'en': 'End of Day',
        'el': 'Τέλος ημέρας',
        'tr': 'Gün Sonu',
        'no': 'Slutt på dagen',
        'es': 'Fin del día',
        'ar': 'نهاية اليوم',
    },
    'description': {
        'en': 'End of day service. Complete the freshwater flushing steps in order. Source: AutoBoss V3.1B Operators Manual, Section 9 (June 2025), pages 7, 11 and 12.',
        'el': 'Σέρβις στο τέλος της ημέρας. Ολοκληρώστε τα βήματα ξεπλύματος με γλυκό νερό με τη σειρά. Πηγή: AutoBoss V3.1B, Εγχειρίδιο χειριστή, Κεφ. 9 (Ιούνιος 2025), σελ. 7, 11 και 12.',
        'tr': 'Gün sonu bakımı. Tatlı su ile yıkama adımlarını sırayla tamamlayın. Kaynak: AutoBoss V3.1B Operatör Kılavuzu, Bölüm 9 (Haziran 2025), sayfa 7, 11 ve 12.',
        'no': 'Service ved slutten av dagen. Utfør ferskvannsspylingen i rekkefølge. Kilde: AutoBoss V3.1B brukerhåndbok, seksjon 9 (juni 2025), side 7, 11 og 12.',
        'es': 'Servicio de fin del día. Complete los pasos del enjuague con agua dulce en orden. Fuente: Manual del operador AutoBoss V3.1B, Sección 9 (junio de 2025), páginas 7, 11 y 12.',
        'ar': 'صيانة نهاية اليوم. نفّذ خطوات الشطف بالمياه العذبة بالترتيب. المصدر: دليل مشغل AutoBoss V3.1B، القسم 9 (يونيو 2025)، الصفحات 7 و11 و12.',
    },
    'items': [
        item('check', True, CAT_AFTER_OPS, {
            'en': 'Check the power pack assembly for leaks or obvious wear and tear.',
            'el': 'Ελέγξτε το Power Pack για διαρροές ή εμφανή φθορά.',
            'tr': 'Power Pack ünitesini kaçaklar veya belirgin aşınma ve yıpranma açısından kontrol edin.',
            'no': 'Kontroller kraftpakken for lekkasjer eller tydelig slitasje.',
            'es': 'Revise el Power Pack por si hay fugas o desgaste evidente.',
            'ar': 'افحص وحدة الطاقة بحثًا عن تسربات أو اهتراء واضح.',
        }),
        item('service', True, CAT_AFTER_OPS, {
            'en': 'Clean and replace the filter bag.',
            'el': 'Καθαρίστε και αντικαταστήστε το σακόφιλτρο.',
            'tr': 'Filtre torbasını temizleyip yerine takın.',
            'no': 'Rengjør og bytt filterposen.',
            'es': 'Limpie y reponga la bolsa filtrante.',
            'ar': 'نظّف كيس الفلتر واستبدله.',
        }),
        item('check', False, CAT_AFTER_OPS, {
            'en': 'Check the sight hole in both thruster props. Remove any debris, such as fishing line or rope fragments.',
            'el': 'Ελέγξτε από την τρύπα θέασης και στις δύο προπέλες των προωθητήρων. Αφαιρέστε τυχόν συντρίμμια, όπως πετονιές ή κομμάτια σχοινιού.',
            'tr': 'Her iki itici pervanesindeki gözetleme deliğini kontrol edin. Misina veya halat parçaları gibi her türlü kalıntıyı temizleyin.',
            'no': 'Kontroller inspeksjonshullet i begge thrusterpropellene. Fjern eventuelt rusk, som fiskesnøre eller taurester.',
            'es': 'Revise el orificio de inspección de ambas hélices de los propulsores. Retire cualquier residuo, como sedal o restos de cabo.',
            'ar': 'افحص فتحة المراقبة في مروحتي الدافعتين. أزل أي حطام مثل خيوط الصيد أو قطع الحبال.',
        }),
        item('service', True, CAT_FLUSHING, {
            'en': '1. Place the washing head assembly with the washing discs facing downwards, so that pressure on them prevents rotation.',
            'el': '1. Τοποθετήστε την κεφαλή πλύσης με τους δίσκους προς τα κάτω, ώστε να πιέζονται και να μην μπορούν να περιστραφούν.',
            'tr': '1. Yıkama kafası ünitesini yıkama diskleri aşağı bakacak şekilde yerleştirin; böylece disklerdeki baskı dönmelerini engeller.',
            'no': '1. Plasser vaskehodet med vaskeskivene vendt nedover, slik at trykket på dem hindrer rotasjon.',
            'es': '1. Coloque el cabezal de lavado con los discos de lavado hacia abajo, de modo que la presión sobre ellos impida que giren.',
            'ar': '1. ضع مجموعة رأس الغسيل بحيث تكون أقراص الغسيل متجهة إلى الأسفل، كي يمنع الضغط عليها دورانها.',
        }, NOTE_FLUSH_SAFETY),
        item('service', False, CAT_FLUSHING, {
            'en': '2. Connect the water intake to a hose placed inside a container of fresh water.',
            'el': '2. Συνδέστε την είσοδο νερού σε εύκαμπτο σωλήνα μέσα σε δοχείο με γλυκό νερό.',
            'tr': '2. Su girişini, tatlı su dolu bir kabın içine yerleştirilmiş bir hortuma bağlayın.',
            'no': '2. Koble vanninntaket til en slange som ligger i en beholder med ferskvann.',
            'es': '2. Conecte la entrada de agua a una manguera colocada dentro de un recipiente con agua dulce.',
            'ar': '2. وصّل مدخل الماء بخرطوم موضوع داخل وعاء مملوء بالمياه العذبة.',
        }),
        item('service', True, CAT_FLUSHING, {
            'en': '3. Start the engine at idle. DO NOT INCREASE ENGINE REVS.',
            'el': '3. Ξεκινήστε τον κινητήρα σε ρελαντί. ΜΗΝ ΑΝΕΒΑΣΕΤΕ ΣΤΡΟΦΕΣ ΚΙΝΗΤΗΡΑ.',
            'tr': '3. Motoru rölantide çalıştırın. MOTOR DEVRİNİ ARTIRMAYIN.',
            'no': '3. Start motoren på tomgang. IKKE ØK TURTALLET.',
            'es': '3. Arranque el motor al ralentí. NO AUMENTE LAS REVOLUCIONES DEL MOTOR.',
            'ar': '3. شغّل المحرك على السرعة الدنيا (الخمول). لا تزد سرعة المحرك.',
        }, NOTE_FLUSH_SAFETY),
        item('service', False, CAT_FLUSHING, {
            'en': '4. Run until fresh water is discharged from the washing discs and the bag filter assembly air bleed pipe.',
            'el': '4. Αφήστε τον κινητήρα να λειτουργεί μέχρι να βγει γλυκό νερό από τους δίσκους πλύσης και τον σωλήνα εξαέρωσης του σακόφιλτρου.',
            'tr': '4. Yıkama disklerinden ve torba filtre ünitesinin hava tahliye borusundan tatlı su çıkana kadar çalıştırın.',
            'no': '4. La motoren gå til det kommer ferskvann ut av vaskeskivene og luftingsrøret på posefilteret.',
            'es': '4. Mantenga el motor en marcha hasta que salga agua dulce por los discos de lavado y por el tubo de purga de aire del conjunto del filtro de bolsa.',
            'ar': '4. اترك المحرك يعمل حتى تخرج المياه العذبة من أقراص الغسيل ومن أنبوب تنفيس الهواء في مجموعة كيس الفلتر.',
        }, NOTE_FLUSH_SAFETY),
        item('service', True, CAT_FLUSHING, {
            'en': '5. Shut down the engine.',
            'el': '5. Σβήστε τον κινητήρα.',
            'tr': '5. Motoru kapatın.',
            'no': '5. Stopp motoren.',
            'es': '5. Apague el motor.',
            'ar': '5. أوقف تشغيل المحرك.',
        }),
        item('service', False, CAT_DAILY_GREASING, {
            'en': 'Grease the cleaner head bearings.',
            'el': 'Λιπάνετε τα ρουλεμάν της κεφαλής πλύσης.',
            'tr': 'Temizleme kafası rulmanlarını gresleyin.',
            'no': 'Smør lagrene i rengjøringshodet.',
            'es': 'Engrase los rodamientos del cabezal de limpieza.',
            'ar': 'شحّم محامل رأس التنظيف.',
        }, NOTE_LITHIUM_GREASE),
    ],
}

WEEKLY_SERVICE = {
    'id': WEEKLY_PROTOCOL_ID,
    'type': 'weekly',
    'copy_from': [],  # filled in at runtime from the active weekly protocols
    'name': {
        'en': 'Weekly Service',
        'el': 'Εβδομαδιαία συντήρηση',
        'tr': 'Haftalık Bakım',
        'no': 'Ukentlig service',
        'es': 'Servicio semanal',
        'ar': 'الصيانة الأسبوعية',
    },
    'description': {
        'en': 'Weekly monitoring and maintenance. REMINDER: Never shut the engine off at high idle unless urgent; allow a 2-minute cool-down before shutting down. Source: AutoBoss V3.1B Operators Manual, Section 9 (June 2025), pages 8, 9, 11 and 12.',
        'el': 'Εβδομαδιαία παρακολούθηση και συντήρηση. ΥΠΕΝΘΥΜΙΣΗ: Ποτέ μη σβήνετε τον κινητήρα σε υψηλές στροφές, εκτός επείγουσας περίπτωσης· αφήστε 2 λεπτά ψύξης πριν τον σβήσετε. Πηγή: AutoBoss V3.1B, Εγχειρίδιο χειριστή, Κεφ. 9 (Ιούνιος 2025), σελ. 8, 9, 11 και 12.',
        'tr': 'Haftalık izleme ve bakım. HATIRLATMA: Acil bir durum olmadıkça motoru asla yüksek rölantide kapatmayın; kapatmadan önce 2 dakika soğumasını bekleyin. Kaynak: AutoBoss V3.1B Operatör Kılavuzu, Bölüm 9 (Haziran 2025), sayfa 8, 9, 11 ve 12.',
        'no': 'Ukentlig overvåking og vedlikehold. PÅMINNELSE: Slå aldri av motoren på høyt tomgangsturtall med mindre det haster; la den kjøle seg ned i 2 minutter før den slås av. Kilde: AutoBoss V3.1B brukerhåndbok, seksjon 9 (juni 2025), side 8, 9, 11 og 12.',
        'es': 'Supervisión y mantenimiento semanal. RECORDATORIO: Nunca apague el motor a ralentí alto salvo urgencia; deje un ciclo de enfriamiento de 2 minutos antes de apagarlo. Fuente: Manual del operador AutoBoss V3.1B, Sección 9 (junio de 2025), páginas 8, 9, 11 y 12.',
        'ar': 'المراقبة والصيانة الأسبوعية. تذكير: لا تطفئ المحرك أبدًا وهو على سرعة خمول عالية إلا في حالة الطوارئ؛ اترك المحرك يبرد لمدة دقيقتين قبل إيقافه. المصدر: دليل مشغل AutoBoss V3.1B، القسم 9 (يونيو 2025)، الصفحات 8 و9 و11 و12.',
    },
    'items': [
        item('service', True, CAT_WEEKLY, {
            'en': 'Inspect and grease the walking wheels: 2 grease points per walking wheel.',
            'el': 'Επιθεωρήστε και λιπάνετε τους περιστρεφόμενους δίσκους οδηγούς (walking wheels): 2 σημεία λίπανσης στον καθένα.',
            'tr': 'Yürüme tekerleklerini kontrol edip gresleyin: her yürüme tekerleğinde 2 gres noktası.',
            'no': 'Kontroller og smør gangehjulene: 2 smørepunkter per gangehjul.',
            'es': 'Inspeccione y engrase las ruedas de desplazamiento: 2 puntos de engrase por rueda.',
            'ar': 'افحص عجلات الحركة وشحّمها: نقطتا تشحيم لكل عجلة.',
        }, NOTE_LITHIUM_GREASE),
        item('service', True, CAT_WEEKLY, {
            'en': 'Cycle the unloader valve to prevent seizure. Loosen it while the AutoBoss is running at idle, or while in the water and running under pressure. Run until water exits the HP water relief overflow outlet. Return the valve to the set-point on the back-nut.',
            'el': 'Δουλέψτε τη βαλβίδα εκτόνωσης για να μην κολλήσει. Χαλαρώστε τη όταν το AutoBoss λειτουργεί σε ρελαντί ή όταν βρίσκεται στο νερό και λειτουργεί υπό πίεση. Περιμένετε να βγει νερό από την έξοδο υπερχείλισης της HP και επαναφέρετε τη βαλβίδα στη ρύθμιση που σημειώνει το πίσω παξιμάδι.',
            'tr': 'Sıkışmasını önlemek için boşaltma (unloader) valfini çalıştırın. AutoBoss rölantide çalışırken veya suda basınç altında çalışırken valfi gevşetin. HP su tahliye taşma çıkışından su gelene kadar çalıştırın. Valfi arka somundaki ayar noktasına geri getirin.',
            'no': 'Mosjoner avlastningsventilen (unloader) for å hindre at den setter seg fast. Løsne den mens AutoBoss går på tomgang, eller mens den er i vannet og går under trykk. Kjør til det kommer vann ut av HP-overløpsutløpet. Sett ventilen tilbake til innstillingspunktet på bakmutteren.',
            'es': 'Accione la válvula de descarga (unloader) para evitar que se agarrote. Aflójela con el AutoBoss funcionando al ralentí, o en el agua y funcionando bajo presión. Manténgalo en marcha hasta que salga agua por la salida de rebose de alivio de agua HP. Devuelva la válvula al punto de ajuste marcado en la contratuerca.',
            'ar': 'شغّل صمام التفريغ (unloader) لمنع انحشاره. أرخِه بينما يعمل AutoBoss على سرعة الخمول، أو وهو في الماء ويعمل تحت الضغط. اتركه يعمل حتى يخرج الماء من مخرج فائض تنفيس المياه عالية الضغط. أعد الصمام إلى نقطة الضبط المحددة على الصامولة الخلفية.',
        }),
        item('check', False, CAT_WEEKLY, {
            'en': 'After resetting the unloader valve: water may leak from the relief overflow outlet for a few seconds while the valve re-seats. If leakage lasts more than 1 minute, investigate; the valve may need replacing.',
            'el': 'Μετά την επαναρύθμιση της βαλβίδας εκτόνωσης: μπορεί να διαρρεύσει νερό από την έξοδο υπερχείλισης για λίγα δευτερόλεπτα μέχρι να εδράσει η βαλβίδα. Εάν η διαρροή συνεχιστεί για περισσότερο από 1 λεπτό, πρέπει να διερευνηθεί· ίσως απαιτείται αντικατάσταση της βαλβίδας.',
            'tr': 'Boşaltma valfi yeniden ayarlandıktan sonra: valf yerine oturana kadar tahliye taşma çıkışından birkaç saniye su sızabilir. Sızıntı 1 dakikadan uzun sürerse inceleyin; valfin değiştirilmesi gerekebilir.',
            'no': 'Etter at avlastningsventilen er tilbakestilt: det kan lekke vann fra overløpsutløpet i noen sekunder mens ventilen setter seg. Varer lekkasjen mer enn 1 minutt, må det undersøkes; ventilen kan måtte byttes.',
            'es': 'Tras reajustar la válvula de descarga: puede salir agua por la salida de rebose de alivio durante unos segundos mientras la válvula se asienta. Si la fuga dura más de 1 minuto, investigue; puede que haya que sustituir la válvula.',
            'ar': 'بعد إعادة ضبط صمام التفريغ: قد يتسرب الماء من مخرج فائض التنفيس لبضع ثوانٍ ريثما يستقر الصمام في مكانه. إذا استمر التسرب أكثر من دقيقة واحدة، فيجب فحص السبب؛ فقد يحتاج الصمام إلى الاستبدال.',
        }),
        item('replacement', False, CAT_WEEKLY, {
            'en': 'Replace the remote control batteries and discard the used batteries.',
            'el': 'Αντικαταστήστε τις μπαταρίες του τηλεχειριστηρίου και απορρίψτε τις χρησιμοποιημένες.',
            'tr': 'Uzaktan kumanda pillerini değiştirin ve kullanılmış pilleri atın.',
            'no': 'Bytt batteriene i fjernkontrollen og kast de brukte batteriene.',
            'es': 'Sustituya las pilas del mando a distancia y deseche las usadas.',
            'ar': 'استبدل بطاريات جهاز التحكم عن بُعد وتخلّص من البطاريات المستعملة.',
        }),
        item('check', True, CAT_WEEKLY, {
            'en': 'Test the bilge pump by pressing the test button on its side. Confirm that it engages.',
            'el': 'Δοκιμάστε την αντλία σεντίνας (bilge pump) πιέζοντας το κουμπί δοκιμής στο πλάι της. Βεβαιωθείτε ότι ενεργοποιείται.',
            'tr': 'Yanındaki test düğmesine basarak sintine pompasını test edin. Devreye girdiğini doğrulayın.',
            'no': 'Test lensepumpen ved å trykke på testknappen på siden. Bekreft at den starter.',
            'es': 'Pruebe la bomba de achique pulsando el botón de prueba de su lateral. Confirme que se activa.',
            'ar': 'اختبر مضخة الآسن بالضغط على زر الاختبار الموجود على جانبها. تأكد من أنها تعمل.',
        }),
        item('check', True, CAT_WEEKLY, {
            'en': 'Test the automatic engine shut-down switch: with the engine at idle, lift the float switch and check that the engine shuts down fully.',
            'el': 'Ελέγξτε την αυτόματη απενεργοποίηση κινητήρα: με τον κινητήρα σε ρελαντί, ανυψώστε τον πλωτήρα-διακόπτη και βεβαιωθείτε ότι ο κινητήρας σβήνει πλήρως.',
            'tr': 'Otomatik motor durdurma şalterini test edin: motor rölantideyken şamandıra şalterini kaldırın ve motorun tamamen durduğunu kontrol edin.',
            'no': 'Test den automatiske motorstoppbryteren: med motoren på tomgang, løft flottørbryteren og kontroller at motoren stopper helt.',
            'es': 'Pruebe el interruptor de parada automática del motor: con el motor al ralentí, levante el interruptor de flotador y compruebe que el motor se apaga por completo.',
            'ar': 'اختبر مفتاح الإيقاف التلقائي للمحرك: والمحرك على سرعة الخمول، ارفع مفتاح العوامة وتحقق من توقف المحرك تمامًا.',
        }),
        item('service', False, CAT_WEEKLY, {
            'en': 'Lubricate the walking wheels with CRC spray.',
            'el': 'Λιπάνετε τους περιστρεφόμενους δίσκους οδηγούς (walking wheels) με ψεκασμό CRC.',
            'tr': 'Yürüme tekerleklerini CRC spreyle yağlayın.',
            'no': 'Smør gangehjulene med CRC-spray.',
            'es': 'Lubrique las ruedas de desplazamiento con spray CRC.',
            'ar': 'زيّت عجلات الحركة ببخاخ CRC.',
        }),
        item('check', False, CAT_WEEKLY, {
            'en': 'Carry out a thorough check of drive belt adjustment and wear.',
            'el': 'Κάντε ενδελεχή έλεγχο των ιμάντων κίνησης για ρύθμιση / τάση και φθορά.',
            'tr': 'Tahrik kayışlarının ayarını ve aşınmasını ayrıntılı olarak kontrol edin.',
            'no': 'Utfør en grundig kontroll av justering og slitasje på drivreimene.',
            'es': 'Realice una revisión a fondo del ajuste y el desgaste de las correas de transmisión.',
            'ar': 'افحص ضبط سيور الإدارة واهتراءها فحصًا شاملًا.',
        }),
        item('check', False, CAT_WEEKLY, {
            'en': 'Check that the flywheel support shaft bearing has been greased.',
            'el': 'Ελέγξτε ότι έχει λιπανθεί το ρουλεμάν του άξονα στήριξης του σφονδύλου.',
            'tr': 'Volan destek mili rulmanının greslendiğini kontrol edin.',
            'no': 'Kontroller at lageret på svinghjulets støtteaksel er smurt.',
            'es': 'Compruebe que se ha engrasado el rodamiento del eje de soporte del volante.',
            'ar': 'تحقق من تشحيم محمل عمود دعم الحذافة.',
        }),
    ],
}

MONTHLY_MAINTENANCE = {
    'id': MONTHLY_PROTOCOL_ID,
    'type': 'monthly',
    'copy_from': [],
    'name': {
        'en': 'Monthly Maintenance',
        'el': 'Μηνιαία συντήρηση',
        'tr': 'Aylık Bakım',
        'no': 'Månedlig vedlikehold',
        'es': 'Mantenimiento mensual',
        'ar': 'الصيانة الشهرية',
    },
    'description': {
        'en': 'Monthly monitoring and maintenance. Source: AutoBoss V3.1B Operators Manual, Section 9 (April 2019), page 10. Hours-based services (50, 250, 500, 750 and 1,000 hours) are carried out separately by an accredited mechanic.',
        'el': 'Μηνιαία παρακολούθηση και συντήρηση. Πηγή: AutoBoss V3.1B, Εγχειρίδιο χειριστή, Κεφ. 9 (Απρίλιος 2019), σελ. 10. Τα σέρβις βάσει ωρών λειτουργίας (50, 250, 500, 750 και 1.000 ώρες) εκτελούνται χωριστά από διαπιστευμένο μηχανικό.',
        'tr': 'Aylık izleme ve bakım. Kaynak: AutoBoss V3.1B Operatör Kılavuzu, Bölüm 9 (Nisan 2019), sayfa 10. Çalışma saatine bağlı bakımlar (50, 250, 500, 750 ve 1.000 saat) yetkili bir teknisyen tarafından ayrıca yapılır.',
        'no': 'Månedlig overvåking og vedlikehold. Kilde: AutoBoss V3.1B brukerhåndbok, seksjon 9 (april 2019), side 10. Timebasert service (50, 250, 500, 750 og 1000 timer) utføres separat av en godkjent mekaniker.',
        'es': 'Supervisión y mantenimiento mensual. Fuente: Manual del operador AutoBoss V3.1B, Sección 9 (abril de 2019), página 10. Los servicios por horas (50, 250, 500, 750 y 1000 horas) los realiza por separado un mecánico acreditado.',
        'ar': 'المراقبة والصيانة الشهرية. المصدر: دليل مشغل AutoBoss V3.1B، القسم 9 (أبريل 2019)، الصفحة 10. تُجرى الصيانة المرتبطة بساعات التشغيل (50 و250 و500 و750 و1000 ساعة) بشكل منفصل على يد ميكانيكي معتمد.',
    },
    'items': [
        item('service', False, CAT_MONTHLY, {
            'en': 'Remove all the washing discs from the washing head, clean them, grease them and refit them.',
            'el': 'Αφαιρέστε όλους τους δίσκους της κεφαλής πλύσης, καθαρίστε τους, γρασάρετέ τους και επανατοποθετήστε τους.',
            'tr': 'Yıkama kafasındaki tüm yıkama disklerini sökün, temizleyin, gresleyin ve yeniden takın.',
            'no': 'Demonter alle vaskeskivene fra vaskehodet, rengjør dem, smør dem og monter dem igjen.',
            'es': 'Desmonte todos los discos de lavado del cabezal de lavado, límpielos, engráselos y vuelva a montarlos.',
            'ar': 'فك جميع أقراص الغسيل من رأس الغسيل، ونظّفها، وشحّمها، ثم أعد تركيبها.',
        }, NOTE_LITHIUM_GREASE),
        item('service', False, CAT_MONTHLY, {
            'en': 'Open the walking wheels, clean them, remove excess grease, check the bungees and close them.',
            'el': 'Ανοίξτε τους περιστρεφόμενους δίσκους οδηγούς (walking wheels), καθαρίστε τους, αφαιρέστε το περίσσιο γράσο, ελέγξτε τα ελαστικά σχοινιά (bungees) και κλείστε τους.',
            'tr': 'Yürüme tekerleklerini açın, temizleyin, fazla gresi alın, elastik halatları (bungee) kontrol edin ve kapatın.',
            'no': 'Åpne gangehjulene, rengjør dem, fjern overflødig fett, kontroller strikkene (bungees) og lukk dem.',
            'es': 'Abra las ruedas de desplazamiento, límpielas, retire el exceso de grasa, revise las cuerdas elásticas (bungees) y vuelva a cerrarlas.',
            'ar': 'افتح عجلات الحركة، ونظّفها، وأزل الشحم الزائد، وافحص الحبال المطاطية (bungees)، ثم أغلقها.',
        }),
        item('service', False, CAT_MONTHLY, {
            'en': 'Clean salt deposits from the walking wheel mounts and grease them before refitting.',
            'el': 'Καθαρίστε τα άλατα από τα στηρίγματα των περιστρεφόμενων δίσκων οδηγών και γρασάρετέ τα πριν τα επανατοποθετήσετε.',
            'tr': 'Yürüme tekerleği bağlantılarındaki tuz birikintilerini temizleyin ve yeniden takmadan önce gresleyin.',
            'no': 'Rengjør saltavleiringer fra festene til gangehjulene og smør dem før de monteres igjen.',
            'es': 'Limpie los depósitos de sal de los soportes de las ruedas de desplazamiento y engráselos antes de volver a montarlos.',
            'ar': 'نظّف الترسبات الملحية عن حوامل عجلات الحركة وشحّمها قبل إعادة تركيبها.',
        }, NOTE_LITHIUM_GREASE),
    ],
}

PROTOCOLS = (START_OF_DAY, END_OF_DAY, WEEKLY_SERVICE, MONTHLY_MAINTENANCE)


def _insert_protocol(conn, protocol, order_offset):
    source_id = protocol['copy_from'][0] if protocol['copy_from'] else None
    source = None
    if source_id:
        source = conn.execute(
            sa.text("SELECT machine_model, display_order FROM maintenance_protocols WHERE id = :id"),
            {'id': source_id},
        ).first()

    conn.execute(
        sa.text("""
            INSERT INTO maintenance_protocols
                (id, name, protocol_type, service_interval_hours, is_recurring, machine_model,
                 description, is_active, display_order, base_language, created_at, updated_at)
            VALUES
                (:id, :name, CAST(:protocol_type AS protocoltype), NULL, true, :machine_model,
                 :description, true, :display_order, 'en', now(), now())
        """),
        {
            'id': protocol['id'],
            'name': protocol['name']['en'],
            'protocol_type': protocol['type'],
            'machine_model': source.machine_model if source else None,
            'description': protocol['description']['en'],
            'display_order': source.display_order if source else order_offset,
        },
    )

    for lang in LANGUAGES:
        conn.execute(
            sa.text("""
                INSERT INTO protocol_translations
                    (id, protocol_id, language_code, name, description, created_at, updated_at)
                VALUES (:id, :protocol_id, :lang, :name, :description, now(), now())
            """),
            {
                'id': str(uuid.uuid4()),
                'protocol_id': protocol['id'],
                'lang': lang,
                'name': protocol['name'][lang],
                'description': protocol['description'][lang],
            },
        )

    for order, entry in enumerate(protocol['items'], start=1):
        item_id = str(uuid.uuid4())
        conn.execute(
            sa.text("""
                INSERT INTO protocol_checklist_items
                    (id, protocol_id, item_order, item_description, item_type, item_category,
                     is_critical, notes, base_language, created_at)
                VALUES
                    (:id, :protocol_id, :item_order, :description, CAST(:item_type AS checklistitemtype),
                     :category, :critical, :notes, 'en', now())
            """),
            {
                'id': item_id,
                'protocol_id': protocol['id'],
                'item_order': order,
                'description': entry['text']['en'],
                'item_type': entry['type'],
                'category': entry['category']['en'],
                'critical': entry['critical'],
                'notes': entry['notes'].get('en'),
            },
        )
        for lang in LANGUAGES:
            conn.execute(
                sa.text("""
                    INSERT INTO checklist_item_translations
                        (id, checklist_item_id, language_code, item_description, notes, item_category,
                         created_at, updated_at)
                    VALUES (:id, :item_id, :lang, :description, :notes, :category, now(), now())
                """),
                {
                    'id': str(uuid.uuid4()),
                    'item_id': item_id,
                    'lang': lang,
                    'description': entry['text'][lang],
                    'notes': entry['notes'].get(lang),
                    'category': entry['category'][lang],
                },
            )


def upgrade():
    # A new enum value cannot be used in the transaction that adds it
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE protocoltype ADD VALUE IF NOT EXISTS 'monthly'")

    conn = op.get_bind()

    old_weekly_ids = [
        str(row.id) for row in conn.execute(
            sa.text("""
                SELECT id FROM maintenance_protocols
                WHERE protocol_type = 'weekly' AND is_active = true
                ORDER BY display_order, created_at
            """)
        )
    ]
    WEEKLY_SERVICE['copy_from'] = old_weekly_ids

    max_order = conn.execute(
        sa.text("SELECT COALESCE(MAX(display_order), 0) FROM maintenance_protocols")
    ).scalar()

    for offset, protocol in enumerate(PROTOCOLS, start=1):
        _insert_protocol(conn, protocol, max_order + offset)

    retired_ids = [OLD_START_PROTOCOL_ID, OLD_END_PROTOCOL_ID] + old_weekly_ids
    conn.execute(
        sa.text("""
            UPDATE maintenance_protocols
            SET is_active = false, updated_at = now()
            WHERE CAST(id AS text) = ANY(:ids)
        """),
        {'ids': retired_ids},
    )


def downgrade():
    conn = op.get_bind()

    conn.execute(
        sa.text("""
            UPDATE maintenance_protocols
            SET is_active = true, updated_at = now()
            WHERE CAST(id AS text) = ANY(:old_ids)
               OR (protocol_type = 'weekly' AND is_active = false AND CAST(id AS text) <> :weekly_id)
        """),
        {'old_ids': [OLD_START_PROTOCOL_ID, OLD_END_PROTOCOL_ID], 'weekly_id': WEEKLY_PROTOCOL_ID},
    )
    # Items, translations and checklist completions cascade with the protocols;
    # executions keep their rows with protocol_id set to NULL.
    conn.execute(
        sa.text("DELETE FROM maintenance_protocols WHERE CAST(id AS text) = ANY(:ids)"),
        {'ids': list(NEW_PROTOCOL_IDS)},
    )
    # PostgreSQL cannot drop an enum value; 'monthly' stays in protocoltype.
