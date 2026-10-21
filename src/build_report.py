"""
Builds 'Diplome_Materiale_Teknike_Kapitujt_4-8.docx' — a technical reference
document (NOT a finished thesis) containing the methodology, architecture,
real results, and screenshots produced by this project, organized by the
chapter they support. Gresa writes the actual thesis prose herself from this
material, in her own words.
"""
import json
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PLOTS = ROOT / "outputs" / "plots"
SHOTS = ROOT / "outputs" / "screenshots"
OUT = ROOT / "Diplome_Materiale_Teknike_Kapitujt_4-8.docx"

with open(ROOT / "outputs" / "evaluation_results.json") as f:
    RESULTS = json.load(f)
with open(ROOT / "outputs" / "eda_summary.json") as f:
    EDA = json.load(f)
with open(ROOT / "models" / "training_timings.json") as f:
    TIMINGS = json.load(f)

DOC_WIDTH_IN = 6.5
BRAND = RGBColor(0x1F, 0x4E, 0x8C)


def add_img(doc, path, caption, max_width=DOC_WIDTH_IN):
    im = Image.open(path)
    w, h = im.size
    width_in = max_width
    doc.add_picture(str(path), width=Inches(width_in))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph()
    run = cap.add_run(caption)
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x60, 0x60, 0x60)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(12)


def heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = BRAND
    return h


def note_box(doc, text):
    p = doc.add_paragraph()
    run = p.add_run("Note: " + text)
    run.italic = True
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x8A, 0x4B, 0x08)
    p.paragraph_format.space_after = Pt(10)


def add_metrics_table(doc):
    table = doc.add_table(rows=1, cols=8)
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    headers = ["Model", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "False Pos.", "False Neg."]
    for c, text in zip(hdr, headers):
        c.text = text
        for p in c.paragraphs:
            for r in p.runs:
                r.bold = True
    for name, m in RESULTS.items():
        row = table.add_row().cells
        row[0].text = name
        row[1].text = f"{m['accuracy']*100:.2f}%"
        row[2].text = f"{m['precision']*100:.2f}%"
        row[3].text = f"{m['recall']*100:.2f}%"
        row[4].text = f"{m['f1_score']*100:.2f}%"
        row[5].text = f"{m['roc_auc']*100:.2f}%"
        row[6].text = str(m["false_positives"])
        row[7].text = str(m["false_negatives"])
    doc.add_paragraph()


