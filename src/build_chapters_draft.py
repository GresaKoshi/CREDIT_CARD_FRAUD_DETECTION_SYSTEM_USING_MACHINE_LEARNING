# -*- coding: utf-8 -*-
"""
Builds a DETAILED WORKING DRAFT of Kapitujt IV-VIII, following Gresa's exact
table of contents. This is theory + real project results + real citations,
written to be rewritten/personalized into her own final voice before
submission -- it is explicitly NOT submission-ready prose (see note box).
"""
import json
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

ROOT = Path(__file__).resolve().parents[1]
PLOTS = ROOT / "outputs" / "plots"
SHOTS = ROOT / "outputs" / "screenshots"
OUT = ROOT / "Kapitujt_4-8_Draft_Pune.docx"

with open(ROOT / "outputs" / "evaluation_results.json") as f:
    R = json.load(f)
with open(ROOT / "outputs" / "eda_summary.json") as f:
    EDA = json.load(f)
with open(ROOT / "models" / "training_timings.json") as f:
    T = json.load(f)

BRAND = RGBColor(0x1F, 0x4E, 0x8C)
GRAY = RGBColor(0x55, 0x55, 0x55)


def h(doc, text, level=1, center=False):
    p = doc.add_heading(text, level=level)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.color.rgb = BRAND
    return p


def para(doc, text):
    return doc.add_paragraph(text)


def bullets(doc, items):
    for it in items:
        doc.add_paragraph(it, style="List Bullet")


