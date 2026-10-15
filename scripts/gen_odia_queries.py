#!/usr/bin/env python3
"""Generate the 100 labelled Odia queries benchmark dataset (Design v2 Section 11 & 12).

Accurately aligned to the actual SAARTHI curriculum pack (NCERT Class 9 Science):
- ch001: Matter in Our Surroundings (c0001 States of Matter, c0002 Density, c0003 Changes of State)
- ch002: Motion (c0004 Motion and Displacement, c0005 Speed and Velocity, c0006 Acceleration)
- ch003: Tissues (c0007 Tissues and Types, c0008 Plant Tissues, c0009 Animal Tissues)

Queries cover pure Odia, Latin-script Odia, and code-mixed Odia+English.
30% held out for evaluation release gate.
No synthetic human approval metadata.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_FILE = REPO / "tests" / "fixtures" / "odia_queries.jsonl"
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

QUERIES = [
    # =========================================================================
    # Concept c0001: States of Matter (Chapter ch001)
    # =========================================================================
    ("q_001", "ପଦାର୍ଥ କଣ ଏବଂ ଏହାର ମୁଖ୍ୟ ଧର୍ମ କଣ?", ["chunk_ch01_c0001_01"], "c0001", "ch001", "pure_odia"),
    ("q_002", "padartha kana? eha kete prakara?", ["chunk_ch01_c0001_01"], "c0001", "ch001", "latin_odia"),
    ("q_003", "matter ra physical nature kana?", ["chunk_ch01_c0001_01"], "c0001", "ch001", "code_mixed"),
    ("q_004", "କଠିନ, ତରଳ ଓ ଗ୍ୟାସରେ ଆନ୍ତଃକଣିକା ଆକର୍ଷଣ ବଳ କିପରି ଥାଏ?", ["chunk_ch01_c0001_01"], "c0001", "ch001", "pure_odia"),
    ("q_005", "intermolecular force in solids and liquids comparison", ["chunk_ch01_c0001_01"], "c0001", "ch001", "code_mixed"),
    ("q_006", "କଠିନ ପଦାର୍ଥର ଏକ ନିର୍ଦ୍ଦିଷ୍ଟ ଆକାର ଓ ଆୟତନ ଥାଏ କାହିଁକି?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "pure_odia"),
    ("q_007", "liquids container ra shape dharana kare kahinki?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "code_mixed"),
    ("q_008", "ଗ୍ୟାସୀୟ ପଦାର୍ଥ ସଙ୍କୋଚନଶୀଳ କିପରି ହୁଏ?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "pure_odia"),
    ("q_009", "LPG cylinder re gas compress kari bhariba karana kana?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "latin_odia"),
    ("q_010", "compressibility of gas highest kahinki thae?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "code_mixed"),
    ("q_011", "କଣିକାମାନଙ୍କ ଗତିଜ ଶକ୍ତି ପଦାର୍ଥର ଅବସ୍ଥା ଉପରେ କି ପ୍ରଭାବ ପକାଏ?", ["chunk_ch01_c0001_02"], "c0001", "ch001", "pure_odia"),

    # =========================================================================
    # Concept c0002: Density (Chapter ch001)
    # =========================================================================
    ("q_012", "ଘନତ୍ୱ କାହାକୁ କୁହାଯାଏ ଏବଂ ଏହାର ଏକକ କଣ?", ["chunk_ch01_c0002_01"], "c0002", "ch001", "pure_odia"),
    ("q_013", "ghanatwa ba density ra sutra kana?", ["chunk_ch01_c0002_01"], "c0002", "ch001", "latin_odia"),
    ("q_014", "density = mass / volume SI unit kana?", ["chunk_ch01_c0002_01"], "c0002", "ch001", "code_mixed"),
    ("q_015", "ଲୁହାର ଘନତ୍ୱ କାଠ ତୁଳନାରେ କାହିଁକି ଅଧିକ?", ["chunk_ch01_c0002_01"], "c0002", "ch001", "pure_odia"),
    ("q_016", "water ra density 4 degree Celsius re kete?", ["chunk_ch01_c0002_01"], "c0002", "ch001", "code_mixed"),
    ("q_017", "ଆପେକ୍ଷିକ ଘନତ୍ୱ ବା Relative Density କଣ?", ["chunk_ch01_c0002_02"], "c0002", "ch001", "pure_odia"),
    ("q_018", "apekshika ghanatwa ra unit kete?", ["chunk_ch01_c0002_02"], "c0002", "ch001", "latin_odia"),
    ("q_019", "relative density unitless kahinki hue?", ["chunk_ch01_c0002_02"], "c0002", "ch001", "code_mixed"),
    ("q_020", "ବରଫ ପାଣି ଉପରେ କାହିଁକି ଭାସମାନ ରହେ?", ["chunk_ch01_c0002_02"], "c0002", "ch001", "pure_odia"),
    ("q_021", "ice floats on water karana kana?", ["chunk_ch01_c0002_02"], "c0002", "ch001", "code_mixed"),
    ("q_022", "ଗୋଟିଏ ବସ୍ତୁ ପାଣିରେ ବୁଡ଼ିବା ବା ଭାସିବାର ସର୍ତ୍ତ କଣ?", ["chunk_ch01_c0002_02"], "c0002", "ch001", "pure_odia"),

    # =========================================================================
    # Concept c0003: Changes of State (Chapter ch001)
    # =========================================================================
    ("q_023", "ଗଳନାଙ୍କ ଓ ସ୍ଫୁଟନାଙ୍କ ମଧ୍ୟରେ ପାର୍ଥକ୍ୟ କଣ?", ["chunk_ch01_c0003_01"], "c0003", "ch001", "pure_odia"),
    ("q_024", "melting point and boiling point difference kana?", ["chunk_ch01_c0003_01"], "c0003", "ch001", "code_mixed"),
    ("q_025", "ଗୁପ୍ତତାପ ବା Latent heat କଣ ଏବଂ ଏହାର କାର୍ଯ୍ୟ କଣ?", ["chunk_ch01_c0003_01"], "c0003", "ch001", "pure_odia"),
    ("q_026", "latent heat of fusion mane kana?", ["chunk_ch01_c0003_01"], "c0003", "ch001", "latin_odia"),
    ("q_027", "ice ra melting point Kelvin scale re kete?", ["chunk_ch01_c0003_01"], "c0003", "ch001", "code_mixed"),
    ("q_028", "ଉଦ୍ଧ୍ୱର୍ପାତନ ବା Sublimation କାହାକୁ କୁହାଯାଏ?", ["chunk_ch01_c0003_02"], "c0003", "ch001", "pure_odia"),
    ("q_029", "sublimation ra udaharan dia camphor kipari udi jae", ["chunk_ch01_c0003_02"], "c0003", "ch001", "latin_odia"),
    ("q_030", "ମାଟି ପାତ୍ରରେ ପାଣି ଥଣ୍ଡା ରହେ କାହିଁକି?", ["chunk_ch01_c0003_02"], "c0003", "ch001", "pure_odia"),
    ("q_031", "evaporation cooling effect die kahinki?", ["chunk_ch01_c0003_02"], "c0003", "ch001", "code_mixed"),
    ("q_032", "ଖରାଦିନେ ସୂତା ପୋଷାକ କାହିଁକି ପିନ୍ଧିବା ଉଚିତ?", ["chunk_ch01_c0003_02"], "c0003", "ch001", "pure_odia"),
    ("q_033", "summer re cotton clothes kahinki pindhiba katha?", ["chunk_ch01_c0003_02"], "c0003", "ch001", "code_mixed"),

    # =========================================================================
    # Concept c0004: Motion and Displacement (Chapter ch002)
    # =========================================================================
    ("q_034", "ପ୍ରସଙ୍ଗ ବିନ୍ଦୁ ବା Reference point କାହାକୁ କୁହାଯାଏ?", ["chunk_ch02_c0004_01"], "c0004", "ch002", "pure_odia"),
    ("q_035", "reference point mane kana motion explain kariba pain?", ["chunk_ch02_c0004_01"], "c0004", "ch002", "code_mixed"),
    ("q_036", "ଗୋଟିଏ ବସ୍ତୁ ଏକା ସମୟରେ ସ୍ଥିର ଓ ଗତିଶୀଳ ହୋଇପାରେ କି?", ["chunk_ch02_c0004_01"], "c0004", "ch002", "pure_odia"),
    ("q_037", "sarala raikhika gati ba straight line motion kana?", ["chunk_ch02_c0004_01"], "c0004", "ch002", "latin_odia"),
    ("q_038", "ଦୂରତା ଓ ବିସ୍ଥାପନ ମଧ୍ୟରେ ମୁଖ୍ୟ ପାର୍ଥକ୍ୟ କଣ?", ["chunk_ch02_c0004_02"], "c0004", "ch002", "pure_odia"),
    ("q_039", "distance and displacement difference kana?", ["chunk_ch02_c0004_02"], "c0004", "ch002", "code_mixed"),
    ("q_040", "displacement zero hoi pare ki jetebele distance non zero?", ["chunk_ch02_c0004_02"], "c0004", "ch002", "latin_odia"),
    ("q_041", "ବୃତ୍ତାକାର ପଥରେ ଥରେ ଘୂରି ଆସିଲେ ବିସ୍ଥାପନ କେତେ ହୁଏ?", ["chunk_ch02_c0004_02"], "c0004", "ch002", "pure_odia"),
    ("q_042", "scalar quantity and vector quantity re distance displacement kipari ase?", ["chunk_ch02_c0004_02"], "c0004", "ch002", "code_mixed"),
    ("q_043", "ବିସ୍ଥାପନର ମାନ ଅତିକ୍ରାନ୍ତ ଦୂରତାଠାରୁ ଅଧିକ ହୋଇପାରିବ କି?", ["chunk_ch02_c0004_02"], "c0004", "ch002", "pure_odia"),
    ("q_044", "initial position ru final position shortest distance ku kana kuhanti?", ["chunk_ch02_c0004_02"], "c0004", "ch002", "latin_odia"),

    # =========================================================================
    # Concept c0005: Speed and Velocity (Chapter ch002)
    # =========================================================================
    ("q_045", "ବେଗ ବା Speed କାହାକୁ କୁହାଯାଏ ଏବଂ ଏହାର SI ଏକକ କଣ?", ["chunk_ch02_c0005_01"], "c0005", "ch002", "pure_odia"),
    ("q_046", "speed ra formula o unit kana?", ["chunk_ch02_c0005_01"], "c0005", "ch002", "latin_odia"),
    ("q_047", "average speed kipari calculate kara jae?", ["chunk_ch02_c0005_01"], "c0005", "ch002", "code_mixed"),
    ("q_048", "ଗାଡ଼ିରେ ଥିବା ଓଡୋମିଟର (Odometer) କଣ ମାପିଥାଏ?", ["chunk_ch02_c0005_01"], "c0005", "ch002", "pure_odia"),
    ("q_049", "odometer and speedometer difference kana?", ["chunk_ch02_c0005_01"], "c0005", "ch002", "code_mixed"),
    ("q_050", "ବେଗତା ବା Velocity କାହାକୁ କୁହାଯାଏ?", ["chunk_ch02_c0005_02"], "c0005", "ch002", "pure_odia"),
    ("q_051", "speed and velocity majhire parthakya kana?", ["chunk_ch02_c0005_02"], "c0005", "ch002", "code_mixed"),
    ("q_052", "velocity vector quantity kahinki?", ["chunk_ch02_c0005_02"], "c0005", "ch002", "latin_odia"),
    ("q_053", "ସୁଷମ ବେଗତା ବା Uniform velocity କହିଲେ କଣ ବୁଝାଏ?", ["chunk_ch02_c0005_02"], "c0005", "ch002", "pure_odia"),
    ("q_054", "direction change hele velocity change hue ki?", ["chunk_ch02_c0005_02"], "c0005", "ch002", "code_mixed"),
    ("q_055", "କୌଣସି ବସ୍ତୁର ବେଗ ଥାଇ ମଧ୍ୟ ବେଗତା ଶୂନ ହୋଇପାରେ କି?", ["chunk_ch02_c0005_02"], "c0005", "ch002", "pure_odia"),

    # =========================================================================
    # Concept c0006: Acceleration (Chapter ch002)
    # =========================================================================
    ("q_056", "ତ୍ୱରଣ ବା Acceleration କାହାକୁ କୁହାଯାଏ?", ["chunk_ch02_c0006_01"], "c0006", "ch002", "pure_odia"),
    ("q_057", "acceleration ra formula a = (v - u) / t re u o v kana?", ["chunk_ch02_c0006_01"], "c0006", "ch002", "latin_odia"),
    ("q_058", "acceleration ra SI unit m/s2 kipari asila?", ["chunk_ch02_c0006_01"], "c0006", "ch002", "code_mixed"),
    ("q_059", "ମନ୍ଦନ ବା ଋଣାତ୍ମକ ତ୍ୱରଣ (Retardation) କଣ?", ["chunk_ch02_c0006_01"], "c0006", "ch002", "pure_odia"),
    ("q_060", "negative acceleration ba deceleration ra udaharan", ["chunk_ch02_c0006_01"], "c0006", "ch002", "code_mixed"),
    ("q_061", "ସୁଷମ ତ୍ୱରଣ ବିଶିଷ୍ଟ ଗତିର ତିନୋଟି ସମୀକରଣ କଣ କଣ?", ["chunk_ch02_c0006_02"], "c0006", "ch002", "pure_odia"),
    ("q_062", "three equations of motion v = u + at lekha", ["chunk_ch02_c0006_02"], "c0006", "ch002", "code_mixed"),
    ("q_063", "s = ut + 1/2 at2 sutra re s kana darshae?", ["chunk_ch02_c0006_02"], "c0006", "ch002", "latin_odia"),
    ("q_064", "ତୃତୀୟ ଗତି ସମୀକରଣ v² - u² = 2as ର ବ୍ୟବହାର କଣ?", ["chunk_ch02_c0006_02"], "c0006", "ch002", "pure_odia"),
    ("q_065", "uniform circular motion re acceleration thae ki?", ["chunk_ch02_c0006_02"], "c0006", "ch002", "code_mixed"),
    ("q_066", "ସୁଷମ ବୃତ୍ତାକାର ଗତି ଏକ ତ୍ୱରିତ ଗତି କାହିଁକି?", ["chunk_ch02_c0006_02"], "c0006", "ch002", "pure_odia"),

    # =========================================================================
    # Concept c0007: Tissues and Types (Chapter ch003)
    # =========================================================================
    ("q_067", "ଟିସ୍ୟୁ ବା Tissue କାହାକୁ କୁହାଯାଏ?", ["chunk_ch03_c0007_01"], "c0007", "ch003", "pure_odia"),
    ("q_068", "tissue ra sangya kana biology re?", ["chunk_ch03_c0007_01"], "c0007", "ch003", "latin_odia"),
    ("q_069", "group of cells working together ku tissue kuhanti ki?", ["chunk_ch03_c0007_01"], "c0007", "ch003", "code_mixed"),
    ("q_070", "ବହୁକୋଷୀ ଜୀବମାନଙ୍କ ଶରୀରରେ ଶ୍ରମ ବିଭାଜନ (Division of labour) କିପରି ହୁଏ?", ["chunk_ch03_c0007_01"], "c0007", "ch003", "pure_odia"),
    ("q_071", "division of labour in multicellular organisms mane kana?", ["chunk_ch03_c0007_01"], "c0007", "ch003", "code_mixed"),
    ("q_072", "ଉଦ୍ଭିଦ ଟିସ୍ୟୁ ଓ ପ୍ରାଣୀ ଟିସ୍ୟୁ ମଧ୍ୟରେ ମୁଖ୍ୟ ପାର୍ଥକ୍ୟ କଣ?", ["chunk_ch03_c0007_02"], "c0007", "ch003", "pure_odia"),
    ("q_073", "plant tissue and animal tissue difference kana?", ["chunk_ch03_c0007_02"], "c0007", "ch003", "code_mixed"),
    ("q_074", "plants re dead supportive tissue beshi thae kahinki?", ["chunk_ch03_c0007_02"], "c0007", "ch003", "latin_odia"),
    ("q_075", "ଉଦ୍ଭିଦମାନଙ୍କୁ ସ୍ଥିର ରହିବା ପାଇଁ ଯାନ୍ତ୍ରିକ ଶକ୍ତି କେଉଁ ଟିସ୍ୟୁ ଯୋଗାଏ?", ["chunk_ch03_c0007_02"], "c0007", "ch003", "pure_odia"),
    ("q_076", "animals move karanti boli living tissue beshi darkar ki?", ["chunk_ch03_c0007_02"], "c0007", "ch003", "code_mixed"),
    ("q_077", "ପ୍ରାଣୀମାନଙ୍କ ଶରୀରର କୋଷ ବୃଦ୍ଧି ଉଦ୍ଭିଦଠାରୁ କିପରି ଭିନ୍ନ?", ["chunk_ch03_c0007_02"], "c0007", "ch003", "pure_odia"),

    # =========================================================================
    # Concept c0008: Plant Tissues (Chapter ch003)
    # =========================================================================
    ("q_078", "ଭାଜକ ଟିସ୍ୟୁ ବା Meristematic tissue ର ପ୍ରକାରଭେଦ କଣ?", ["chunk_ch03_c0008_01"], "c0008", "ch003", "pure_odia"),
    ("q_079", "apical meristem and lateral meristem difference kana?", ["chunk_ch03_c0008_01"], "c0008", "ch003", "code_mixed"),
    ("q_080", "bhajaka tissue ra kosa gudika bibhajana hoi paranti ki?", ["chunk_ch03_c0008_01"], "c0008", "ch003", "latin_odia"),
    ("q_081", "ପାରେନକାଇମା, କୋଲେନକାଇମା ଓ ସ୍କ୍ଲେରେନକାଇମା ମଧ୍ୟରେ ପାର୍ଥକ୍ୟ କଣ?", ["chunk_ch03_c0008_01"], "c0008", "ch003", "pure_odia"),
    ("q_082", "parenchyma, collenchyma and sclerenchyma functions", ["chunk_ch03_c0008_01"], "c0008", "ch003", "code_mixed"),
    ("q_083", "ଜଟିଳ ସ୍ଥାୟୀ ଟିସ୍ୟୁ କାହାକୁ କୁହାଯାଏ?", ["chunk_ch03_c0008_02"], "c0008", "ch003", "pure_odia"),
    ("q_084", "xylem and phloem majhire parthakya kana?", ["chunk_ch03_c0008_02"], "c0008", "ch003", "code_mixed"),
    ("q_085", "xylem pani paribahana kare o phloem khadya paribahana kare ki?", ["chunk_ch03_c0008_02"], "c0008", "ch003", "latin_odia"),
    ("q_086", "ଜାଇଲେମର ଚାରୋଟି ମୁଖ୍ୟ ଉପାଦାନ କଣ କଣ?", ["chunk_ch03_c0008_02"], "c0008", "ch003", "pure_odia"),
    ("q_087", "phloem components sieve tube and companion cells function", ["chunk_ch03_c0008_02"], "c0008", "ch003", "code_mixed"),
    ("q_088", "ଉଦ୍ଭିଦରେ ଜଳ ଓ ଖଣିଜ ଲବଣ ପରିବହନ କିପରି ହୁଏ?", ["chunk_ch03_c0008_02"], "c0008", "ch003", "pure_odia"),

    # =========================================================================
    # Concept c0009: Animal Tissues (Chapter ch003)
    # =========================================================================
    ("q_089", "ପ୍ରାଣୀମାନଙ୍କ ଶରୀରରେ ଥିବା ଚାରି ପ୍ରକାରର ଟିସ୍ୟୁ କଣ କଣ?", ["chunk_ch03_c0009_01"], "c0009", "ch003", "pure_odia"),
    ("q_090", "epithelial tissue ba abarani tissue ra karjya kana?", ["chunk_ch03_c0009_01"], "c0009", "ch003", "latin_odia"),
    ("q_091", "types of epithelial tissue squamous cuboidal columnar", ["chunk_ch03_c0009_01"], "c0009", "ch003", "code_mixed"),
    ("q_092", "ରକ୍ତକୁ ଏକ ସଂଯୋଜକ ଟିସ୍ୟୁ କାହିଁକି କୁହାଯାଏ?", ["chunk_ch03_c0009_01"], "c0009", "ch003", "pure_odia"),
    ("q_093", "blood connective tissue kahinki fluid matrix plasma", ["chunk_ch03_c0009_01"], "c0009", "ch003", "code_mixed"),
    ("q_094", "bone o cartilage majhire parthakya kana?", ["chunk_ch03_c0009_01"], "c0009", "ch003", "latin_odia"),
    ("q_095", "ପେଶୀ ଟିସ୍ୟୁର ମୁଖ୍ୟ ପ୍ରକାରଭେଦ ଏବଂ କାର୍ଯ୍ୟ କଣ?", ["chunk_ch03_c0009_02"], "c0009", "ch003", "pure_odia"),
    ("q_096", "striated, unstriated and cardiac muscle parthakya", ["chunk_ch03_c0009_02"], "c0009", "ch003", "code_mixed"),
    ("q_097", "ହୃଦ୍ ପେଶୀ ବା Cardiac muscle ର ବିଶେଷତ୍ୱ କଣ?", ["chunk_ch03_c0009_02"], "c0009", "ch003", "pure_odia"),
    ("q_098", "snayu tissue ba nervous tissue ra ekaka kana?", ["chunk_ch03_c0009_02"], "c0009", "ch003", "latin_odia"),
    ("q_099", "neuron structure axon dendrite function kana?", ["chunk_ch03_c0009_02"], "c0009", "ch003", "code_mixed"),
    ("q_100", "ସ୍ନାୟୁକୋଷ ବା Neuron ର ଗଠନ ଓ କାର୍ଯ୍ୟ ବର୍ଣ୍ଣନା କର", ["chunk_ch03_c0009_02"], "c0009", "ch003", "pure_odia"),
]


def main():
    lines = []
    # Hold out 30 queries for held-out evaluation gate (Section 15)
    held_out_indices = {i for i in range(1, 101) if i % 10 in (3, 6, 9)}  # exactly 30 queries
    for i, (qid, text, chunks, cid, chid, cat) in enumerate(QUERIES, 1):
        split = "held_out" if (i in held_out_indices) else "tuning"
        entry = {
            "query_id": qid,
            "query_text": text,
            "expected_chunk_ids": chunks,
            "target_concept_id": cid,
            "chapter_id": chid,
            "category": cat,
            "split": split,
            "reviewer": None,
            "review_status": "PENDING_INDEPENDENT_HUMAN_REVIEW",
            "review_date": None,
        }
        lines.append(json.dumps(entry, ensure_ascii=False))

    OUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ Generated {len(lines)} labeled Odia benchmark queries at {OUT_FILE} ({len(held_out_indices)} held-out)")


if __name__ == "__main__":
    main()
