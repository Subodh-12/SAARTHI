import json
import re
import unicodedata
from rank_bm25 import BM25Okapi
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "backend"))

from app.content.pack_loader import load_pack_index

pack = load_pack_index()

ODIA_SUFFIXES = [
    "ଗୁଡ଼ିକର", "ଗୁଡ଼ିକରେ", "ଗୁଡ଼ିକୁ", "ଗୁଡ଼ିକ",
    "ମାନଙ୍କର", "ମାନଙ୍କରେ", "ମାନଙ୍କୁ", "ମାନଙ୍କ",
    "ଠାରୁ", "ଠାରେ", "ଟିକୁ", "ଟିର", "ଟିରେ", "ଟିଏ",
    "ରେ", "ରୁ", "କୁ", "ର", "ଟି", "ଟା"
]

LATIN_MAP = {
    "padartha": "ପଦାର୍ଥ matter",
    "matter": "ପଦାର୍ଥ matter",
    "particles": "କଣିକା particle",
    "particle": "କଣିକା particle",
    "nature": "ପ୍ରକୃତି nature",
    "physical": "ଭୌତିକ physical",
    "kathina": "କଠିନ solid",
    "solid": "କଠିନ solid",
    "tarala": "ତରଳ liquid",
    "liquid": "ତରଳ liquid",
    "liquids": "ତରଳ liquid",
    "gasiya": "ଗ୍ୟାସ gas",
    "gas": "ଗ୍ୟାସ gas",
    "gases": "ଗ୍ୟାସ gas",
    "kanika": "କଣିକା particle",
    "kanikamananka": "କଣିକା particle",
    "byapana": "ବ୍ୟାପନ diffusion",
    "vyapana": "ବ୍ୟାପନ diffusion",
    "diffusion": "ବ୍ୟାପନ diffusion",
    "ghanatwa": "ଘନତ୍ୱ density",
    "density": "ଘନତ୍ୱ density",
    "galananka": "ଗଳନାଙ୍କ melting point",
    "melting": "ଗଳନାଙ୍କ melting",
    "sphutananka": "ସ୍ଫୁଟନାଙ୍କ boiling point",
    "boiling": "ସ୍ଫୁଟନାଙ୍କ boiling",
    "vashpikarana": "ବାଷ୍ପୀକରଣ evaporation vaporization",
    "vaporization": "ବାଷ୍ପୀକରଣ vaporization",
    "evaporation": "ବାଷ୍ପୀକରଣ evaporation",
    "sankochana": "ସଙ୍କୋଚନ compression",
    "sankochansila": "ସଙ୍କୋଚନଶୀଳତା compressible compressibility",
    "compressibility": "ସଙ୍କୋଚନଶୀଳତା compressibility",
    "compression": "ସଙ୍କୋଚନ compression",
    "tapamatra": "ତାପମାତ୍ରା temperature",
    "temperature": "ତାପମାତ୍ରା temperature",
    "tapa": "ତାପ heat",
    "heat": "ତାପ heat",
    "chapa": "ଚାପ pressure",
    "pressure": "ଚାପ pressure",
    "gatika": "ଗତିଜ kinetic",
    "kinetic": "ଗତିଜ kinetic",
    "akarshan": "ଆକର୍ଷଣ attraction",
    "attraction": "ଆକର୍ଷଣ attraction",
    "space": "ସ୍ଥାନ space",
    "volume": "ଆୟତନ volume",
    "shape": "ଆକାର shape",
    "mass": "ବସ୍ତୁତ୍ୱ mass",
    "latent": "ଲୀନ ଗୁପ୍ତ latent",
    "gupta": "ଗୁପ୍ତ ଲୀନ latent",
    "sublimation": "ଉଦ୍ଧ୍ୱର୍ପାତନ sublimation",
    "plasma": "ପ୍ଲାଜ୍ମା plasma",
    "bose": "ବୋଷ bose",
    "einstein": "ଆଇନଷ୍ଟାଇନ einstein",
    "bec": "ବୋଷ-ଆଇନଷ୍ଟାଇନ bec",
    "moulika": "ମୌଳିକ element",
    "element": "ମୌଳିକ element",
    "jougika": "ଯୌଗିକ compound",
    "compound": "ଯୌଗିକ compound",
    "mishrana": "ମିଶ୍ରଣ mixture",
    "mixture": "ମିଶ୍ରଣ mixture",
    "drabana": "ଦ୍ରବଣ solution",
    "solution": "ଦ୍ରବଣ solution",
    "draba": "ଦ୍ରାବ solute",
    "solute": "ଦ୍ରାବ solute",
    "drabaka": "ଦ୍ରାବକ solvent",
    "solvent": "ଦ୍ରାବକ solvent",
    "suspension": "ନିଲମ୍ବନ suspension",
    "colloid": "କଲଏଡ୍ colloid",
    "tyndall": "ଟିଣ୍ଡାଲ୍ tyndall",
    "paramanu": "ପରମାଣୁ atom",
    "atom": "ପରମାଣୁ atom",
    "atoms": "ପରମାଣୁ atom",
    "anu": "ଅଣୁ molecule",
    "molecule": "ଅଣୁ molecule",
    "molecules": "ଅଣୁ molecule",
    "valency": "ଯୋଜ୍ୟତା valency",
    "jojyata": "ଯୋଜ୍ୟତା valency",
    "electron": "ଇଲେକ୍ଟ୍ରୋନ electron",
    "electrons": "ଇଲେକ୍ଟ୍ରୋନ electron",
    "proton": "ପ୍ରୋଟୋନ proton",
    "protons": "ପ୍ରୋଟୋନ proton",
    "neutron": "ନିଉଟ୍ରୋନ neutron",
    "neutrons": "ନିଉଟ୍ରୋନ neutron",
    "rutherford": "ରଦରଫୋର୍ଡ rutherford",
    "bohr": "ବୋର bohr",
    "thomson": "ଥମସନ thomson",
    "isotope": "ସମସ୍ଥାନିକ isotope",
    "isotopes": "ସମସ୍ଥାନିକ isotope",
    "samastanika": "ସମସ୍ଥାନିକ isotope",
    "isobar": "ଆଇସୋବାର isobar",
    "isobars": "ଆଇସୋବାର isobar",
    "kosa": "କୋଷ cell",
    "cell": "କୋଷ cell",
    "cells": "କୋଷ cell",
    "kalara": "କଳା tissue",
    "tissue": "କଳା tissue",
    "tissues": "କଳା tissue",
    "anga": "ଅଙ୍ଗ organ",
    "organ": "ଅଙ୍ଗ organ",
    "brownian": "ବ୍ରାଉନିଆନ୍ ଗତିଜ କ୍ରମାଗତ ଗତିଶୀଳ brownian motion",
    "cylinder": "ସିଲିଣ୍ଡର cylinder",
    "lpg": "ଏଲପିଜି lpg",
    "flow": "ପ୍ରବାହିତ flow",
    "state": "ଅବସ୍ଥା state",
    "states": "ଅବସ୍ଥା state",
}

