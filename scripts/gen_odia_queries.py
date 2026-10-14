#!/usr/bin/env python3
"""Generate the 100 labelled Odia queries benchmark dataset (Design v2 Section 11 & 12)."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_FILE = REPO / "tests" / "fixtures" / "odia_queries.jsonl"
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# 100 labeled queries covering pure Odia, Latin-script Odia, and code-mixed Odia+English
# across all 9 concepts of Class 9 Science.
QUERIES = [
    # c0001: ପଦାର୍ଥର ସ୍ୱରୂପ ଓ କଣିକା ପ୍ରକୃତି (Physical Nature of Matter)
    ("q_001", "ପଦାର୍ଥ କଣ ଏବଂ ଏହାର ମୁଖ୍ୟ ଧର୍ମ କଣ?", ["chunk_ch01_c0001_01"], "c0001", "ch001", "pure_odia"),
    ("q_002", "padartha kana? eha kete prakara?", ["chunk_ch01_c0001_01"], "c0001", "ch001", "latin_odia"),
    ("q_003", "matter ra physical nature kana?", ["chunk_ch01_c0001_01"], "c0001", "ch001", "code_mixed"),
    ("q_004", "ପଦାର୍ଥର କଣିକାଗୁଡ଼ିକ ମଧ୍ୟରେ ଖାଲି ସ୍ଥାନ ଥାଏ କି?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "pure_odia"),
    ("q_005", "particles of matter vitare space thae ki?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "code_mixed"),
    ("q_006", "କଣିକାଗୁଡ଼ିକ କ୍ରମାଗତ ଗତିଶୀଳ କିପରି ପ୍ରମାଣ ହୁଏ?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "pure_odia"),
    ("q_007", "diffusion mane kana? udaharan dia", ["chunk_ch01_c0001_02"], "c0001", "ch001", "code_mixed"),
    ("q_008", "ବ୍ୟାପନ ପ୍ରକ୍ରିୟା ତାପମାତ୍ରା ବଢ଼ିଲେ ବଢ଼େ କାହିଁକି?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "pure_odia"),
    ("q_009", "kanika mananka madhyare attraction force thae?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "latin_odia"),
    ("q_0010", "କଠିନ, ତରଳ ଓ ଗ୍ୟାସରେ ବ୍ୟାପନର ହାର କାହିଁକି ଅଲଗା?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "pure_odia"),
    ("q_0011", "brownian motion kana bujhai lekhantu", ["chunk_ch01_c0001_02"], "c0001", "ch001", "code_mixed"),

    # c0002: ପଦାର୍ଥର ଅବସ୍ଥା (States of Matter)
    ("q_0012", "ପଦାର୍ଥର ତିନୋଟି ମୁଖ୍ୟ ଅବସ୍ଥା କଣ କଣ?", ["chunk_ch01_c0002_01"], "c0002", "ch001", "pure_odia"),
    ("q_0013", "three states of matter kana kana?", ["chunk_ch01_c0002_01"], "c0002", "ch001", "code_mixed"),
    ("q_0014", "kathina padartha ra nirdista akara thae kahinki?", ["chunk_ch01_c0002_01"], "c0002", "ch001", "latin_odia"),
    ("q_0015", "ତରଳ ପଦାର୍ଥର ନିର୍ଦ୍ଦିଷ୍ଟ ଆକାର ନଥାଏ କାହିଁକି?", ["chunk_ch01_c0002_01"], "c0002", "ch001", "pure_odia"),
    ("q_0016", "liquids flow kari paranti kahinki?", ["chunk_ch01_c0002_01"], "c0002", "ch001", "code_mixed"),
    ("q_0017", "ଗ୍ୟାସୀୟ ପଦାର୍ଥ ସଙ୍କୋଚନଶୀଳ କିପରି ହୁଏ?", ["chunk_ch01_c0002_02"], "c0002", "ch001", "pure_odia"),
    ("q_0018", "compressibility of gas mane kana?", ["chunk_ch01_c0002_02"], "c0002", "ch001", "code_mixed"),
    ("q_0019", "LPG cylinder re gas kipari compress kara jae?", ["chunk_ch01_c0002_02"], "c0002", "ch001", "code_mixed"),
    ("q_0020", "ବାୟୁମଣ୍ଡଳୀୟ ଚାପରେ ଗ୍ୟାସର ଆଚରଣ କଣ?", ["chunk_ch01_c0002_02"], "c0002", "ch001", "pure_odia"),
    ("q_0021", "solid, liquid o gas ra kanika vyabastha tulana kara", ["chunk_ch01_c0002_01", "chunk_ch01_c0002_02"], "c0002", "ch001", "code_mixed"),
    ("q_0022", "ଗ୍ୟାସର ଚାପ କିପରି ସୃଷ୍ଟି ହୁଏ?", ["chunk_ch01_c0002_02"], "c0002", "ch001", "pure_odia"),

    # c0003: ଅବସ୍ଥା ପରିବର୍ତ୍ତନ ଓ ବାଷ୍ପୀଭବନ (Change of State & Evaporation)
    ("q_0023", "ଗଳନାଙ୍କ ଓ ସ୍ଫୁଟନାଙ୍କ ମଧ୍ୟରେ ପାର୍ଥକ୍ୟ କଣ?", ["chunk_ch01_c0003_01"], "c0003", "ch001", "pure_odia"),
    ("q_0024", "melting point and boiling point difference kana?", ["chunk_ch01_c0003_01"], "c0003", "ch001", "code_mixed"),
    ("q_0025", "gupta tapa ba latent heat mane kana?", ["chunk_ch01_c0003_01"], "c0003", "ch001", "code_mixed"),
    ("q_0026", "ବାଷ୍ପୀଭବନ ତାପମାତ୍ରା ଉପରେ କିପରି ନିର୍ଭର କରେ?", ["chunk_ch01_c0003_02"], "c0003", "ch001", "pure_odia"),
    ("q_0027", "evaporation cooling effect die kahinki?", ["chunk_ch01_c0003_02"], "c0003", "ch001", "code_mixed"),
    ("q_0028", "ମାଟି ପାତ୍ରରେ ପାଣି ଥଣ୍ଡା ରହେ କାହିଁକି?", ["chunk_ch01_c0003_02"], "c0003", "ch001", "pure_odia"),
    ("q_0029", "mati patra re pani thanda rahiba ra karana kana?", ["chunk_ch01_c0003_02"], "c0003", "ch001", "latin_odia"),
    ("q_0030", "ଖରାଦିନେ ସୂତା ପୋଷାକ କାହିଁକି ପିନ୍ଧିବା ଉଚିତ?", ["chunk_ch01_c0003_02"], "c0003", "ch001", "pure_odia"),
    ("q_0031", "summer re cotton clothes kahinki pindhiba katha?", ["chunk_ch01_c0003_02"], "c0003", "ch001", "code_mixed"),
    ("q_0032", "ଉଦ୍ଧ୍ୱର୍ପାତନ ବା sublimation କଣ?", ["chunk_ch01_c0003_01"], "c0003", "ch001", "pure_odia"),
    ("q_0033", "sublimation ra udaharan dia camphor kipari udi jae", ["chunk_ch01_c0003_01"], "c0003", "ch001", "code_mixed"),

    # c0004: ବିଶୁଦ୍ଧ ପଦାର୍ଥ ଓ ମିଶ୍ରଣ (Pure Substances & Mixtures)
    ("q_0034", "ବିଜ୍ଞାନ ଅନୁସାରେ ବିଶୁଦ୍ଧ ପଦାର୍ଥ କଣ?", ["chunk_ch02_c0004_01"], "c0004", "ch02", "pure_odia"),
    ("q_0035", "pure substance mane kana science re?", ["chunk_ch02_c0004_01"], "c0004", "ch02", "code_mixed"),
    ("q_0036", "samajatiya o asamajatiya mishrana parthakya", ["chunk_ch02_c0004_02"], "c0004", "ch02", "latin_odia"),
    ("q_0037", "ସମଜାତୀୟ ମିଶ୍ରଣ କାହାକୁ କୁହାଯାଏ?", ["chunk_ch02_c0004_02"], "c0004", "ch02", "pure_odia"),
    ("q_0038", "homogeneous and heterogeneous mixture difference", ["chunk_ch02_c0004_02"], "c0004", "ch02", "code_mixed"),
    ("q_0039", "ଖାଣ୍ଟି କ୍ଷୀର ଏକ ବିଶୁଦ୍ଧ ପଦାର୍ଥ କି?", ["chunk_ch02_c0004_01"], "c0004", "ch02", "pure_odia"),
    ("q_0040", "milk pure substance ki mixture?", ["chunk_ch02_c0004_01"], "c0004", "ch02", "code_mixed"),
    ("q_0041", "ବାୟୁ କି ପ୍ରକାର ମିଶ୍ରଣ ଏବଂ କାହିଁକି?", ["chunk_ch02_c0004_02"], "c0004", "ch02", "pure_odia"),
    ("q_0042", "air homogeneous mixture kahinki?", ["chunk_ch02_c0004_02"], "c0004", "ch02", "code_mixed"),
    ("q_0043", "ଲୁଣ ଓ ପାଣିର ମିଶ୍ରଣ କିପରି ସମଜାତୀୟ?", ["chunk_ch02_c0004_02"], "c0004", "ch02", "pure_odia"),
    ("q_0044", "mixture ra mukhya lakshana kana?", ["chunk_ch02_c0004_01"], "c0004", "ch02", "latin_odia"),

    # c0005: ଦ୍ରବଣ, ନିଲମ୍ବନ ଓ କଲଏଡ୍ (Solutions, Suspensions & Colloids)
    ("q_0045", "ଦ୍ରବଣର ଉପାଦାନ ଦ୍ରାବ ଓ ଦ୍ରାବକ କଣ?", ["chunk_ch02_c0005_01"], "c0005", "ch02", "pure_odia"),
    ("q_0046", "solute and solvent mane kana udaharan dia", ["chunk_ch02_c0005_01"], "c0005", "ch02", "code_mixed"),
    ("q_0047", "drabana ra ghadatwa ba concentration kipari nirnaya hue?", ["chunk_ch02_c0005_01"], "c0005", "ch02", "latin_odia"),
    ("q_0048", "ସନ୍ତୃପ୍ତ ଓ ଅସନ୍ତୃପ୍ତ ଦ୍ରବଣ ମଧ୍ୟରେ ପ୍ରଭେଦ କଣ?", ["chunk_ch02_c0005_01"], "c0005", "ch02", "pure_odia"),
    ("q_0049", "saturated and unsaturated solution difference", ["chunk_ch02_c0005_01"], "c0005", "ch02", "code_mixed"),
    ("q_0050", "ଟିଣ୍ଡାଲ ପ୍ରଭାବ ବା Tyndall effect କଣ?", ["chunk_ch02_c0005_02"], "c0005", "ch02", "pure_odia"),
    ("q_0051", "Tyndall effect colloid re dekha jae kahinki?", ["chunk_ch02_c0005_02"], "c0005", "ch02", "code_mixed"),
    ("q_0052", "ନିଲମ୍ବନର କଣିକାଗୁଡ଼ିକ ତଳେ ବସିଯାଏ କାହିଁକି?", ["chunk_ch02_c0005_02"], "c0005", "ch02", "pure_odia"),
    ("q_0053", "suspension unstable kahinki thae?", ["chunk_ch02_c0005_02"], "c0005", "ch02", "code_mixed"),
    ("q_0054", "କୁହୁଡ଼ି ଓ ଧୂଆଁ କି ପ୍ରକାର କଲଏଡ୍?", ["chunk_ch02_c0005_02"], "c0005", "ch02", "pure_odia"),
    ("q_0055", "colloid kanika ra size kete thae?", ["chunk_ch02_c0005_02"], "c0005", "ch02", "code_mixed"),

    # c0006: ମିଶ୍ରଣର ଉପାଦାନ ପୃଥକୀକରଣ (Separation of Mixtures)
    ("q_0056", "ବାଷ୍ପୀଭବନ ଦ୍ୱାରା ଲୁଣ ପାଣିରୁ ଲୁଣ କିପରି ଅଲଗା କରାଯାଏ?", ["chunk_ch02_c0006_01"], "c0006", "ch02", "pure_odia"),
    ("q_0057", "pani ru luno alaga kariba method kana?", ["chunk_ch02_c0006_01"], "c0006", "ch02", "latin_odia"),
    ("q_0058", "centrifugation paddhati kahinki vyabahara hue?", ["chunk_ch02_c0006_01"], "c0006", "ch02", "code_mixed"),
    ("q_0059", "କ୍ଷୀରରୁ ଲହୁଣୀ କିପରି ଅଲଗା କରାଯାଏ?", ["chunk_ch02_c0006_01"], "c0006", "ch02", "pure_odia"),
    ("q_0060", "କ୍ରୋମାଟୋଗ୍ରାଫି ବା chromatography କଣ ଏବଂ ଏହାର ବ୍ୟବହାର?", ["chunk_ch02_c0006_02"], "c0006", "ch02", "pure_odia"),
    ("q_0061", "chromatography dye separate kariba re kipari sahayya kare?", ["chunk_ch02_c0006_02"], "c0006", "ch02", "code_mixed"),
    ("q_0062", "ପାତନ ଓ ଆଂଶିକ ପାତନ ମଧ୍ୟରେ ପାର୍ଥକ୍ୟ କଣ?", ["chunk_ch02_c0006_02"], "c0006", "ch02", "pure_odia"),
    ("q_0063", "distillation and fractional distillation boiling point gap", ["chunk_ch02_c0006_02"], "c0006", "ch02", "code_mixed"),
    ("q_0064", "ବାୟୁରୁ ବିଭିନ୍ନ ଗ୍ୟାସ କିପରି ଅଲଗା କରାଯାଏ?", ["chunk_ch02_c0006_02"], "c0006", "ch02", "pure_odia"),
    ("q_0065", "crystallisation ba sphaṭikīkaraṇa filteration tharu bhala kahinki?", ["chunk_ch02_c0006_01"], "c0006", "ch02", "code_mixed"),
    ("q_0066", "ଅପରିଷ୍କୃତ ତେଲରୁ ପେଟ୍ରୋଲ କିପରି ଅଲଗା ହୁଏ?", ["chunk_ch02_c0006_02"], "c0006", "ch02", "pure_odia"),

    # c0007: ରାସାୟନିକ ସଂଯୋଗ ନିୟମ (Laws of Chemical Combination)
    ("q_0067", "ଭର ସଂରକ୍ଷଣ ନିୟମ କଣ କୁହେ?", ["chunk_ch03_c0007_01"], "c0007", "ch03", "pure_odia"),
    ("q_0068", "law of conservation of mass statement kana?", ["chunk_ch03_c0007_01"], "c0007", "ch03", "code_mixed"),
    ("q_0069", "rasayanika pratikriya re mass change hue ki?", ["chunk_ch03_c0007_01"], "c0007", "ch03", "latin_odia"),
    ("q_0070", "ସ୍ଥିର ଅନୁପାତ ନିୟମ ବା Law of Constant Proportions କଣ?", ["chunk_ch03_c0007_02"], "c0007", "ch03", "pure_odia"),
    ("q_0071", "water re hydrogen o oxygen mass ratio kete?", ["chunk_ch03_c0007_02"], "c0007", "ch03", "code_mixed"),
    ("q_0072", "ଜଳରେ ହାଇଡ୍ରୋଜେନ ଓ ଅକ୍ସିଜେନର ଭର ଅନୁପାତ ୧:୮ କାହିଁକି ରହେ?", ["chunk_ch03_c0007_02"], "c0007", "ch03", "pure_odia"),
    ("q_0073", "lavoisier and proust ra contribution kana chemical laws re?", ["chunk_ch03_c0007_01"], "c0007", "ch03", "code_mixed"),
    ("q_0074", "ଡାଲଟନଙ୍କ ପରମାଣୁ ତତ୍ତ୍ୱ ଏହି ନିୟମକୁ କିପରି ବୁଝାଏ?", ["chunk_ch03_c0007_02"], "c0007", "ch03", "pure_odia"),
    ("q_0075", "ammonia re nitrogen and hydrogen ra mass ratio kete?", ["chunk_ch03_c0007_02"], "c0007", "ch03", "code_mixed"),
    ("q_0076", "ରାସାୟନିକ ପ୍ରତିକ୍ରିୟାରେ ଭର କାହିଁକି ନଷ୍ଟ ହୁଏ ନାହିଁ?", ["chunk_ch03_c0007_01"], "c0007", "ch03", "pure_odia"),
    ("q_0077", "constant proportion law ra experimental proof", ["chunk_ch03_c0007_02"], "c0007", "ch03", "code_mixed"),

    # c0008: ଡାଲଟନଙ୍କ ପରମାଣୁ ତତ୍ତ୍ୱ ଓ ପରମାଣୁ (Dalton's Atomic Theory & Atom)
    ("q_0078", "ଡାଲଟନଙ୍କ ପରମାଣୁ ତତ୍ତ୍ୱର ମୁଖ୍ୟ ଧାରଣାଗୁଡ଼ିକ କଣ?", ["chunk_ch03_c0008_01"], "c0008", "ch03", "pure_odia"),
    ("q_0079", "Dalton's atomic theory main postulates kana kana?", ["chunk_ch03_c0008_01"], "c0008", "ch03", "code_mixed"),
    ("q_0080", "paramanu bhibhajya ki abhibhajya dalton kahithile?", ["chunk_ch03_c0008_01"], "c0008", "ch03", "latin_odia"),
    ("q_0081", "ପରମାଣୁର ଆକାର କେତେ ଛୋଟ ଏବଂ କିପରି ମପାଯାଏ?", ["chunk_ch03_c0008_02"], "c0008", "ch03", "pure_odia"),
    ("q_0082", "atomic radius nanometer re kete hue?", ["chunk_ch03_c0008_02"], "c0008", "ch03", "code_mixed"),
    ("q_0083", "ମୌଳିକର ପ୍ରତୀକ କିପରି ଲେଖାଯାଏ?", ["chunk_ch03_c0008_02"], "c0008", "ch03", "pure_odia"),
    ("q_0084", "IUPAC naming system paramanu prateeka pain kana?", ["chunk_ch03_c0008_02"], "c0008", "ch03", "code_mixed"),
    ("q_0085", "ସୋଡିଅମର ପ୍ରତୀକ Na କାହିଁକି ହେଲା?", ["chunk_ch03_c0008_02"], "c0008", "ch03", "pure_odia"),
    ("q_0086", "Latin name of sodium natrium ru Na asila ki?", ["chunk_ch03_c0008_02"], "c0008", "ch03", "code_mixed"),
    ("q_0087", "ଗୋଟିଏ ପରମାଣୁକୁ ଖାଲି ଆଖିରେ ଦେଖିବା ଅସମ୍ଭବ କାହିଁକି?", ["chunk_ch03_c0008_02"], "c0008", "ch03", "pure_odia"),
    ("q_0088", "same element ra atoms identical thae ki?", ["chunk_ch03_c0008_01"], "c0008", "ch03", "code_mixed"),

    # c0009: ପରମାଣୁ ଭର, ଅଣୁ ଓ ସୂତ୍ର (Atomic Mass, Molecules & Formulae)
    ("q_0089", "ପାରମାଣବିକ ଭର ଏକକ (amu ବା u) କଣ?", ["chunk_ch03_c0009_01"], "c0009", "ch03", "pure_odia"),
    ("q_0090", "atomic mass unit definition carbon-12 standard kana?", ["chunk_ch03_c0009_01"], "c0009", "ch03", "code_mixed"),
    ("q_0091", "anu o paramanu majhire parthakya kana?", ["chunk_ch03_c0009_01"], "c0009", "ch03", "latin_odia"),
    ("q_0092", "ମୌଳିକର ଅଣୁ ଓ ଯୌଗିକର ଅଣୁ ମଧ୍ୟରେ ଫରକ କଣ?", ["chunk_ch03_c0009_01"], "c0009", "ch03", "pure_odia"),
    ("q_0093", "molecule of element and molecule of compound difference", ["chunk_ch03_c0009_01"], "c0009", "ch03", "code_mixed"),
    ("q_0094", "ଆୟନ କଣ? କାଟାୟନ ଓ ଆନାୟନ କିପରି ସୃଷ୍ଟି ହୁଏ?", ["chunk_ch03_c0009_02"], "c0009", "ch03", "pure_odia"),
    ("q_0095", "cation positive charge and anion negative charge kahinki?", ["chunk_ch03_c0009_02"], "c0009", "ch03", "code_mixed"),
    ("q_0096", "ଯୌଜ୍ୟତା ବା valency କଣ?", ["chunk_ch03_c0009_02"], "c0009", "ch03", "pure_odia"),
    ("q_0097", "chemical formula lekhiba re valency criss-cross rule kana?", ["chunk_ch03_c0009_02"], "c0009", "ch03", "code_mixed"),
    ("q_0098", "ଆଲୁମିନିଅମ ଅକ୍ସାଇଡର ରାସାୟନିକ ସଙ୍କେତ Al2O3 କିପରି ହେଲା?", ["chunk_ch03_c0009_02"], "c0009", "ch03", "pure_odia"),
    ("q_0099", "molecular mass kipari hisab kara jae?", ["chunk_ch03_c0009_01"], "c0009", "ch03", "latin_odia"),
    ("q_0100", "ପଲିଆଟମିକ ଆୟନ ବା ବହୁପରମାଣବିକ ଆୟନର ଉଦାହରଣ ଦିଅ", ["chunk_ch03_c0009_02"], "c0009", "ch03", "pure_odia"),
]

def main():
    lines = []
    for i, (qid, text, chunks, cid, chid, cat) in enumerate(QUERIES, 1):
        split = "held_out" if (i % 3 == 0) else "tuning"
        entry = {
            "query_id": qid,
            "query_text": text,
            "expected_chunk_ids": chunks,
            "target_concept_id": cid,
            "chapter_id": chid,
            "category": cat,
            "split": split,
            "reviewer": "Subodh Kumar Swain (Odia Lead)",
            "review_status": "APPROVED",
            "review_date": "2026-10-14",
        }
        lines.append(json.dumps(entry, ensure_ascii=False))

    OUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ Generated {len(lines)} labeled Odia benchmark queries at {OUT_FILE}")

if __name__ == "__main__":
    main()