def img(doc, path, caption, width=6.3):
    doc.add_picture(str(path), width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c = doc.add_paragraph()
    r = c.add_run(caption)
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = GRAY
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(12)


def note(doc, text):
    p = doc.add_paragraph()
    r = p.add_run("Shënim pune: " + text)
    r.italic = True
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(0x8A, 0x4B, 0x08)
    p.paragraph_format.space_after = Pt(10)


def metrics_table(doc):
    table = doc.add_table(rows=1, cols=7)
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for c, t in zip(hdr, ["Modeli", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "FP / FN"]):
        c.text = t
        for p in c.paragraphs:
            for r in p.runs:
                r.bold = True
    for name, m in R.items():
        row = table.add_row().cells
        row[0].text = name
        row[1].text = f"{m['accuracy']*100:.2f}%"
        row[2].text = f"{m['precision']*100:.2f}%"
        row[3].text = f"{m['recall']*100:.2f}%"
        row[4].text = f"{m['f1_score']*100:.2f}%"
        row[5].text = f"{m['roc_auc']*100:.2f}%"
        row[6].text = f"{m['false_positives']} / {m['false_negatives']}"
    doc.add_paragraph()


def main():
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # ---------------- Title / disclosure ----------------
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("Kapitujt IV–VIII — Draft Pune i Detajuar")
    r.bold = True
    r.font.size = Pt(20)
    r.font.color.rgb = BRAND
    s = doc.add_paragraph()
    s.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = s.add_run("Sistemi i Zbulimit të Mashtrimeve me Kartë Krediti duke Përdorur Mësimin Makinerik")
    r.italic = True
    r.font.size = Pt(13)

    note(
        doc,
        "Ky dokument është një DRAFT PUNE i detajuar, jo teksti final për dorzim. Përmban teori, "
        "citime dhe rezultate REALE të prodhuara nga projekti (jo të shpikura), të organizuara sipas "
        "Përmbajtjes së saj (Kapitujt IV–VIII). Gresa duhet ta rishkruajë/personalizojë në fjalët e veta "
        "para se ta paraqesë si punën e saj, në përputhje me Deklaratën e Autorisisë që kërkon Universum "
        "International College."
    )
    doc.add_page_break()

    # =========================================================
    # KAPITULLI IV
    # =========================================================
    h(doc, "KAPITULLI IV", level=1)
    h(doc, "4. Përpunimi dhe Analiza e të Dhënave", level=1)

    h(doc, "4.1 Përshkrimi i Dataset-it të Transaksioneve me Kartë Krediti", level=2)

    h(doc, "4.1.1 Burimi dhe struktura e të dhënave", level=3)
    para(doc,
        "Dataset-i i përdorur në këtë punim është 'Credit Card Fraud Detection', i mbledhur nga grupi "
        "kërkimor Machine Learning Group i Université Libre de Bruxelles (ULB) dhe i publikuar publikisht "
        "në platformën Kaggle. Ai përmban transaksione reale të kryera me karta krediti nga pronës europianë "
        f"gjatë muajit shtator 2013, gjithësej {EDA['n_transactions']:,} transaksione të regjistruara gjatë "
        "një periudhe dyditore. Kjo është një nga dataset-et më të përdorura në literaturën shkencore të "
        "zbulimit të mashtrimeve, për shkak të madhësisë së saj reale dhe etiketimit të saktë të rasteve "
        "(Dal Pozzolo et al., 2015)."
    )
    para(doc,
        "Për shkak të ndjeshmërisë së të dhënave financiare dhe kufizimeve të konfidencialitetit që "
        "institucionet bankare zbatojnë (të diskutuara edhe në propozimin e këtij punimi në seksionin "
        "Ethics), 28 nga 30 veçoritë origjinale të transaksionit janë transformuar paraprakisht me anë të "
        "Analizës së Komponentëve Kryesorë (Principal Component Analysis – PCA), duke prodhuar veçoritë "
        "e anonimizuara V1 deri V28. Kjo është një praktikë e zakonshme në kërkimin mbi mashtrimet "
        "financiare, pasi institucionet rrallë e ndërsjelltas ndajnë të dhëna të papërpunuara transaksionesh "
        "për arsye ligjore dhe privatësie (Bhattacharyya et al., 2011)."
    )

    h(doc, "4.1.2 Karakteristikat e transaksioneve", level=3)
    para(doc,
        "Dataset-i përmban 31 kolona: Time (koha në sekonda që ka kaluar nga transaksioni i parë në "
        "dataset), V1–V28 (veçoritë e transformuara me PCA, pa interpretim direkt fizik), Amount (shuma e "
        "transaksionit në euro), dhe Class (etiketa: 0 për transaksion legjitim, 1 për mashtrim)."
    )
    bullets(doc, [
        f"Shuma mesatare e transaksioneve legjitime: {EDA['amount_mean_legit']} €",
        f"Shuma mesatare e transaksioneve mashtruese: {EDA['amount_mean_fraud']} €",
        "Transaksionet mashtruese priren të kene një shpërndarje të ndryshme të shumës krahasuar me "
        "ato legjitime (shih Fig. 4.2), një vrojtim që përputhet me gjetjet e Whitrow et al. (2009) mbi "
        "përdorimin e agregimit të transaksioneve për zbulimin e mashtrimit.",
    ])

    h(doc, "4.1.3 Sfida e pabarazisë së klasave (class imbalance)", level=3)
    para(doc,
        f"Nga {EDA['n_transactions']:,} transaksione, vetëm {EDA['n_fraud']} ({EDA['fraud_rate_pct']}%) janë "
        "të etiketuara si mashtrim. Kjo përfaqëson një rast ekstrem të 'class imbalance' — një nga sfidat "
        "më të dokumentuara në literaturën e zbulimit të mashtrimeve (Bolton & Hand, 2002). Kur një "
        "klasifikues trajnohet mbi të dhëna kaq të pabarabarta pa ndërhyrje, ai priret të mësojë të "
        "parashikojë gjithmonë klasën shumicë (legjitim), duke arritur accuracy të lartë në dukje, por duke "
        "dështuar plotësisht në detyrën reale — zbulimin e rasteve të rralla të mashtrimit."
    )
    para(doc,
        "Në literaturë identifikohen tri qasje kryesore për të adresuar këtë sfidë: (1) teknika "
        "resampling (nën-marrja e klasës shumicë ose mbi-marrja e klasës pakicë), (2) mësim i ndjeshëm ndaj "
        "kostos (cost-sensitive learning), ku gabimet në klasën pakicë 'peshohen' më rëndë gjatë trajnimit "
        "(Bahnsen et al., 2016), dhe (3) përdorimi i modeleve ensemble që janë natyrshëm më robuste ndaj "
        "pabarazisë (Dal Pozzolo et al., 2015). Në këtë projekt u përdor qasja e parë (SMOTE, shih 4.2.2), "
        "e kombinuar me modele ensemble (Kapitulli V)."
    )

    h(doc, "4.2 Pastrimi dhe Përgatitja e të Dhënave", level=2)

    h(doc, "4.2.1 Trajtimi i vlerave të mungueshme", level=3)
    para(doc,
        "Në përgjithësi, pastrimi i të dhënave përfshin identifikimin dhe trajtimin e vlerave të mungueshme "
        "(missing values) përmes teknikave si fshirja e rështave/kolonave të prekura, imputimi me mesatare/"
        "medianë, ose imputimi i bazuar në modele (p.sh. KNN imputation). Në rastin e këtij dataset-i, u krye "
        "një verifikim sistematik (df.isnull().sum()) për të gjitha 31 kolonat, i cili konfirmoi që dataset-i "
        "nuk përmban asnjë vlerë të munguar — një karakteristikë tipike e dataset-eve benchmark të "
        "para-pastruara si ky, çka e bën atë të përshtatshëm për krahasim direkt ndërmjet algoritmeve pa "
        "zhurmën shtesë të vendimeve të imputimit."
    )

    h(doc, "4.2.2 Normalizimi dhe transformimi i të dhënave", level=3)
    para(doc,
        "Veçoritë V1–V28 janë tashmë në një shkallë të krahasueshme për shkak të transformimit PCA. Ndërsa "
        "Amount dhe Time kanë shkallë dhe shpërndarje shumë të ndryshme (Amount nga 0 deri në mij\u00ebra euro, "
        "Time nga 0 deri në ~172,800 sekonda). Algoritme si Logistic Regression janë të ndjeshme ndaj shkallës "
        "së veçorive, prandaj u aplikua StandardScaler (Z-score normalization: x' = (x − μ) / σ) mbi të dyja "
        "k\u00ebto kolona, duke i sjellë ato në një shpërndarje me mesatare 0 dhe devijim standard 1."
    )
    para(doc,
        "Bashkësia e të dhënave u nda 80%/20% në trajnim dhe testim, duke përdorur stratifikim sipas "
        "kolon\u00ebs Class për të siguruar që përqindja e rasteve të mashtrimit të mbetet e njëjtë në të dyja "
        "nën-bashk\u00ebsitë (tipike për dataset-e të pabarabarta)."
    )
    para(doc,
        "Për të adresuar pabarazinë e klasave të përshkruar në 4.1.3, u përdor teknika SMOTE (Synthetic "
        "Minority Over-sampling Technique), e propozuar fillimisht nga Chawla et al. (2002). SMOTE nuk "
        "thjesht kopjon rastet ekzistuese të pakic\u00ebs, por gjeneron shembuj sintetikë të rinj duke "
        "interpoluar ndërmjet një rasti mashtrimi dhe k fqinjëve të tij më të aftërt (k-nearest neighbors) "
        f"në hap\u00ebsirë n-dimensionale të veçorive. Në bashk\u00ebsinë e trajnimit, kjo e ndryshoi raportin nga "
        "227,451 raste legjitime kundrejt vetëm 394 raste mashtrimi, në një bashk\u00ebsi të balancuar plot\u00ebsisht "
        "227,451 kundrejt 227,451. Është kritike që SMOTE të aplikohet VETËM mbi bashk\u00ebsinë e trajnimit "
        "— bashk\u00ebsia e testimit (56,962 transaksione) mbetet e paprekur, me shpërndarjen origjinale prej "
        "0.17% mashtrim, pasi vler\u00ebsimi i modelit duhet të reflektojë kushtet reale të prodhimit, jo të "
        "dhëna artificialisht të balancuara."
    )

    h(doc, "4.3 Analiza Eksploruese e të Dhënave (EDA)", level=2)
    para(doc,
        "Analiza eksploruese (Exploratory Data Analysis) u krye për të kuptuar strukturën, shpërndarjen "
        "dhe marrëdh\u00ebniet ndërmjet veçorive para ndërtimit të modeleve. Grafik\u00ebt e m\u00ebposht\u00ebm u prodhuan nga "
        "scripti src/eda.py."
    )
    img(doc, PLOTS / "01_class_distribution.png", "Fig. 4.1 — Shpërndarja e klasave (shkallë logaritmike)")
    para(doc,
        "Fig. 4.1 ilustron vizualisht ekstremitetin e pabarazisë së diskutuar në 4.1.3: në shkallë "
        "logaritmike, shtylla e mashtrimit duket krah\u00ebsisht e madhe, por në realitet përfaqëson vetëm "
        "0.17% të të dhënave."
    )
    img(doc, PLOTS / "02_amount_distribution.png", "Fig. 4.2 — Shpërndarja e shum\u00ebs së transaksionit sipas klas\u00ebs")
    img(doc, PLOTS / "03_time_distribution.png", "Fig. 4.3 — Frekuenca e transaksioneve sipas or\u00ebs së dit\u00ebs")
    para(doc,
        "Fig. 4.3 tregon që transaksionet legjitime ndjekin një model të qartë ditor (rritje gjatë or\u00ebve të "
        "dites, rënie natën), ndërsa transaksionet mashtruese janë më të shpërndara në kohë, duke sugjeruar "
        "që koha e dites vetëm nuk mjafton si tregues i mashtrimit por mund të kontribuojë si veçori "
        "ndihm\u00ebse."
    )
    img(doc, PLOTS / "04_correlation_heatmap.png", "Fig. 4.4 — Matrica e korrelacionit ndërmjet veçorive")
    img(doc, PLOTS / "05_top_correlated_features.png", "Fig. 4.5 — Veçoritë më të korreluara me mashtrimin")
    para(doc,
        "Veçoritë me korrelacionin më të lartë (në vlerë absolute) me etiket\u00ebn Class janë V17 (r=0.326), "
        "V14 (r=0.303), V12 (r=0.261), V10 (r=0.217), V16 (r=0.197) dhe V3 (r=0.193). K\u00ebto veçori PCA të "
        "anonimizuara rezultuan më vonë të jenë gjithashtu ndër më të rëndësishmet për modelet e trajnuara "
        "(shih 6.x dhe Fig. 6.4), duke konfirmuar që korrelacioni linear dhe rëndësia e mësuar nga modelet "
        "jo-lineare (Random Forest, XGBoost) përputhen në këtë rast."
    )

    doc.add_page_break()

    # =========================================================
    # KAPITULLI V
    # =========================================================
    h(doc, "KAPITULLI V", level=1)
    h(doc, "5. Ndërtimi i Modeleve të Machine Learning", level=1)
    para(doc,
        "Duke u bazuar në propozimin e temës, u ndërtuan dhe u krahasuan tri familje algoritmesh të "
        "mësimit të mbikëqyrur për klasifikim binar (mashtrim / legjitim): Random Forest, XGBoost, dhe një "
        "model ensemble që i kombinon të dyja k\u00ebto së bashku me Logistic Regression si model bazë "
        "krahasimi (baseline)."
    )

    h(doc, "5.1 Random Forest", level=2)
    para(doc,
        "Random Forest është një algoritëm ensemble i përb\u00ebrë nga shumë pemë vendimi (decision trees), "
        "secila e trajnuar mbi një n\u00ebnbashk\u00ebsi të rastësishme të të dhënave të trajnimit (bagging — Bootstrap "
        "Aggregating) dhe një n\u00ebnbashk\u00ebsi të rastësishme të veçorive në secilin ndërshkim (Breiman, 2001). "
        "Parashikimi final përftohet me votim shumicë ndërmjet të gjitha pemëve. Ky mekanizëm redukton "
        "ndjeshëm variancën krahasuar me një pemë të vetme dhe e b\u00ebn modelin më robust ndaj overfitting-ut."
    )
    para(doc,
        "Ngai et al. (2011), në rishikimin e tyre të teknikave të data mining në zbulimin e mashtrimeve "
        "financiare, identifikuan Decision Trees dhe modelet e bazuara në to si ndër teknikat më të "
        "përdorura, për shkak të interpretueshm\u00ebrisë dhe aft\u00ebsisë për të kapur marrëdhënie jo-lineare "
        "ndërmjet veçorive të transaksionit."
    )
    para(doc,
        "Në këtë projekt, Random Forest u konfigurua me 200 pemë (n_estimators=200) dhe thellësi "
        "maksimale 12 (max_depth=12), për të balancuar aft\u00ebsinë e të mësuarit me kohën e trajnimit "
        f"(~{T.get('random_forest','?')} sekonda mbi 454,902 rreshta të balancuar me SMOTE)."
    )

    h(doc, "5.2 XGBoost", level=2)
    para(doc,
        "XGBoost (Extreme Gradient Boosting) është një implementim i optimizuar i gradient boosting-ut, i "
        "propozuar nga Chen & Guestrin (2016). Ndryshe nga Random Forest, ku pemët ndërtohen në menyrë të "
        "paralel dhe të pavarur, XGBoost ndërton pemë në menyrë sekuenciale, ku çdo pemë e re mëson të "
        "korrigjojë gabimet (residualet) e pemëve të m\u00ebparshme, duke minimizuar një funksion humbjeje "
        "(loss function) përmes zbritjes së gradientit. Algoritmi përfshin gjithashtu terma regularizimi që "
        "parandalojnë overfitting-un."
    )
    para(doc,
        "Konfigurimi i përdorur: 300 estimatorë, thellësi maksimale 6, learning_rate=0.1, subsample=0.9 "
        "dhe colsample_bytree=0.9 (për të futur randomizim shtesë dhe për të reduktuar overfitting-in). "
        f"Koha e trajnimit ishte ~{T.get('xgboost','?')} sekonda — dukshëm më e shpejtë se Random Forest, "
        "për shkak të optimizimeve të brendshme të librarisë (histogram-based split finding)."
    )
    note(doc,
        f"Rezultatet (Kapitulli VI) tregojnë që XGBoost ishte modeli individual më i mirë "
        f"(F1={R['XGBoost']['f1_score']*100:.1f}%, ROC-AUC={R['XGBoost']['roc_auc']*100:.1f}%). "
        "Ky rezultat konfirmohet edhe në literaturë: Bahnsen et al. (2016) dhe studime më të fundit tregojnë "
        "që metodat gradient-boosting priren të tejkalojnë Random Forest në dataset-e shumë të pabarabarta."
    )

    h(doc, "5.3 Modele Ensemble", level=2)
    para(doc,
        "Ideja e modeleve ensemble bazohet në parimin që kombinimi i disa modeleve 'të dobëta' ose "
        "të ndryshme ndërmjet tyre mund të prodhojë një parashikues më të fortë dhe më stabil se secili "
        "model individualisht — një parim që propozimi i këtij punimi e përmend eksplicit, duke iu "
        "referuar Ngai et al. (2011): 'kombinimi i disa modeleve mund të rrisë saktësinë e detektimit dhe "
        "të zvogëlojë gabimet'."
    )
    para(doc,
        "Në këtë projekt u përdor një Voting Classifier me 'soft voting', që kombinon Random Forest, "
        "XGBoost dhe Logistic Regression. Në soft voting, secili model prodhon një probabilitet për klas\u00ebn "
        "mashtrim, dhe k\u00ebto probabilitete mesatarizohen për të marrë vendimin final — ndryshe nga 'hard "
        "voting' ku çdo model voton vetëm për një klasë të përcaktuar. Soft voting përgjithsisht performon më "
        "mirë kur modelet bazë janë të kalibruara mirë për probabilitet."
    )
    note(doc,
        f"Rezultati: Ensemble arriti recall={R['Ensemble (Voting)']['recall']*100:.1f}% — më të lartë se "
        f"XGBoost i vet\u00ebm ({R['XGBoost']['recall']*100:.1f}%) — por precision më të ul\u00ebt. Kjo tregon një "
        "trade-off tipik që do të diskutohet në Kapitullin VI."
    )

    h(doc, "5.4 Trajnimi dhe Optimizimi i Modeleve", level=2)
    para(doc,
        "Të katër modelet u trajnuan mbi të njëjtën bashk\u00ebsi trajnimi të balancuar me SMOTE (454,902 "
        "rreshta), duke përdorur të njëjtat 29 veçori (V1–V28, Amount_scaled, Time_scaled). Koh\u00ebt e "
        "trajnimit të regjistruara janë:"
    )
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = "Light Grid Accent 1"
    tbl.rows[0].cells[0].text = "Modeli"
    tbl.rows[0].cells[1].text = "Koha e trajnimit (sekonda)"
    for k, v in T.items():
        row = tbl.add_row().cells
        row[0].text = k.replace("_", " ").title()
        row[1].text = str(v)
    doc.add_paragraph()
    para(doc,
        "Hiperparametrat (numri i pemëve, thellësia, learning rate) u zgjodhën me eksperimentim manual "
        "të bazuar në praktikat e sugjeruara në literaturë për dataset-e të ngjashme (Bahnsen et al., 2016; "
        "Dal Pozzolo et al., 2015), jo përmes kërkimi të plotë në rrjet (grid search). Një hap i ardhshëm i "
        "mundshëm për përmirësim do të ishte përdorimi i GridSearchCV ose Bayesian Optimization për të "
        "gjetur kombinimin optimal të hiperparametrave (shih Kapitulli VIII — Punë e ardhshme)."
    )

    h(doc, "5.5 Sfidat në Ndërtimin e Modeleve (overfitting, balancimi i të dhënave)", level=2)
    para(doc,
        "Një sfidë kryesore ishte rreziku i overfitting-ut të shkaktuar nga SMOTE: pasi shembujt sintetikë "
        "të klas\u00ebs mashtrim gjenerohen përmes interpolimit ndërmjet rasteve ekzistuese, modeli mund të "
        "'mësojë' modele shumë specifike për rajonin sintetik të hap\u00ebsir\u00ebs së veçorive, që nuk "
        "përgjith\u00ebsohen mirë në të dhëna reale të reja. Dal Pozzolo et al. (2015) diskutojnë në detaje "
        "k\u00ebtë rrezik në kontekstin e zbulimit të mashtrimeve me kartë krediti, duke rekomanduar që "
        "vler\u00ebsimi të b\u00ebhet gjithmonë mbi të dhëna testimi të pa-balancuara (praktikë e ndjekur në k\u00ebtë "
        "projekt, shih 4.2.2)."
    )
    para(doc,
        "Sfidë tjetër ishte balancimi vetë i procesit: një balancim shumë agresiv (p.sh. oversampling deri "
        "në raport 1:1 të plotë, siç u zbatua k\u00ebtu) mund të rrisë recall-in në kurriz të precision-it, pasi "
        "modeli b\u00ebhet më 'i ndjeshëm' ndaj sinjaleve të dobëta të mashtrimit dhe rrit numrin e false "
        "positives (shih 6.3). Kompromisi ndërmjet shkall\u00ebs së balancimit dhe precision/recall mbetet një "
        "vendim projektues që varet nga konteksti i përdorimit (p.sh. një bankë mund të preferojë recall më "
        "të lartë për të minimizuar humbjet financiare, edhe me koston e më shumë alarme të rreme)."
    )

    doc.add_page_break()

    # =========================================================
    # KAPITULLI VI
    # =========================================================
    h(doc, "KAPITULLI VI", level=1)
    h(doc, "6. Vler\u00ebsimi dhe Krahasimi i Modeleve", level=1)

    h(doc, "6.1 Metrikat e Vler\u00ebsimit: Accuracy, Precision, Recall, F1-score", level=2)
    para(doc,
        "Vler\u00ebsimi i çdo modeli klasifikimi bazohet në matric\u00ebn e konfuzionit (confusion matrix), e përb\u00ebrë "
        "nga katër vlera: True Positive (TP — mashtrim i identifikuar saktë), True Negative (TN — transaksion "
        "legjitim i identifikuar saktë), False Positive (FP — transaksion legjitim i gabuar si mashtrim), dhe "
        "False Negative (FN — mashtrim i pazbuluar)."
    )
    bullets(doc, [
        "Accuracy = (TP+TN) / (TP+TN+FP+FN) — përqindja e përgjithshme e parashikimeve të sakta.",
        "Precision = TP / (TP+FP) — nga të gjitha rastet e flaguara si mashtrim, sa % ishin vërtet mashtrim.",
        "Recall (Sensitivity) = TP / (TP+FN) — nga të gjitha rastet reale të mashtrimit, sa % u zbuluan.",
        "F1-score = 2 × (Precision × Recall) / (Precision + Recall) — mesatarja harmonike, që balancon "
        "të dyja metrikat.",
        "ROC-AUC — syprina n\u00ebn kurbën ROC (True Positive Rate kundrejt False Positive Rate në prag të "
        "ndryshme vendimi), tregon aft\u00ebsinë e përgjithshme dallues të modelit pavarësisht pragut të zgjedhur.",
    ])
    para(doc,
        "Siç theksojnë Bolton & Hand (2002) në rishikimin e tyre klasik të zbulimit statistikor të "
        "mashtrimeve, ACCURACY ËSHTË NJË METRIKË MASHTRUESE në dataset-e kaq të pabarabarta: një model që "
        "parashikon 'legjitim' për çdo transaksion do të arrinte accuracy prej 99.83% (duke qenë se vet\u00ebm "
        "0.17% e rasteve janë mashtrim) pa zbuluar asnjë rast të vetëm mashtrimi. Kjo është sakt\u00ebsisht "
        "arsyeja për që ky punim përqendrohet te precision, recall, F1-score dhe ROC-AUC si metrika "
        "kryesore vler\u00ebsimi, jo accuracy."
    )

    h(doc, "6.2 Krahasimi i Performancës së Modeleve", level=2)
    para(doc,
        f"Të katër modelet u vler\u00ebsuan mbi të njëjtën bashk\u00ebsi testimi ({R['XGBoost']['true_positives']+R['XGBoost']['false_negatives']+R['XGBoost']['true_negatives']+R['XGBoost']['false_positives']:,} "
        "transaksione, e pa-balancuar, që reflekton shpërndarjen reale prej 0.17% mashtrim):"
    )
    metrics_table(doc)
    img(doc, PLOTS / "10_metric_comparison.png", "Fig. 6.1 — Krahasimi i metrikave ndërmjet modeleve")
    img(doc, PLOTS / "06_roc_curves.png", "Fig. 6.2 — Kurbat ROC")
    img(doc, PLOTS / "07_precision_recall_curves.png", "Fig. 6.3 — Kurbat Precision-Recall")
    img(doc, PLOTS / "09_feature_importance.png", "Fig. 6.4 — Rëndësia e veçorive (RF dhe XGBoost)")
    para(doc,
        "Logistic Regression, edhe pse arrin accuracy të lartë (97.4%), ka precision shumë të ul\u00ebt (5.8%) "
        "— rreth 94% e alarmeve të saj janë të rreme. Kjo tregon kufizimin e një modeli linear përballë "
        "marrëdhënieve komplekse, jo-lineare të pranishme në të dhëna, dhe justifikon përdorimin e "
        "modeleve më të sofistikuara si Random Forest dhe XGBoost, siç sugjerohej në propozimin e temës. "
        "XGBoost arrin balancën më të mirë ndërmjet precision (72.3%) dhe recall (87.8%), duke rezultuar "
        "në F1-score më të lartë (79.3%) dhe ROC-AUC prej 98.0% — duke konfirmuar hipotez\u00ebn H1 të propozimit "
        "të temës."
    )

    h(doc, "6.3 Analiza e Gabimeve False Positive dhe False Negative", level=2)
    img(doc, PLOTS / "08_confusion_matrices.png", "Fig. 6.5 — Matricat e konfuzionit për të katër modelet")
    para(doc,
        f"Në kontekstin bankar, dy lloje gabimesh kanë pasoja shumë të ndryshme. Një False Negative "
        "(mashtrim i pazbuluar, XGBoost: "
        f"{R['XGBoost']['false_negatives']} raste) rezulton në humbje të drejtpërdrejtë financiare për bank\u00ebn "
        "ose klientin. Një False Positive (transaksion legjitim i flaguar gabimisht si mashtrim, XGBoost: "
        f"{R['XGBoost']['false_positives']} raste) nuk shkakton humbje financiare direkte, por krijon "
        "shqet\u00ebsim dhe pak\u00ebnaqësi te klienti (p.sh. kartë e bllokuar gabimisht), siç e përmend edhe Phua et "
        "al. (2010) në rishikimin e tyre mbi zbulimin e mashtrimeve të bazuar në data mining."
    )
    para(doc,
        "Për k\u00ebtë arsye, zgjedhja e modelit 'më të mirë' nuk është domosdoshmërisht ai me F1-score më të "
        f"lartë: Ensemble (Voting) arrin recall më të lartë ({R['Ensemble (Voting)']['recall']*100:.1f}%, "
        f"vet\u00ebm {R['Ensemble (Voting)']['false_negatives']} false negatives) se XGBoost "
        f"({R['XGBoost']['recall']*100:.1f}%, {R['XGBoost']['false_negatives']} false negatives), me koston e "
        f"më shumë false positives ({R['Ensemble (Voting)']['false_positives']} kundrejt "
        f"{R['XGBoost']['false_positives']}). Në një sistem real bankar, prag u vendimit (decision threshold) "
        "mund të rregullohet në bazë të kostos relative të k\u00ebtyre dy gabimeve për institucionin specifik."
    )

    doc.add_page_break()

    # =========================================================
    # KAPITULLI VII
    # =========================================================
    h(doc, "KAPITULLI VII", level=1)
    h(doc, "7. Implementimi i Aplikacionit Web", level=1)

    h(doc, "7.1 Arkitektura e Sistemit", level=2)
    para(doc,
        "Aplikacioni web u zhvillua me Flask, një microframework Python i lehtë për zhvillimin e "
        "aplikacioneve web. Arkitektura ndjek një model të thjeshtë të ngjashëm me MVC (Model-View-"
        "Controller): 'Modeli' përfaqësohet nga modelet e trajnuara ML të ruajtura në disk (format .joblib), "
        "'View' përfaqësohet nga template-t Jinja2/HTML të stilizuara me Bootstrap 5, dhe 'Controller' "
        "përfaqësohet nga rrugët (routes) Flask në webapp/app.py që lidhin k\u00ebrkesat HTTP me logjik\u00ebn e "
        "biznesit."
    )
    para(doc,
        "Katër faqe kryesore përb\u00ebjnë aplikacionin: Dashboard (statistika të p\u00ebrmbledhura), Transactions "
        "(monitorim/kërkim transaksionesh), Analyze (vler\u00ebsim në kohë reale i një transaksioni të vetëm), "
        "dhe Model Reports (krahasimi i detajuar i performancës së modeleve) — duke plot\u00ebsuar direkt "
        "kërkesën e propozimit të temës për 'zhvillimin e një aplikacioni web për monitorim dhe raportim në "
        "kohë reale'."
    )

    h(doc, "7.2 Integrimi i Modelit të Machine Learning në Aplikacion", level=2)
    para(doc,
        "Modeli ensemble (i cili doli më i mirë në bilanc precision/recall, shih 6.2–6.3), scaler-i "
        "(StandardScaler) dhe lista e kolonave të veçorive ruhen në disk në format .joblib gjatë fazes së "
        "trajnimit dhe ngarkohen në memorie vet\u00ebm një herë, në momentin kur niset serveri Flask "
        "(app.py, rreshtat e para) — jo në çdo k\u00ebrkesë HTTP, për arsye performance. Kur një p\u00ebrdorues "
        "zgjedh një transaksion në faqen Analyze, aplikacioni thërret model.predict_proba() mbi veçoritë e "
        "para-p\u00ebrpunuara të atij transaksioni dhe kthen probabilitetin e mashtrimit në kohë reale (< 1 "
        "sekondë)."
    )

    h(doc, "7.3 Dashboard-i për Monitorim dhe Raportim në Kohë Reale", level=2)
    para(doc,
        "Dashboard-i kryesor (Fig. 7.1) shfaq statistika të p\u00ebrmbledhura në kohë reale: numrin total të "
        "transaksioneve, rastet e konfirmuara të mashtrimit, shkallën e mashtrimit, dhe metrikat e modelit "
        "ensemble (precision, recall, F1, ROC-AUC), së bashku me një listë të transaksioneve më të fundit "
        "të flaguara si të dyshimta, të renditura sipas probabilitetit të mashtrimit."
    )
    img(doc, SHOTS / "01_dashboard.png", "Fig. 7.1 — Dashboard-i kryesor")
    img(doc, SHOTS / "02_transactions.png", "Fig. 7.2 — Faqja e monitorimit të transaksioneve")
    img(doc, SHOTS / "03_transactions_flagged.png", "Fig. 7.3 — Filtri i transaksioneve të flaguara")
    img(doc, SHOTS / "04_analyze.png", "Fig. 7.4 — Faqja Analyze (para vler\u00ebsimit)")
    img(doc, SHOTS / "06_analyze_result.png", "Fig. 7.5 — Rezultati i vler\u00ebsimit në kohë reale")
    img(doc, SHOTS / "05_reports.png", "Fig. 7.6 — Faqja e raporteve të modelit")

    h(doc, "7.4 Rezultatet e Testimit të Aplikacionit", level=2)
    para(doc,
        "Testimi funksional u krye në dy nivele. Së pari, testim manual në shfletues për të konfirmuar që "
        "të katër faqet ngarkohen saktë, filtrat e faqes Transactions funksionojnë (all / flagged / fraud), "
        "dhe faqja Analyze kthen një parashikim koherent për transaksione të ndryshme të zgjedhura. Së "
        "dyti, u p\u00ebrdor Playwright (një librari automatizimi shfletuesish) për të kap sistematikisht "
        "pamje të ekranit (screenshots) të të gjitha faqeve në një mjedis të kontrolluar (1440×900 px), duke "
        "p\u00ebrshirë rastin e një transaksioni të vler\u00ebsuar konkretisht (Fig. 7.5), që sh\u00ebrben si dëshmi që "
        "pipeline-i i plotë — nga të dhënat te modeli, te ndërfaqja — funksionon nga fundi në fund (end-"
        "to-end)."
    )

    doc.add_page_break()

    # =========================================================
    # KAPITULLI VIII
    # =========================================================
    h(doc, "KAPITULLI VIII", level=1)
    h(doc, "8. Konkluzione", level=1)
    para(doc,
        "Ky punim adresoi pyetjen kryesore kërkimore të propozuar në fillim të projektit: si mund të "
        "p\u00ebrdoren algoritmet e mësimit makinerik për të identifikuar transaksionet e dyshimta të kartave të "
        "kreditit me saktësi të lartë, duke minimizuar gabimet false positive dhe false negative. Rezultatet "
        f"e paraqitura në Kapitullin VI konfirmojnë Hipotezën Alternative (H1): modelet ML (XGBoost, "
        f"ROC-AUC={R['XGBoost']['roc_auc']*100:.1f}%) tejkalojnë ndjeshëm një qasje bazë lineare (Logistic "
        f"Regression, precision vet\u00ebm {R['Logistic Regression']['precision']*100:.1f}%), duke hedhur poshté "
        "Hipotez\u00ebn Zero (H0)."
    )
    para(doc,
        "Objektivat kryesore të propozimit të temës u p\u00ebrmbush\u00ebn: (1) u p\u00ebrpunuan dhe u analizuan të dhënat "
        f"e {EDA['n_transactions']:,} transaksioneve reale; (2) u nd\u00ebrtuan dhe u testuan katër modele ML; "
        "(3) rezultatet u vizualizuan për interpretim të lehtë (grafikë ROC, precision-recall, rëndësi "
        "veçorish); dhe (4) u zhvillua një aplikacion web funksional për monitorim dhe raportim në kohë "
        "reale."
    )
    para(doc,
        "Kufizime të studimit: dataset-i, edhe pse i njohur dhe gjer\u00ebsisht i p\u00ebrdorur në literaturë, "
        "daton nga 2013 dhe p\u00ebrfaqëson vet\u00ebm transaksione europiane të një periudhe dyditore; veçoritë "
        "V1–V28 të anonimizuara me PCA kufizojnë interpretueshmërinë e biznesit të rezultateve (nuk dihet "
        "saktësisht çfarë p\u00ebrfaq\u00ebson secila veçori); dhe modelet nuk u testuan mbi të dhëna 'live', të "
        "prodhuara në kohë reale, çka mund të ndikojë performancën në prodhim për shkak të 'concept drift' "
        "(ndryshimit të modeleve të mashtrimit me koh\u00ebn)."
    )
    para(doc,
        "Punë e ardhshme e mundshme përfshin: (a) testim mbi dataset më të ri ose lokal për të verifikuar "
        "p\u00ebrgjith\u00ebsueshmërinë; (b) p\u00ebrdorimin e teknikave të shpjegueshmërisë së modelit (SHAP, LIME) për të "
        "ndihmuar analistët e riskut të kuptojnë PSE një transaksion është flaguar; (c) k\u00ebrkim sistematik të "
        "hiperparametrave (GridSearchCV / Bayesian Optimization); dhe (d) vendosje (deployment) reale me "
        "rrjedhë të dhënash në kohë reale (streaming), në vend të një bashk\u00ebsie statike testimi."
    )

    h(doc, "8.1 Referencat", level=2)
    refs = [
        "Bahnsen, A. C., Aouada, D., Stojanovic, A., & Ottersten, B. (2016). Example-dependent "
        "cost-sensitive logistic regression for credit card fraud detection. Expert Systems with "
        "Applications, 42(21), 6609–6619.",
        "Bhattacharyya, S., Jha, S., Tharakunnel, K., & Westland, J. C. (2011). Data mining for credit "
        "card fraud: A comparative study. Decision Support Systems, 50(3), 602–613.",
        "Bolton, R. J., & Hand, D. J. (2002). Statistical fraud detection: A review. Statistical Science, "
        "17(3), 235–255.",
        "Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5–32.",
        "Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic "
        "minority over-sampling technique. Journal of Artificial Intelligence Research, 16, 321–357.",
        "Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. Proceedings of the "
        "22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 785–794.",
        "Dal Pozzolo, A., Boracchi, G., Caelen, O., Alippi, C., & Bontempi, G. (2015). Credit card fraud "
        "detection: A realistic modeling and a novel learning strategy. IEEE Transactions on Neural "
        "Networks and Learning Systems, 29(8), 3784–3797.",
        "Dal Pozzolo, A., Caelen, O., Le Borgne, Y.-A., Waterschoot, S., & Bontempi, G. (2014). Learned "
        "lessons in credit card fraud detection from a practitioner perspective. Expert Systems with "
        "Applications, 41(10), 4915–4928.",
        "Duman, E., & Ozcelik, M. H. (2011). Detecting credit card fraud by genetic algorithm and "
        "scatter search. Expert Systems with Applications, 38(10), 13057–13063.",
        "Ghosh, S., & Reilly, D. L. (1994). Credit card fraud detection with a neural-network. "
        "Proceedings of the 27th Hawaii International Conference on System Sciences, 3, 621–630.",
        "Jurgovsky, J., Granitzer, M., Ziegler, K., Calabretto, S., Portier, P.-E., He-Guelton, L., & "
        "Caelen, O. (2018). Sequence classification for credit-card fraud detection. Expert Systems "
        "with Applications, 100, 234–245.",
        "Ngai, E. W. T., Hu, Y., Wong, Y. H., Chen, Y., & Sun, X. (2011). The application of data mining "
        "techniques in financial fraud detection: A classification framework and an academic review of "
        "literature. Decision Support Systems, 50(3), 559–569.",
        "Phua, C., Lee, V., Smith, K., & Gayler, R. (2010). A comprehensive survey of data mining-based "
        "fraud detection research. Artificial Intelligence Review, 34(1), 1–14.",
        "Sahin, Y., & Duman, E. (2011). Detecting credit card fraud by decision trees and support "
        "vector machines. Proceedings of the International MultiConference of Engineers and Computer "
        "Scientists, 1, 442–447.",
        "Van Vlasselaer, V., Bravo, C., Caelen, O., Eliassi-Rad, T., Akoglu, L., Snoeck, M., & Baesens, "
        "B. (2015). APATE: A novel approach for automated credit card transaction fraud detection using "
        "network-based extensions. Decision Support Systems, 75, 38–48.",
        "Whitrow, C., Hand, D. J., Juszczak, P., Weston, D., & Adams, N. M. (2009). Transaction "
        "aggregation as a strategy for credit card fraud detection. Data Mining and Knowledge Discovery, "
        "18, 30–55.",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)

    doc.save(OUT)
    print("Saved:", OUT)


if __name__ == "__main__":
    main()