def main():
    doc = Document()

    # Base font
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # ---------- Title page ----------
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("Materiale Teknike për Kapitujt 4–8")
    r.bold = True
    r.font.size = Pt(22)
    r.font.color.rgb = BRAND

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("Sistemi i Zbulimit të Mashtrimeve me Kartë Krediti duke Përdorur Mësimin Makinerik")
    r.italic = True
    r.font.size = Pt(14)

    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.add_run(
        "\nStudente: Gresa Koshi\nPrograma: Shkenca Kompjuterike\n"
        "Universum International College (powered by Arizona State University)\n"
    )

    note_box(
        doc,
        "Ky dokument NUK është punimi final i diplomës. Ai përmban rezultatet reale, kodin, "
        "metodologjinë dhe pamjet e ekranit (screenshots) të prodhuara nga zbatimi aktual i "
        "projektit, të organizuara sipas kapitujve, si material referimi. Kapitujt 4–8 të "
        "disertacionit duhet të shkruhen nga vetë studentja, me fjalët e saj, duke u bazuar në "
        "këto të dhëna dhe rezultate."
    )
    doc.add_page_break()

    # ---------- Chapter 4 ----------
    heading(doc, "Kapitulli 4 — Metodologjia dhe Analiza e të Dhënave", level=1)

    heading(doc, "4.1 Dataset-i i përdorur", level=2)
    doc.add_paragraph(
        f"Dataset-i: 'Credit Card Fraud Detection' (transaksione anonimizuara të kartave të "
        f"kreditit, Shtator 2013, Evropë), i marrë nga Kaggle. Përmban {EDA['n_transactions']:,} "
        f"transaksione me {EDA['n_features']} veçori (features): Time, V1–V28 (komponentë të "
        f"transformuar me PCA për arsye privatësie), dhe Amount. Etiketa Class tregon nëse "
        f"transaksioni është mashtrues (1) apo legjitim (0)."
    )
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = "Light Grid Accent 1"
    tbl.rows[0].cells[0].text = "Metrikë"
    tbl.rows[0].cells[1].text = "Vlerë"
    rows_data = [
        ("Numri total i transaksioneve", f"{EDA['n_transactions']:,}"),
        ("Transaksione mashtruese", f"{EDA['n_fraud']} ({EDA['fraud_rate_pct']}%)"),
        ("Transaksione legjitime", f"{EDA['n_legit']:,}"),
        ("Shuma mesatare - legjitime", f"{EDA['amount_mean_legit']} $"),
        ("Shuma mesatare - mashtrim", f"{EDA['amount_mean_fraud']} $"),
    ]
    for k, v in rows_data:
        row = tbl.add_row().cells
        row[0].text = k
        row[1].text = v
    doc.add_paragraph()

    heading(doc, "4.2 Analiza eksploruese e të dhënave (EDA)", level=2)
    doc.add_paragraph(
        "Grafikët e mëposhtëm u gjeneruan nga scripti src/eda.py dhe tregojnë pabarazinë ekstreme "
        "të klasave (0.17% mashtrim), shpërndarjen e shumave dhe kohës, dhe strukturën e "
        "korrelacionit ndërmjet veçorive."
    )
    add_img(doc, PLOTS / "01_class_distribution.png", "Fig. 4.1 — Shpërndarja e klasave (shkallë logaritmike)")
    add_img(doc, PLOTS / "02_amount_distribution.png", "Fig. 4.2 — Shpërndarja e shumës së transaksionit sipas klasës")
    add_img(doc, PLOTS / "03_time_distribution.png", "Fig. 4.3 — Frekuenca e transaksioneve sipas orës së ditës")
    add_img(doc, PLOTS / "04_correlation_heatmap.png", "Fig. 4.4 — Matrica e korrelacionit ndërmjet veçorive")
    add_img(doc, PLOTS / "05_top_correlated_features.png", "Fig. 4.5 — 12 veçoritë më të korreluara me mashtrimin")

    heading(doc, "4.3 Përpunimi i të dhënave (Preprocessing)", level=2)
    doc.add_paragraph(
        "Hapat e zbatuar në src/preprocess.py:\n"
        "1. Standardizimi (StandardScaler) i kolonave Amount dhe Time, pasi këto nuk janë "
        "transformuar paraprakisht me PCA si V1–V28.\n"
        "2. Ndarja train/test 80/20 me stratifikim sipas klasës, për të ruajtur proporcionin e "
        "rasteve mashtruese në të dy nën-bashkësitë.\n"
        "3. Balancimi i të dhënave të trajnimit me SMOTE (Synthetic Minority Over-sampling "
        "Technique): nga 227,451 raste legjitime kundrejt vetëm 394 raste mashtruese, në "
        "227,451 kundrejt 227,451 pas balancimit. Kjo teknikë u përmend edhe në propozimin e "
        "temës (Bahnsen et al., 2016) si mënyrë për të adresuar dataset-et e pabarabarta.\n"
        "4. Bashkësia e testimit (56,962 transaksione) MBETET E PABALANCUAR dhe reflekton "
        "shpërndarjen origjinale — kjo është kritike sepse vlerësimi i modelit duhet të bëhet "
        "në kushte reale, jo artificialisht të balancuara."
    )

    doc.add_page_break()

    # ---------- Chapter 5 ----------
    heading(doc, "Kapitulli 5 — Dizajni i Sistemit dhe Implementimi", level=1)

    heading(doc, "5.1 Arkitektura e sistemit", level=2)
    doc.add_paragraph(
        "Sistemi është ndërtuar në Python dhe përbëhet nga katër module kryesore:\n"
        "• src/eda.py — analiza eksploruese e të dhënave dhe gjenerimi i grafikëve.\n"
        "• src/preprocess.py — standardizimi, ndarja train/test, dhe balancimi SMOTE.\n"
        "• src/train.py — trajnimi i 4 modeleve: Logistic Regression (bazë krahasimi), Random "
        "Forest, XGBoost, dhe një Voting Ensemble (kombinim i të treve).\n"
        "• src/evaluate.py — vlerësimi i modeleve dhe gjenerimi i grafikëve të performancës.\n"
        "• webapp/app.py — aplikacioni web (Flask) për monitorim dhe raportim në kohë reale, siç "
        "kërkohej në propozimin e temës."
    )

    heading(doc, "5.2 Algoritmet e Machine Learning", level=2)
    doc.add_paragraph(
        "Tre algoritme klasifikimi u trajnuan dhe u krahasuan, në përputhje me metodologjinë e "
        "propozuar:\n"
        "• Random Forest (200 pemë, thellësi max. 12) — modeli ensemble bazë i sugjeruar në "
        "literaturë (Ngai et al., 2011).\n"
        "• XGBoost (300 estimatorë, learning_rate=0.1) — algoritëm gradient boosting, i njohur "
        "për performancë të lartë në dataset-e të pabarabarta.\n"
        "• Voting Ensemble (soft voting) — kombinon Random Forest, XGBoost dhe Logistic "
        "Regression, siç sugjerohej në propozim ('kombinimi i disa modeleve mund të rrisë "
        "saktësinë e detektimit')."
    )
    times_txt = ", ".join(f"{k.replace('_',' ')}: {v}s" for k, v in TIMINGS.items())
    doc.add_paragraph(f"Kohët e trajnimit (referencë teknike): {times_txt}.")

    heading(doc, "5.3 Aplikacioni Web (Dashboard)", level=2)
    doc.add_paragraph(
        "Aplikacioni web u ndërtua me Flask dhe ka katër faqe kryesore, që plotësojnë kërkesën e "
        "propozimit për 'zhvillimin e një aplikacioni web për monitorim dhe raportim në kohë reale':"
    )
    doc.add_paragraph(
        "• Dashboard — statistika përmbledhëse, metrikat e modelit ensemble, dhe lista e "
        "transaksioneve më të fundit të flaguara si të dyshimta.\n"
        "• Transactions — tabelë e kërkueshme/filtrueshme e transaksioneve me probabilitetin e "
        "mashtrimit dhe nivelin e riskut.\n"
        "• Analyze — zgjedh një transaksion dhe merr parashikim në kohë reale nga modeli "
        "ensemble (probabilitet + klasifikim).\n"
        "• Model Reports — krahasimi i plotë i performancës së katër modeleve me grafikë."
    )

    add_img(doc, SHOTS / "01_dashboard.png", "Fig. 5.1 — Faqja kryesore e dashboard-it")
    add_img(doc, SHOTS / "02_transactions.png", "Fig. 5.2 — Faqja e transaksioneve")
    add_img(doc, SHOTS / "03_transactions_flagged.png", "Fig. 5.3 — Transaksionet e flaguara nga modeli")
    add_img(doc, SHOTS / "04_analyze.png", "Fig. 5.4 — Faqja e analizës së transaksioneve (para vlerësimit)")
    add_img(doc, SHOTS / "06_analyze_result.png", "Fig. 5.5 — Rezultati i vlerësimit në kohë reale për një transaksion")
    add_img(doc, SHOTS / "05_reports.png", "Fig. 5.6 — Faqja e raporteve të modelit")

    doc.add_page_break()

    # ---------- Chapter 6 ----------
    heading(doc, "Kapitulli 6 — Rezultatet dhe Vlerësimi", level=1)

    heading(doc, "6.1 Metrikat e performancës", level=2)
    doc.add_paragraph(
        "Katër modelet u vlerësuan mbi të njëjtën bashkësi testimi (56,962 transaksione, e "
        "pabalancuar, duke reflektuar shpërndarjen reale prej 0.17% mashtrim):"
    )
    add_metrics_table(doc)
    doc.add_paragraph(
        "Vërejtje kyçe për interpretim: Logistic Regression arrin 'accuracy' të lartë (97.4%) por "
        "'precision' shumë të ulët (5.8%) — kjo tregon pse accuracy vetëm ËSHTË METRIKË "
        "MASHTRUESE në dataset-e kaq të pabarabarta (492 raste nga 284,807). XGBoost arrin "
        "balancën më të mirë ndërmjet precision (72.3%) dhe recall (87.8%), duke rezultuar në "
        "F1-score më të lartë (79.3%) dhe numrin më të vogël të gabimeve totale."
    )

    heading(doc, "6.2 Kurbat ROC dhe Precision-Recall", level=2)
    add_img(doc, PLOTS / "06_roc_curves.png", "Fig. 6.1 — Kurbat ROC për të katër modelet")
    add_img(doc, PLOTS / "07_precision_recall_curves.png", "Fig. 6.2 — Kurbat Precision-Recall")

    heading(doc, "6.3 Matricat e konfuzionit", level=2)
    add_img(doc, PLOTS / "08_confusion_matrices.png", "Fig. 6.3 — Matricat e konfuzionit për të katër modelet")

    heading(doc, "6.4 Rëndësia e veçorive (Feature Importance)", level=2)
    add_img(doc, PLOTS / "09_feature_importance.png", "Fig. 6.4 — 10 veçoritë më të rëndësishme (RF dhe XGBoost)")

    heading(doc, "6.5 Krahasimi i modeleve", level=2)
    add_img(doc, PLOTS / "10_metric_comparison.png", "Fig. 6.5 — Krahasimi i metrikave ndërmjet modeleve")

    doc.add_page_break()

    # ---------- Chapter 7 ----------
    heading(doc, "Kapitulli 7 — Diskutimi (shënime pune)", level=1)
    note_box(doc, "Këto janë pika diskutimi bazuar në rezultate reale — zhvilloji në prozë origjinale.")
    doc.add_paragraph(
        "• Lidhja me hipotezat e propozimit: H1 ('modelet ML përmirësojnë ndjeshëm saktësinë "
        f"krahasuar me metodat tradicionale') mbështetet nga rezultatet — XGBoost arrin ROC-AUC "
        f"{RESULTS['XGBoost']['roc_auc']*100:.1f}% dhe F1-score {RESULTS['XGBoost']['f1_score']*100:.1f}%, "
        "shumë mbi atë çfarë do të arrinin pragjet statike tradicionale (p.sh. kufij fiks të shumës).\n"
        "• Trade-off precision/recall: rritja e recall (kapja e më shumë rasteve mashtruese) "
        "zakonisht ul precision-in (më shumë false positives). Në kontekst bankar, false "
        "negative (mashtrim i pazbuluar) zakonisht ka kosto më të lartë se false positive "
        "(alarm i rremë), prandaj modeli me recall më të lartë (Ensemble, 88.8%) mund të "
        "preferohet edhe pse ka precision më të ulët se XGBoost i vetëm.\n"
        "• Kufizime: dataset-i është nga 2013, transaksione evropiane, dhe veçoritë V1–V28 janë "
        "të anonimizuara me PCA — kjo kufizon interpretueshmërinë (nuk dihet çfarë përfaqëson "
        "çdo veçori) dhe mund të mos përfaqësojë modele mashtrimi më të fundit.\n"
        "• Krahasim me literaturën e cituar në propozim: rezultatet konfirmojnë gjetjet e Ngai "
        "et al. (2011) dhe Bahnsen et al. (2016) për efektivitetin e ensemble/gradient-boosting "
        "modeleve dhe rëndësinë e teknikave të balancimit (SMOTE) në dataset-e shumë të "
        "pabarabarta.\n"
        "• Komponenti web plotëson boshllëkun e identifikuar në literaturë (shumica e studimeve "
        "fokusohen vetëm te modeli, jo te vizualizimi/aplikacioni praktik)."
    )

    doc.add_page_break()

    # ---------- Chapter 8 ----------
    heading(doc, "Kapitulli 8 — Përfundimi (shënime pune)", level=1)
    note_box(doc, "Pika kryesore për seksionin e përfundimit — shndërroji në prozë origjinale.")
    doc.add_paragraph(
        "• Projekti arriti të ndërtojë dhe krahasojë me sukses katër modele ML për zbulimin e "
        "mashtrimeve me kartë krediti, duke konfirmuar hipotezën H1.\n"
        "• XGBoost rezultoi modeli individual më i mirë (F1=79.3%, ROC-AUC=98.0%); Ensemble "
        "ofron recall më të lartë (88.8%) me kosto të vogël precision-i.\n"
        "• U zhvillua një aplikacion web funksional (dashboard, monitorim transaksionesh, analizë "
        "në kohë reale, raportim), duke plotësuar plotësisht objektivat e propozimit të temës.\n"
        "• Punë e ardhshme e mundshme: testim mbi dataset më të ri/lokal, shpjegueshmëri e "
        "modelit (SHAP/LIME) për interpretim më të lehtë nga analistët e riskut, vendosje "
        "(deployment) reale me stream të dhënash live, dhe testim A/B i pragjeve të vendimit."
    )

    doc.add_page_break()

    # ---------- Appendix ----------
    heading(doc, "Shtojca — Struktura e Projektit", level=1)
    doc.add_paragraph(
        "projekt/\n"
        "  data/creditcard.csv           - dataset-i origjinal\n"
        "  src/eda.py                    - analiza eksploruese\n"
        "  src/preprocess.py             - standardizim, split, SMOTE\n"
        "  src/train.py                  - trajnimi i modeleve\n"
        "  src/evaluate.py               - vlerësimi dhe grafikët\n"
        "  src/screenshot.py             - kap pamjet e ekranit të dashboard-it\n"
        "  models/                       - modelet e trajnuara (.joblib)\n"
        "  webapp/app.py                 - aplikacioni Flask\n"
        "  webapp/templates/             - faqet HTML (Dashboard, Transactions, Analyze, Reports)\n"
        "  outputs/plots/                - grafikët e EDA dhe vlerësimit\n"
        "  outputs/screenshots/          - pamjet e ekranit të aplikacionit web"
    )
    doc.add_paragraph(
        "Për të ekzekutuar sistemin: python src/eda.py → python src/train.py → "
        "python src/evaluate.py → python webapp/app.py (dashboard në http://127.0.0.1:5057)."
    )

    doc.save(OUT)
    print("Saved:", OUT)


if __name__ == "__main__":
    main()