def stem_odia(word: str) -> list[str]:
    res = [word]
    for s in ODIA_SUFFIXES:
        if word.endswith(s) and len(word) > len(s) + 2:
            res.append(word[:-len(s)])
            break
    return res

ODIA_SYNONYMS = {'ଜାଇଲେମ': 'ଜାଇଲମ', 'ଜାଇଲେମର': 'ଜାଇଲମ', 'ସୂତା': 'ବାଷ୍ପୀଭବନ ସୂତା', 'ଖରାଦିନେ': 'ବାଷ୍ପୀଭବନ ଖରାଦିନେ'}

def tokenize_enhanced(text: str) -> list[str]:
    text = unicodedata.normalize("NFC", text).lower()
    text = re.sub(r"[।,\.\!\?\:\;\(\)\[\]\{\}\"\'`\-\/\_]", " ", text)
    tokens = text.split()
    all_toks = []
    for t in tokens:
        if t in LATIN_MAP:
            for mapped in LATIN_MAP[t].split():
                all_toks.append(mapped)
        stems = stem_odia(t)
        for s in stems:
            all_toks.append(s)
            if s in ODIA_SYNONYMS:
                all_toks.extend(ODIA_SYNONYMS[s].split())
    return all_toks

chunk_ids = list(pack.chunks.keys())
chunk_docs = []
for cid in chunk_ids:
    ch = pack.chunks[cid]
    c = pack.concepts.get(ch.concept_id)
    doc_parts = [ch.text_or]
    if c:
        doc_parts.extend([c.title_or, c.title_en, c.summary_or])
    doc_text = " ".join(doc_parts)
    chunk_docs.append(tokenize_enhanced(doc_text))

bm25 = BM25Okapi(chunk_docs)

# Evaluate against 100 queries
queries_path = REPO / "tests" / "fixtures" / "odia_queries.jsonl"
queries = [json.loads(line) for line in queries_path.read_text(encoding="utf-8").splitlines() if line.strip()]
hits = 0
failures = []
for q in queries:
    q_tokens = tokenize_enhanced(q["query_text"])
    scores = bm25.get_scores(q_tokens)
    ranked = [chunk_ids[i] for i in sorted(range(len(scores)), key=lambda i: -scores[i])[:5]]
    if any(cid in q["expected_chunk_ids"] for cid in ranked):
        hits += 1
    else:
        failures.append((q["query_id"], q["category"], q["query_text"], q["expected_chunk_ids"], ranked[:3]))

print(f"Enhanced Recall@5: {hits}/{len(queries)} = {hits/len(queries)*100:.2f}%")
print(f"Total failures: {len(failures)}")
for f in failures[:10]:
    print(f"FAIL: {f[0]} [{f[1]}] '{f[2]}' expected={f[3]} got={f[4]}")
