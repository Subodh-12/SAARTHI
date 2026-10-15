# Chapter 3: Tissues Questions
# Concepts: c0007 (Tissues and Types), c0008 (Plant Tissues), c0009 (Animal Tissues)
# Each concept has 12 questions: 4 easy, 4 medium, 4 hard.
# Bloom levels cover: remember, understand, apply, analyze, evaluate, create.

def get_ch03_questions():
    q = []

    # ------------------------------------------------------------------------
    # CONCEPT c0007: Tissues and Types (ଟିସ୍ୟୁ ଓ ଏହାର ପ୍ରକାରଭେଦ)
    # ------------------------------------------------------------------------
    # 1. Easy - Remember
    q.append({
        "question_id": "q_ch03_c0007_01",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "ଉତ୍ପତ୍ତି ଓ ଗଠନ ଦୃଷ୍ଟିରୁ ସମାନ ଏବଂ ଏକ ନିର୍ଦ୍ଦିଷ୍ଟ କାର୍ଯ୍ୟ କରୁଥିବା କୋଷମାନଙ୍କ ସମଷ୍ଟିକୁ କଣ କୁହାଯାଏ?",
        "options": [
            {"index": 0, "text_or": "ଅଙ୍ଗ (Organ)", "misconception_tag": "confusing_tissue_with_organ", "explanation_or": "ବିଭିନ୍ନ ଟିସ୍ୟୁ ଏକତ୍ରିତ ହୋଇ ଅଙ୍ଗ ଗଠନ କରନ୍ତି।"},
            {"index": 1, "text_or": "ଟିସ୍ୟୁ (Tissue)", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ଅଙ୍ଗତନ୍ତ୍ର (Organ system)", "misconception_tag": "confusing_tissue_with_organ_system", "explanation_or": "ଏକାଧିକ ଅଙ୍ଗ ମିଶି ଅଙ୍ଗତନ୍ତ୍ର ଗଠନ କରନ୍ତି।"},
            {"index": 3, "text_or": "କୋଷାଙ୍ଗ (Organelle)", "misconception_tag": "confusing_tissue_with_organelle", "explanation_or": "କୋଷାଙ୍ଗ ହେଉଛି କୋଷ ଭିତରେ ଥିବା ଅଂଶ (ଯଥା ମାଇଟୋକଣ୍ଡ୍ରିଆ)।"}
        ],
        "correct_option": 1,
        "explanation_or": "ସମାନ ଉତ୍ପତ୍ତି ଏବଂ ସମାନ କାର୍ଯ୍ୟ ସମ୍ପାଦନ କରୁଥିବା କୋଷମାନଙ୍କ ଗୋଷ୍ଠୀକୁ ଟିସ୍ୟୁ କୁହାଯାଏ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # 2. Easy - Remember
    q.append({
        "question_id": "q_ch03_c0007_02",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "ନିମ୍ନଲିଖିତ ମଧ୍ୟରୁ କେଉଁଟି ଏକ ତରଳ ସଂଯୋଜକ ଟିସ୍ୟୁର (liquid connective tissue) ଉଦାହରଣ ଅଟେ?",
        "options": [
            {"index": 0, "text_or": "ରକ୍ତ (Blood)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଅସ୍ଥି (Bone)", "misconception_tag": "confusing_solid_connective_with_liquid", "explanation_or": "ଅସ୍ଥି ଏକ କଠିନ ସଂଯୋଜକ ଟିସ୍ୟୁ।"},
            {"index": 2, "text_or": "ମାଂସପେଶୀ (Muscle)", "misconception_tag": "confusing_muscular_tissue_with_connective", "explanation_or": "ମାଂସପେଶୀ ପେଶୀ ଟିସ୍ୟୁ ଅନ୍ତର୍ଭୁକ୍ତ।"},
            {"index": 3, "text_or": "ଚର୍ମ (Skin)", "misconception_tag": "confusing_epithelial_with_connective", "explanation_or": "ଚର୍ମ ଏପିଥେଲିଆଲ ଟିସ୍ୟୁ ଦ୍ୱାରା ଆଚ୍ଛାଦିତ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ରକ୍ତ ହେଉଛି ଏକ ତରଳ ସଂଯୋଜକ ଟିସ୍ୟୁ ଯାହାର ପ୍ଲାଜମା ମଧ୍ୟରେ କୋଷଗୁଡ଼ିକ ଭାସମାନ ଅବସ୍ଥାରେ ଥାଆନ୍ତି।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # 3. Easy - Understand
    q.append({
        "question_id": "q_ch03_c0007_03",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "understand",
        "qtype": "mcq",
        "prompt_or": "ବହୁକୋଷୀ ଜୀବମାନଙ୍କ ଶରୀରରେ 'ଶ୍ରମ ବିଭାଜନ' (division of labour) ର ମୁଖ୍ୟ ଉଦ୍ଦେଶ୍ୟ କଣ?",
        "options": [
            {"index": 0, "text_or": "ବିଭିନ୍ନ କୋଷ ଗୋଷ୍ଠୀ ନିର୍ଦ୍ଦିଷ୍ଟ କାର୍ଯ୍ୟ କରିବା ଫଳରେ ସମଗ୍ର ଶରୀରର କାର୍ଯ୍ୟଦକ୍ଷତା ସର୍ବାଧିକ ହୁଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "କୋଷମାନଙ୍କ ମଧ୍ୟରେ ପ୍ରତିଯୋଗିତା ବୃଦ୍ଧି କରିବା", "misconception_tag": "assuming_cellular_competition", "explanation_or": "କୋଷଗୁଡ଼ିକ ସହଯୋଗ କରି କାର୍ଯ୍ୟ କରନ୍ତି, ପ୍ରତିଯୋଗିତା ନୁହେଁ।"},
            {"index": 2, "text_or": "ଜୀବକୁ ଏକକୋଷୀ ଜୀବରେ ପରିଣତ କରିବା", "misconception_tag": "reversing_evolutionary_complexity", "explanation_or": "ଶ୍ରମ ବିଭାଜନ ବହୁକୋଷୀ ଜୀବର ଜଟିଳତା ଓ ଦକ୍ଷତା ବଢ଼ାଏ।"},
            {"index": 3, "text_or": "ଶରୀରର ତାପମାତ୍ରା ସର୍ବଦା ଶୂନ ରଖିବା", "misconception_tag": "confusing_function_with_temperature", "explanation_or": "ଏହା ଶ୍ରମ ବିଭାଜନର ଉଦ୍ଦେଶ୍ୟ ନୁହେଁ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଶ୍ରମ ବିଭାଜନ ଯୋଗୁଁ ନିର୍ଦ୍ଦିଷ୍ଟ ଟିସ୍ୟୁ ନିର୍ଦ୍ଦିଷ୍ଟ କାର୍ଯ୍ୟ (ଯଥା ଶ୍ୱାସକ୍ରିୟା, ପରିବହନ, ସଙ୍କୋଚନ) ଅତି ନିପୁଣତାର ସହ ସମ୍ପାଦନ କରେ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # 4. Easy - Understand
    q.append({
        "question_id": "q_ch03_c0007_04",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "understand",
        "qtype": "mcq",
        "prompt_or": "ଉଦ୍ଭିଦମାନଙ୍କଠାରେ ପ୍ରାଣୀମାନଙ୍କ ତୁଳନାରେ ମୃତ ସହାୟକ ଟିସ୍ୟୁ (dead supportive tissue) କାହିଁକି ଅଧିକ ଦେଖାଯାଏ?",
        "options": [
            {"index": 0, "text_or": "ଉଦ୍ଭିଦ ସ୍ଥିର ଥାଏ ଏବଂ ତାକୁ କମ୍ ଶକ୍ତି ବ୍ୟୟରେ ଝଡ଼-ବର୍ଷାରୁ ରକ୍ଷା ପାଇବାକୁ ଯାନ୍ତ୍ରିକ ଦୃଢ଼ତା ଦରକାର ହୁଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଉଦ୍ଭିଦର କୋଷଗୁଡ଼ିକ ଜୀବନ୍ତ ରହିବାକୁ ଭଲ ପାଆନ୍ତି ନାହିଁ", "misconception_tag": "teleological_anthropomorphic_error", "explanation_or": "ଏହା କୌଣସି ବୈଜ୍ଞାନିକ କାରଣ ନୁହେଁ।"},
            {"index": 2, "text_or": "ଉଦ୍ଭିଦରେ ଆଲୋକଶ୍ଳେଷଣ କେବେ ହୋଇପାରେ ନାହିଁ", "misconception_tag": "denying_photosynthesis", "explanation_or": "ଉଦ୍ଭିଦ ଆଲୋକଶ୍ଳେଷଣ ଦ୍ୱାରା ଖାଦ୍ୟ ପ୍ରସ୍ତୁତ କରେ।"},
            {"index": 3, "text_or": "ପ୍ରାଣୀମାନଙ୍କର କୌଣସି ଜୀବନ୍ତ ଟିସ୍ୟୁ ନଥାଏ", "misconception_tag": "reversing_plant_animal_cellularity", "explanation_or": "ପ୍ରାଣୀମାନଙ୍କ ଅଧିକାଂଶ ଟିସ୍ୟୁ ଜୀବନ୍ତ କୋଷ ଦ୍ୱାରା ଗଠିତ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଉଦ୍ଭିଦ ସ୍ଥାନ ପରିବର୍ତ୍ତନ କରେ ନାହିଁ; ମୃତ ଟିସ୍ୟୁ (ଯଥା ସ୍କ୍ଲେରେନକାଇମା) କମ୍ ରକ୍ଷଣାବେକ୍ଷଣ ଶକ୍ତିରେ ଗଛକୁ ଠିଆ ହେବାକୁ ଯାନ୍ତ୍ରିକ ଶକ୍ତି ଦିଏ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # 5. Medium - Apply
    q.append({
        "question_id": "q_ch03_c0007_05",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "ଗଛର କାଣ୍ଡରୁ ବାହାର ବକଳ ବା ଛାଲ (bark) କାଢ଼ିଦେଲେ ଗଛ କାହିଁକି ସଂକ୍ରମଣ ଓ ଶୁଷ୍କତାର ଶିକାର ହୁଏ?",
        "options": [
            {"index": 0, "text_or": "କାରଣ ବକଳରେ ଥିବା ସୁରକ୍ଷାକାରୀ କର୍କ ଟିସ୍ୟୁ (protective cork) ନଷ୍ଟ ହୋଇଯାଏ ଯାହା ଜଳକ୍ଷୟ ଓ ଜୀବାଣୁ ପ୍ରବେଶ ରୋକୁଥିଲା", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "କାରଣ ଗଛର ହୃତ୍‌ପିଣ୍ଡ ଧଡ଼କନ ବନ୍ଦ ହୋଇଯାଏ", "misconception_tag": "attributing_animal_organs_to_plants", "explanation_or": "ଉଦ୍ଭିଦର ହୃତ୍‌ପିଣ୍ଡ ନଥାଏ।"},
            {"index": 2, "text_or": "କାରଣ କାଣ୍ଡ ତୁରନ୍ତ ତରଳରେ ପରିଣତ ହୋଇଯାଏ", "misconception_tag": "assuming_phase_change_in_stem", "explanation_or": "ଛାଲ ଛଡ଼ାଇଲେ କାଣ୍ଡ ତରଳେ ନାହିଁ।"},
            {"index": 3, "text_or": "କାରଣ ମୂଳରୁ ଜଳ ଶୋଷଣ ବନ୍ଦ ହୋଇଯାଏ", "misconception_tag": "confusing_cork_with_root_hairs", "explanation_or": "ମୂଳରୋମ ଜଳ ଶୋଷଣ କରନ୍ତି, କାଣ୍ଡର ଛାଲ ନୁହେଁ।"}
        ],
        "correct_option": 0,
        "explanation_or": "କର୍କ ବା ବାହ୍ୟ ସୁରକ୍ଷାକାରୀ ଟିସ୍ୟୁରେ ସୁବେରିନ୍ (suberin) ଥାଏ ଯାହା ଗ୍ୟାସ ଓ ଜଳ ଅପ୍ରବେଶ୍ୟ କରି ରୋଗ ଜୀବାଣୁରୁ ରକ୍ଷା କରେ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # 6. Medium - Apply
    q.append({
        "question_id": "q_ch03_c0007_06",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "ରକ୍ତ, ହୃତ୍‌ପେଶୀ, ଏବଂ ଜାଇଲମକୁ ସେମାନଙ୍କ ଶ୍ରେଣୀ ଅନୁଯାୟୀ କିପରି ସଠିକ୍ ଭାବେ ବର୍ଗୀକରଣ କରାଯାଇପାରିବ?",
        "options": [
            {"index": 0, "text_or": "ରକ୍ତ: ସଂଯୋଜକ ଟିସ୍ୟୁ, ହୃତ୍‌ପେଶୀ: ପେଶୀ ଟିସ୍ୟୁ, ଜାଇଲମ: ଜଟିଳ ଉଦ୍ଭିଦ ଟିସ୍ୟୁ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ରକ୍ତ: ଉଦ୍ଭିଦ ଟିସ୍ୟୁ, ହୃତ୍‌ପେଶୀ: ସଂଯୋଜକ ଟିସ୍ୟୁ, ଜାଇଲମ: ଏପିଥେଲିଆଲ ଟିସ୍ୟୁ", "misconception_tag": "confusing_plant_and_animal_tissues", "explanation_or": "ରକ୍ତ ପ୍ରାଣୀ ଟିସ୍ୟୁ ଏବଂ ଜାଇଲମ ଉଦ୍ଭିଦ ଟିସ୍ୟୁ।"},
            {"index": 2, "text_or": "ରକ୍ତ: ସ୍ନାୟୁ ଟିସ୍ୟୁ, ହୃତ୍‌ପେଶୀ: ଉଦ୍ଭିଦ ଟିସ୍ୟୁ, ଜାଇଲମ: ସଂଯୋଜକ ଟିସ୍ୟୁ", "misconception_tag": "misclassifying_muscular_tissue", "explanation_or": "ହୃତ୍‌ପେଶୀ ଏକ ପେଶୀ ଟିସ୍ୟୁ।"},
            {"index": 3, "text_or": "ତିନୋଟି ଯାକ କୌଣସି ଟିସ୍ୟୁ ନୁହଁନ୍ତି, କେବଳ ସାଧାରଣ ରାସାୟନିକ ପଦାର୍ଥ", "misconception_tag": "denying_biological_tissue_status", "explanation_or": "ଏଗୁଡ଼ିକ ସମସ୍ତେ ସୁଗଠିତ ଜୈବିକ ଟିସ୍ୟୁ ଅଟନ୍ତି।"}
        ],
        "correct_option": 0,
        "explanation_or": "ରକ୍ତ ହେଉଛି ପ୍ରାଣୀର ତରଳ ସଂଯୋଜକ ଟିସ୍ୟୁ, ହୃତ୍‌ପେଶୀ ହୃତ୍‌ପିଣ୍ଡର ପେଶୀ ଟିସ୍ୟୁ ଏବଂ ଜାଇଲମ ଉଦ୍ଭିଦର ସମ୍ବହନକାରୀ ଜଟିଳ ଟିସ୍ୟୁ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # 7. Medium - Analyze
    q.append({
        "question_id": "q_ch03_c0007_07",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "ଉଦ୍ଭିଦର ବୃଦ୍ଧି ଏବଂ ପ୍ରାଣୀର ବୃଦ୍ଧି ଶୈଳୀ ମଧ୍ୟରେ ଥିବା ପ୍ରମୁଖ ପାର୍ଥକ୍ୟର ବିଶ୍ଳେଷଣ କର।",
        "options": [
            {"index": 0, "text_or": "ଉଦ୍ଭିଦର ବୃଦ୍ଧି ନିର୍ଦ୍ଦିଷ୍ଟ ବିଭାଜନଶୀଳ ଅଞ୍ଚଳରେ ଆଜୀବନ ସୀମିତ ଥାଏ, ମାତ୍ର ପ୍ରାଣୀର ବୃଦ୍ଧି ସମଗ୍ର ଶରୀରରେ ସୁଷମ ଓ ଏକ ନିର୍ଦ୍ଦିଷ୍ଟ ବୟସ ପରେ ସ୍ଥିର ହୁଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଉଦ୍ଭିଦର ବୃଦ୍ଧି ୧୦ ବର୍ଷ ପରେ ବନ୍ଦ ହୁଏ କିନ୍ତୁ ପ୍ରାଣୀ ଆଜୀବନ ବଢ଼ିଚାଲେ", "misconception_tag": "reversing_plant_animal_growth_patterns", "explanation_or": "ବୃକ୍ଷ ଆଜୀବନ ବୃଦ୍ଧି ପାଏ, ପ୍ରାଣୀ ଏକ ନିର୍ଦ୍ଦିଷ୍ଟ ସମୟ ପରେ ବଢ଼େ ନାହିଁ।"},
            {"index": 2, "text_or": "ଉଭୟଙ୍କ ବୃଦ୍ଧି କେବଳ ଡାହାଣ ପାଖରେ ହିଁ ହୋଇଥାଏ", "misconception_tag": "asymmetrical_growth_fallacy", "explanation_or": "ଜୈବିକ ବୃଦ୍ଧି ସମମିତ ଭାବେ ଘଟେ।"},
            {"index": 3, "text_or": "କୌଣସି ଉଦ୍ଭିଦରେ କୋଷ ବିଭାଜନ ହୁଏ ନାହିଁ", "misconception_tag": "denying_plant_cell_division", "explanation_or": "ଭାଜକ ଟିସ୍ୟୁରେ ଦ୍ରୁତ କୋଷ ବିଭାଜନ ଘଟେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଉଦ୍ଭିଦରେ ଭାଜକ ଟିସ୍ୟୁ ଥିବାରୁ ଅଗ୍ରଭାଗରେ ଆଜୀବନ ବୃଦ୍ଧି ଘଟେ; ପ୍ରାଣୀମାନଙ୍କ ଶରୀରରେ କୋଷୀୟ ବୃଦ୍ଧି ସାରା ଶରୀରରେ ସୁଷମ ଭାବେ ସମନ୍ୱିତ ହୁଏ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # 8. Medium - Analyze
    q.append({
        "question_id": "q_ch03_c0007_08",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "ଏକକୋଷୀ ଜୀବ (ଯଥା ଆମିବା) ରେ ଟିସ୍ୟୁ ସ୍ତରର ସଂଗଠନ (tissue level organisation) କାହିଁକି ଦରକାର ହୁଏ ନାହିଁ?",
        "options": [
            {"index": 0, "text_or": "କାରଣ ଗୋଟିଏ କୋଷ ହିଁ ପୋଷଣ, ଶ୍ୱାସକ୍ରିୟା ଓ ରେଚନ ପରି ସମସ୍ତ ମୌଳିକ ଜୈବିକ କ୍ରିୟା ଏକାକୀ ସମ୍ପାଦନ କରେ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଆମିବାର କୌଣସି ଜୀବନ ନଥାଏ", "misconception_tag": "denying_amoeba_life", "explanation_or": "ଆମିବା ଏକ ଜୀବନ୍ତ ପ୍ରୋଟୋଜୋଆ ଅଟେ।"},
            {"index": 2, "text_or": "ଆମିବା କେବଳ ଟିସ୍ୟୁ ବିନା ମରିଯାଏ", "misconception_tag": "contradictory_reasoning", "explanation_or": "ଆମିବା ବିନା ଟିସ୍ୟୁରେ ସଫଳତାର ସହ ବଞ୍ଚି ରହେ।"},
            {"index": 3, "text_or": "ଆମିବାର କୋଷାଙ୍ଗଗୁଡ଼ିକ ଟିସ୍ୟୁ ଭାବେ ଗଣାଯାଏ", "misconception_tag": "equating_organelles_with_tissues", "explanation_or": "କୋଷାଙ୍ଗ କୋଷର ଭିତର ଅଂଶ, କୋଷମାନଙ୍କ ଗୋଷ୍ଠୀ ନୁହେଁ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଏକକୋଷୀ ଜୀବରେ ଗୋଟିଏ କୋଷ ଭିତରେ ହିଁ ସମସ୍ତ କାର୍ଯ୍ୟ ହୋଇଥାଏ; ଏକାଧିକ କୋଷ ନଥିବାରୁ ସେଠାରେ ଟିସ୍ୟୁ ଗଠନର ଆବଶ୍ୟକତା ନଥାଏ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # 9. Hard - Evaluate
    q.append({
        "question_id": "q_ch03_c0007_09",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ବଡ଼ ବୃକ୍ଷମାନଙ୍କ କାଠିଆ ଅଂଶରେ ଅଧିକାଂଶ ଟିସ୍ୟୁ ମୃତ କୋଷରେ ଗଠିତ ହେବାର ଉଦ୍ଭିଦବିଜ୍ଞାନୀୟ ମୂଲ୍ୟାୟନ କର। ଏହା ବୃକ୍ଷ ପାଇଁ କି ପ୍ରକାର ଅନୁକୂଳନ (adaptation)?",
        "options": [
            {"index": 0, "text_or": "ଏହା କମ୍ ଶକ୍ତି ଓ ଖାଦ୍ୟ ବ୍ୟୟରେ ବୃକ୍ଷକୁ ବିରାଟ ଉଚ୍ଚତାରେ ଠିଆ ହେବାକୁ ଆବଶ୍ୟକ ଯାନ୍ତ୍ରିକ ଦୃଢ଼ତା ଯୋଗାଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଏହା ଏକ ତ୍ରୁଟି ଯାହା ଯୋଗୁଁ ଗଛ ଶୀଘ୍ର ମରିଯାଏ", "misconception_tag": "viewing_adaptation_as_defect", "explanation_or": "ଏହା ଗଛକୁ ଶହ ଶହ ବର୍ଷ ବଞ୍ଚିବାରେ ସାହାଯ୍ୟ କରେ।"},
            {"index": 2, "text_or": "ମୃତ କୋଷ ଗଛକୁ ପକ୍ଷୀମାନଙ୍କଠାରୁ ଲୁଚାଇ ରଖେ", "misconception_tag": "absurd_camouflage_claim", "explanation_or": "ଏହା ସୁରକ୍ଷା ଓ ଦୃଢ଼ତା ପାଇଁ ଉଦ୍ଦିଷ୍ଟ।"},
            {"index": 3, "text_or": "ମୃତ କୋଷ ଆଲୋକଶ୍ଳେଷଣର ଗତିକୁ ୧୦୦ ଗୁଣ ବଢ଼ାଇଦିଏ", "misconception_tag": "attributing_photosynthesis_to_dead_cells", "explanation_or": "ମୃତ କୋଷରେ କ୍ଲୋରୋପ୍ଲାଷ୍ଟ ନଥାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ମୃତ ଟିସ୍ୟୁରେ ପ୍ରୋଟୋପ୍ଲାଜ୍ମ ନଥାଏ, ତେଣୁ ଏହା ଶ୍ୱାସକ୍ରିୟା ପାଇଁ ଶକ୍ତି ନେଇନଥାଏ, କିନ୍ତୁ କାନ୍ଥରେ ଲିଗ୍ନିନ ଥିବାରୁ ବିରାଟ ଯାନ୍ତ୍ରିକ ଶକ୍ତି ପ୍ରଦାନ କରେ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # 10. Hard - Evaluate
    q.append({
        "question_id": "q_ch03_c0007_10",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ଏପିଥେଲିଆଲ ଟିସ୍ୟୁ ତଳେ ଥିବା ଭିତ୍ତି ଝିଲ୍ଲୀ (basement membrane) ଯଦି ନଷ୍ଟ ହୋଇଯାଏ, ତେବେ ଶରୀର ଉପରେ କି ପ୍ରଭାବ ପଡ଼ିବାର ସମ୍ଭାବନା ରହିଛି?",
        "options": [
            {"index": 0, "text_or": "ଆବରଣୀ କୋଷଗୁଡ଼ିକ ସଂଯୋଜକ ଟିସ୍ୟୁରୁ ଅଲଗା ହୋଇଯିବେ ଏବଂ ପୋଷକ ତତ୍ତ୍ୱର ବିନିମୟ ବାଧାପ୍ରାପ୍ତ ହେବ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ସମସ୍ତ ଅସ୍ଥି ତୁରନ୍ତ ଭାଙ୍ଗିଯିବ", "misconception_tag": "attributing_skeletal_failure_to_epithelium", "explanation_or": "ଅସ୍ଥି କଙ୍କାଳ ତନ୍ତ୍ରର ଅଂଶ।"},
            {"index": 2, "text_or": "ରକ୍ତ ସଞ୍ଚାଳନ ଦ୍ୱିଗୁଣିତ ହୋଇଯିବ", "misconception_tag": "unsupported_cardiovascular_boost", "explanation_or": "ଭିତ୍ତି ଝିଲ୍ଲୀ କ୍ଷତିଗ୍ରସ୍ତ ହେଲେ ରକ୍ତ ସଞ୍ଚାଳନ ବଢ଼େ ନାହିଁ।"},
            {"index": 3, "text_or": "କୌଣସି ପ୍ରଭାବ ପଡ଼ିବ ନାହିଁ କାରଣ ଭିତ୍ତି ଝିଲ୍ଲୀର କୌଣସି କାର୍ଯ୍ୟ ନାହିଁ", "misconception_tag": "denying_basement_membrane_function", "explanation_or": "ଭିତ୍ତି ଝିଲ୍ଲୀ ଆଧାର ଓ ବାରଣ ଉଭୟ ଭାବେ କାର୍ଯ୍ୟ କରେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଭିତ୍ତି ଝିଲ୍ଲୀ ଏପିଥେଲିଆଲ କୋଷକୁ ତଳେ ଥିବା ସଂଯୋଜକ ଟିସ୍ୟୁ ସହ ବାନ୍ଧି ରଖେ ଏବଂ ରକ୍ତଜାଲକରୁ ପୋଷକ ପଦାର୍ଥର ବ୍ୟାପନ ନିୟନ୍ତ୍ରଣ କରେ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # 11. Hard - Create
    q.append({
        "question_id": "q_ch03_c0007_11",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ଜୈବିକ ସଂଗଠନର ସ୍ତରଗୁଡ଼ିକୁ (Levels of Biological Organisation) କ୍ଷୁଦ୍ରତମରୁ ବୃହତ୍ତମ କ୍ରମରେ ସଜାଇଲେ କେଉଁ କ୍ରମଟି ସଠିକ୍ ହେବ?",
        "options": [
            {"index": 0, "text_or": "କୋଷ → ଟିସ୍ୟୁ → ଅଙ୍ଗ → ଅଙ୍ଗତନ୍ତ୍ର → ସମ୍ପୂର୍ଣ୍ଣ ଜୀବ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଟିସ୍ୟୁ → କୋଷ → ଅଙ୍ଗତନ୍ତ୍ର → ଅଙ୍ଗ → ଜୀବ", "misconception_tag": "inverting_cell_tissue_order", "explanation_or": "କୋଷ ମିଶି ଟିସ୍ୟୁ ଗଠନ କରନ୍ତି, ଓଲଟା ନୁହେଁ।"},
            {"index": 2, "text_or": "ଅଙ୍ଗ → ଟିସ୍ୟୁ → କୋଷ → ଜୀବ → ଅଙ୍ଗତନ୍ତ୍ର", "misconception_tag": "scrambled_hierarchy", "explanation_or": "ଅଙ୍ଗ ଟିସ୍ୟୁଠାରୁ ବଡ଼ ସ୍ତର ଅଟେ।"},
            {"index": 3, "text_or": "କୋଷ → ଅଙ୍ଗ → ଟିସ୍ୟୁ → ଅଙ୍ଗତନ୍ତ୍ର", "misconception_tag": "placing_organ_before_tissue", "explanation_or": "ପ୍ରଥମେ ଟିସ୍ୟୁ, ତାପରେ ଅଙ୍ଗ ଗଠିତ ହୁଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ମୌଳିକ ଏକକ କୋଷ (Cell) ଏକାଠି ହୋଇ ଟିସ୍ୟୁ (Tissue), ଟିସ୍ୟୁ ମିଶି ଅଙ୍ଗ (Organ), ଅଙ୍ଗ ମିଶି ଅଙ୍ଗତନ୍ତ୍ର (Organ System) ଏବଂ ଶେଷରେ ସମ୍ପୂର୍ଣ୍ଣ ଜୀବ (Organism) ଗଠିତ ହୁଏ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # 12. Hard - Create
    q.append({
        "question_id": "q_ch03_c0007_12",
        "concept_id": "c0007",
        "chapter_id": "ch003",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ଅଜଣା ଏକ ଟିସ୍ୟୁ ନମୁନା ମାଇକ୍ରୋସ୍କୋପ୍ ତଳେ ଦେଖିବା ବେଳେ ଏହାର କୋଷଗୁଡ଼ିକ ଚାରିପାଖରେ ଏକ ସ୍ପଷ୍ଟ ସେଲ୍ୟୁଲୋଜ୍ କୋଷଭିତ୍ତି (cell wall) ଦେଖାଗଲା। ଆପଣ ଏହାକୁ କିପରି ଚିହ୍ନଟ କରିବେ?",
        "options": [
            {"index": 0, "text_or": "ଏହା ନିଶ୍ଚିତ ଭାବେ ଏକ ଉଦ୍ଭିଦ ଟିସ୍ୟୁ, କାରଣ ପ୍ରାଣୀ କୋଷରେ କୋଷଭିତ୍ତି ନଥାଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଏହା ଏକ ମାଂସପେଶୀ ଟିସ୍ୟୁ", "misconception_tag": "identifying_plant_cell_as_muscle", "explanation_or": "ମାଂସପେଶୀ ପ୍ରାଣୀ ଟିସ୍ୟୁ, ଏଥିରେ କୋଷଭିତ୍ତି ନଥାଏ।"},
            {"index": 2, "text_or": "ଏହା ଏକ ସ୍ନାୟୁ ଟିସ୍ୟୁ", "misconception_tag": "identifying_plant_cell_as_nerve", "explanation_or": "ନ୍ୟୁରନରେ କେବଳ ପ୍ଲାଜମା ଝିଲ୍ଲୀ ଥାଏ, କୋଷଭିତ୍ତି ନୁହେଁ।"},
            {"index": 3, "text_or": "ଏହା ଏକ ରକ୍ତ କଣିକା", "misconception_tag": "identifying_as_blood_cell", "explanation_or": "ରକ୍ତ କଣିକାର କୌଣସି କୋଷଭିତ୍ତି ନଥାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ସେଲ୍ୟୁଲୋଜ୍ ନିର୍ମିତ ଦୃଢ଼ କୋଷଭିତ୍ତି କେବଳ ଉଦ୍ଭିଦ ଟିସ୍ୟୁର ଅନନ୍ୟ ବୈଶିଷ୍ଟ୍ୟ ଅଟେ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.1",
        "revision": 1,
        "status": "active"
    })

    # ------------------------------------------------------------------------
    # CONCEPT c0008: Plant Tissues (ଉଦ୍ଭିଦ ଟିସ୍ୟୁ)
    # ------------------------------------------------------------------------
    # 1. Easy - Remember
    q.append({
        "question_id": "q_ch03_c0008_01",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "ଉଦ୍ଭିଦର ମୂଳ ଓ କାଣ୍ଡର ଅଗ୍ରଭାଗରେ ରହି ଲମ୍ବ ବୃଦ୍ଧି କରୁଥିବା ଭାଜକ ଟିସ୍ୟୁକୁ କଣ କୁହାଯାଏ?",
        "options": [
            {"index": 0, "text_or": "ଅଗ୍ରସ୍ଥ ଭାଜକ ଟିସ୍ୟୁ (Apical meristem)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ପାର୍ଶ୍ୱସ୍ଥ ଭାଜକ ଟିସ୍ୟୁ (Lateral meristem)", "misconception_tag": "confusing_apical_with_lateral", "explanation_or": "ପାର୍ଶ୍ୱସ୍ଥ ମେରିଷ୍ଟେମ୍ କାଣ୍ଡର ମୋଟେଇ ବଢ଼ାଏ।"},
            {"index": 2, "text_or": "ଅନ୍ତର୍ବିଷ୍ଟ ଭାଜକ ଟିସ୍ୟୁ (Intercalary meristem)", "misconception_tag": "confusing_apical_with_intercalary", "explanation_or": "ଅନ୍ତର୍ବିଷ୍ଟ ଗଣ୍ଠି ନିକଟରେ ଥାଏ।"},
            {"index": 3, "text_or": "ସ୍ଥାୟୀ ଟିସ୍ୟୁ", "misconception_tag": "confusing_meristematic_with_permanent", "explanation_or": "ସ୍ଥାୟୀ ଟିସ୍ୟୁ କୋଷ ବିଭାଜନ କ୍ଷମତା ହରାଇଥାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଅଗ୍ରସ୍ଥ ଭାଜକ ଟିସ୍ୟୁ (Apical meristem) କାଣ୍ଡ ଏବଂ ମୂଳର ଅଗ୍ରଭାଗରେ ରହି ଲମ୍ବ ବୃଦ୍ଧି କରେ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # 2. Easy - Remember
    q.append({
        "question_id": "q_ch03_c0008_02",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "କୋଷ କାନ୍ଥରେ ଲିଗ୍ନିନ୍ (lignin) ଜମା ହୋଇ ମୃତ କୋଷରେ ପରିଣତ ହୋଇଥିବା ଦୃଢ଼ ଉଦ୍ଭିଦ ଟିସ୍ୟୁ କେଉଁଟି?",
        "options": [
            {"index": 0, "text_or": "ପାରେନକାଇମା (Parenchyma)", "misconception_tag": "confusing_sclerenchyma_with_parenchyma", "explanation_or": "ପାରେନକାଇମା କୋଷ ଜୀବନ୍ତ ଓ ପତଳା କାନ୍ଥ ବିଶିଷ୍ଟ।"},
            {"index": 1, "text_or": "କୋଲେନକାଇମା (Collenchyma)", "misconception_tag": "confusing_sclerenchyma_with_collenchyma", "explanation_or": "କୋଲେନକାଇମାରେ ପେକ୍ଟିନ ଜମା ଥାଏ, ଲିଗ୍ନିନ ନୁହେଁ।"},
            {"index": 2, "text_or": "ସ୍କ୍ଲେରେନକାଇମା (Sclerenchyma)", "misconception_tag": None, "explanation_or": None},
            {"index": 3, "text_or": "କ୍ଲୋରେନକାଇମା", "misconception_tag": "confusing_with_photosynthetic_parenchyma", "explanation_or": "କ୍ଲୋରେନକାଇମା ଆଲୋକଶ୍ଳେଷଣ କରେ।"}
        ],
        "correct_option": 2,
        "explanation_or": "ସ୍କ୍ଲେରେନକାଇମା କୋଷର କାନ୍ଥରେ ଲିଗ୍ନିନ ଜମା ହୋଇ କୋଷଗୁଡ଼ିକ ମୃତ ହୋଇଯାଆନ୍ତି (ଯଥା ନଡ଼ିଆ କତାର ତନ୍ତୁ)।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # 3. Easy - Understand
    q.append({
        "question_id": "q_ch03_c0008_03",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "understand",
        "qtype": "mcq",
        "prompt_or": "ପତ୍ରର ବାହ୍ୟ ଚର୍ମରେ ଥିବା ଷ୍ଟୋମାଟା (Stomata) ବା ସ୍ତୋମର ମୁଖ୍ୟ କାର୍ଯ୍ୟ କଣ?",
        "options": [
            {"index": 0, "text_or": "ଗ୍ୟାସ ବିନିମୟ (ବାୟୁ ସହ O₂ ଓ CO₂ ଆଦାନପ୍ରଦାନ) ଏବଂ ଉତ୍ସ୍ୱେଦନ (Transpiration)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଗଛକୁ ଠିଆ ହୋଇ ରହିବାକୁ ଶକ୍ତି ଦେବା", "misconception_tag": "confusing_stomata_with_mechanical_tissue", "explanation_or": "ଦୃଢ଼ତା ସ୍କ୍ଲେରେନକାଇମା ପ୍ରଦାନ କରେ।"},
            {"index": 2, "text_or": "ମାଟିରୁ ଜଳ ଶୋଷଣ କରିବା", "misconception_tag": "confusing_stomata_with_roots", "explanation_or": "ମୂଳରୋମ ଜଳ ଶୋଷଣ କରନ୍ତି।"},
            {"index": 3, "text_or": "ଫଳ ଉତ୍ପାଦନ ନିୟନ୍ତ୍ରଣ କରିବା", "misconception_tag": "attributing_reproduction_to_stomata", "explanation_or": "ଏହା ପ୍ରଜନନ ଅଙ୍ଗର କାର୍ଯ୍ୟ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଷ୍ଟୋମାଟା ରକ୍ଷୀକୋଷ (Guard cells) ଦ୍ୱାରା ନିୟନ୍ତ୍ରିତ ହୋଇ ଗ୍ୟାସୀୟ ବିନିମୟ ଏବଂ ଜଳୀୟବାଷ୍ପ ନିର୍ଗମନ (ଉତ୍ସ୍ୱେଦନ) କରେ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # 4. Easy - Understand
    q.append({
        "question_id": "q_ch03_c0008_04",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "understand",
        "qtype": "mcq",
        "prompt_or": "ଜାଇଲମ (Xylem) ଏବଂ ଫ୍ଲୋଏମ (Phloem) କୁ କାହିଁକି 'ଜଟିଳ ସ୍ଥାୟୀ ଟିସ୍ୟୁ' (Complex permanent tissue) କୁହାଯାଏ?",
        "options": [
            {"index": 0, "text_or": "ଏମାନେ ଏକାଧିକ ପ୍ରକାରର କୋଷକୁ ନେଇ ଗଠିତ ହୋଇ ଏକତ୍ରିତ ଭାବେ ଗୋଟିଏ କାର୍ଯ୍ୟ କରନ୍ତି", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଏମାନଙ୍କୁ ମାଇକ୍ରୋସ୍କୋପରେ ଦେଖିବା ବହୁତ କଷ୍ଟକର", "misconception_tag": "interpreting_complex_as_difficult_to_see", "explanation_or": "'ଜଟିଳ' ଶବ୍ଦ କୋଷର ବିଭିନ୍ନତାକୁ ବୁଝାଏ।"},
            {"index": 2, "text_or": "ଏମାନେ କେବଳ ବିଷାକ୍ତ ଉଦ୍ଭିଦରେ ହିଁ ମିଳନ୍ତି", "misconception_tag": "associating_complexity_with_toxicity", "explanation_or": "ସମସ୍ତ ସପୁଷ୍ପକ ବୃକ୍ଷରେ ସମ୍ବହନ ଟିସ୍ୟୁ ଥାଏ।"},
            {"index": 3, "text_or": "ଏମାନଙ୍କର କୌଣସି ନିର୍ଦ୍ଦିଷ୍ଟ କାର୍ଯ୍ୟ ନଥାଏ", "misconception_tag": "denying_vascular_function", "explanation_or": "ଜଳ ଓ ଖାଦ୍ୟ ପରିବହନ ଏମାନଙ୍କ ମୁଖ୍ୟ କାର୍ଯ୍ୟ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ସରଳ ଟିସ୍ୟୁ ଏକା ପ୍ରକାର କୋଷରେ ଗଠିତ, କିନ୍ତୁ ଜାଇଲମ ଓ ଫ୍ଲୋଏମ ୪ ପ୍ରକାରର ଭିନ୍ନ କୋଷରେ ଗଠିତ ହୋଇ ସମ୍ବହନ କାର୍ଯ୍ୟ କରନ୍ତି।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # 5. Medium - Apply
    q.append({
        "question_id": "q_ch03_c0008_05",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "ଘାସକୁ ଉପରୁ କାଟିଦେବା ପରେ କିମ୍ବା ଛେଳି ଚରିଯିବା ପରେ ତାହା ପୁଣି ଦ୍ରୁତ ଗତିରେ କିପରି ବଢ଼ିଯାଏ?",
        "options": [
            {"index": 0, "text_or": "ଗଣ୍ଠି ନିକଟରେ ଥିବା ଅନ୍ତର୍ବିଷ୍ଟ ଭାଜକ ଟିସ୍ୟୁ (Intercalary meristem) ସକ୍ରିୟ ଭାବେ ନୂଆ କୋଷ ସୃଷ୍ଟି କରେ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଜାଇଲମ ଟିସ୍ୟୁ କୋଷ ବିଭାଜନ କରିବା ଆରମ୍ଭ କରେ", "misconception_tag": "attributing_division_to_xylem", "explanation_or": "ଜାଇଲମ ଏକ ସ୍ଥାୟୀ ଟିସ୍ୟୁ, ଏହା ବିଭାଜିତ ହୁଏ ନାହିଁ।"},
            {"index": 2, "text_or": "ଛେଳିର ଲାଳ ଯୋଗୁଁ ଘାସ ଲମ୍ବା ହୁଏ", "misconception_tag": "attributing_growth_to_saliva", "explanation_or": "ଉଦ୍ଭିଦର ନିଜସ୍ୱ ଭାଜକ ଟିସ୍ୟୁ ହିଁ ବୃଦ୍ଧି ଘଟାଏ।"},
            {"index": 3, "text_or": "ପତ୍ରର ଷ୍ଟୋମାଟା କାଣ୍ଡରେ ପରିଣତ ହୁଏ", "misconception_tag": "assuming_stomata_transmutation", "explanation_or": "ଷ୍ଟୋମାଟା ରନ୍ଧ୍ର ଅଟେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ତୃଣଜାତୀୟ ଉଦ୍ଭିଦର ପର୍ବମଧ୍ୟ (internode) ବା ଗଣ୍ଠି ପାଖରେ ଅନ୍ତର୍ବିଷ୍ଟ ମେରିଷ୍ଟେମ୍ ଥିବାରୁ ଅଗ୍ରଭାଗ କଟିଗଲେ ମଧ୍ୟ ଏହା ଶୀଘ୍ର ବୃଦ୍ଧି ପାଏ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # 6. Medium - Apply
    q.append({
        "question_id": "q_ch03_c0008_06",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "ନଡ଼ିଆ କତାର ଟାଣ ତନ୍ତୁ କେଉଁ ଉଦ୍ଭିଦ ଟିସ୍ୟୁ ଦ୍ୱାରା ନିର୍ମିତ ହୋଇଥାଏ?",
        "options": [
            {"index": 0, "text_or": "ସ୍କ୍ଲେରେନକାଇମା ଟିସ୍ୟୁ (Sclerenchyma)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ପାରେନକାଇମା ଟିସ୍ୟୁ", "misconception_tag": "confusing_sclerenchyma_with_parenchyma", "explanation_or": "ପାରେନକାଇମା କୋମଳ ଟିସ୍ୟୁ ଅଟେ।"},
            {"index": 2, "text_or": "ଭାଜକ ଟିସ୍ୟୁ", "misconception_tag": "confusing_fibers_with_meristem", "explanation_or": "ଭାଜକ ଟିସ୍ୟୁ ଅତ୍ୟନ୍ତ କୋମଳ ଓ ବିଭାଜନଶୀଳ।"},
            {"index": 3, "text_or": "ଏପିଥେଲିଆଲ ଟିସ୍ୟୁ", "misconception_tag": "confusing_plant_with_animal_tissue", "explanation_or": "ଏପିଥେଲିଆଲ ପ୍ରାଣୀମାନଙ୍କଠାରେ ଥାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ନଡ଼ିଆର ବାହ୍ୟ ଆବରଣ ସ୍କ୍ଲେରେନକାଇମା ତନ୍ତୁରେ ଗଠିତ, ଯାହାର ଲିଗ୍ନିନଯୁକ୍ତ ମୋଟା କାନ୍ଥ ଏହାକୁ ଅତ୍ୟନ୍ତ ଦୃଢ଼ କରେ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # 7. Medium - Analyze
    q.append({
        "question_id": "q_ch03_c0008_07",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "ଜାଇଲମ ଏବଂ ଫ୍ଲୋଏମ ମଧ୍ୟରେ ପରିବହନର ଦିଗ ସମ୍ପର୍କରେ କେଉଁ ତୁଳନାତ୍ମକ ବିଶ୍ଳେଷଣଟି ସଠିକ୍?",
        "options": [
            {"index": 0, "text_or": "ଜାଇଲମରେ ଜଳର ପରିବହନ କେବଳ ଉର୍ଦ୍ଧ୍ୱମୁଖୀ (unidirectional), କିନ୍ତୁ ଫ୍ଲୋଏମରେ ଖାଦ୍ୟ ପରିବହନ ଉଭୟ ଉର୍ଦ୍ଧ୍ୱ ଓ ଅଧୋମୁଖୀ (bidirectional)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଜାଇଲମ ଖାଦ୍ୟ ତଳକୁ ବୁହାଏ ଏବଂ ଫ୍ଲୋଏମ ପାଣି ଉପରକୁ ଉଠାଏ", "misconception_tag": "reversing_xylem_phloem_functions", "explanation_or": "ଜାଇଲମ ଜଳ ଏବଂ ଫ୍ଲୋଏମ ଖାଦ୍ୟ ପରିବହନ କରେ।"},
            {"index": 2, "text_or": "ଉଭୟ ଜାଇଲମ ଓ ଫ୍ଲୋଏମ କେବଳ ଅଧୋମୁଖୀ ଦିଗରେ କାର୍ଯ୍ୟ କରନ୍ତି", "misconception_tag": "assuming_only_downward_transport", "explanation_or": "ଜଳ ମୂଳରୁ ଉପରକୁ ଉଠିବା ବାଧ୍ୟତାମୂଳକ।"},
            {"index": 3, "text_or": "କୌଣସି ଟିସ୍ୟୁରେ ଦିଗର କୌଣସି ନିୟମ ନଥାଏ", "misconception_tag": "denying_regulated_transport", "explanation_or": "ଉଦ୍ଭିଦ ଶରୀରବିଜ୍ଞାନରେ ଏହା ସୁନିର୍ଦ୍ଦିଷ୍ଟ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଜାଇଲମ ମୂଳରୁ ଉପରକୁ ଏକମୁଖୀ ଜଳ ପରିବହନ କରେ; ଫ୍ଲୋଏମ ପତ୍ରରୁ ଖାଦ୍ୟକୁ ମୂଳ (ତଳକୁ) ଏବଂ ବୃଦ୍ଧିଶୀଳ କଢ଼ି (ଉପରକୁ) ଉଭୟ ଦିଗରେ ସ୍ଥାନାନ୍ତରିତ କରେ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # 8. Medium - Analyze
    q.append({
        "question_id": "q_ch03_c0008_08",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "ପବନରେ ଗଛର ଡାଳ ଓ ପତ୍ର ଭାଙ୍ଗି ନଯାଇ ସହଜରେ ନଇଁପଡ଼ିବାର ନମନୀୟତା (flexibility) କେଉଁ ଟିସ୍ୟୁ ଯୋଗୁଁ ସମ୍ଭବ ହୁଏ?",
        "options": [
            {"index": 0, "text_or": "କୋଲେନକାଇମା ଟିସ୍ୟୁ (Collenchyma)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ସ୍କ୍ଲେରେନକାଇମା ଟିସ୍ୟୁ", "misconception_tag": "confusing_rigidity_with_flexibility", "explanation_or": "ସ୍କ୍ଲେରେନକାଇମା କଠିନ ଓ ଭଙ୍ଗୁର, ନମନୀୟ ନୁହେଁ।"},
            {"index": 2, "text_or": "ଜାଇଲମ ଭେସେଲ", "misconception_tag": "confusing_water_pipe_with_flexibility", "explanation_or": "ଜାଇଲମ ଜଳ ପରିବହନ ପାଇଁ ଉଦ୍ଦିଷ୍ଟ।"},
            {"index": 3, "text_or": "କେବଳ ଏୟାରେନକାଇମା", "misconception_tag": "confusing_buoyancy_with_flexibility", "explanation_or": "ଏୟାରେନକାଇମା ଜଳଜ ଉଦ୍ଭିଦକୁ ଭାସିବାକୁ ସାହାଯ୍ୟ କରେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "କୋଲେନକାଇମା କୋଷର କୋଣଗୁଡ଼ିକରେ ପେକ୍ଟିନ ଜମା ଥିବାରୁ ଏହା ଉଦ୍ଭିଦର ଅଙ୍ଗକୁ ବିନା ଭାଙ୍ଗିବାରେ ନମନୀୟତା ଓ ଯାନ୍ତ୍ରିକ ସହାୟତା ଦିଏ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # 9. Hard - Evaluate
    q.append({
        "question_id": "q_ch03_c0008_09",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ଯଦି ଏକ ବଡ଼ ଗଛର କାଣ୍ଡରୁ ଫ୍ଲୋଏମ ସ୍ତରକୁ ଚାରିପାଖରୁ ଏକ ରିଙ୍ଗ ଆକାରରେ କାଟି କାଢ଼ିଦିଆଯାଏ (Girdling experiment), ତେବେ ଗଛଟିର କେଉଁ ଅଂଶ ପ୍ରଥମେ ମୃତ୍ୟୁବରଣ କରିବ?",
        "options": [
            {"index": 0, "text_or": "ମୂଳ (Roots) ପ୍ରଥମେ ମରିବ କାରଣ ପତ୍ରରୁ ଖାଦ୍ୟ ମୂଳ ପର୍ଯ୍ୟନ୍ତ ପହଞ୍ଚିପାରିବ ନାହିଁ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ପତ୍ର ପ୍ରଥମେ ମରିବ କାରଣ ଫ୍ଲୋଏମ ପାଣି ବୁହାଉଥିଲା", "misconception_tag": "confusing_phloem_with_water_conduction", "explanation_or": "ଜାଇଲମ ଅକ୍ଷୁଣ୍ଣ ଥିବାରୁ ପତ୍ର ପାଣି ପାଇଚାଲିବ।"},
            {"index": 2, "text_or": "ଗଛଟି ଅଧିକ ଫଳ ଦେବ", "misconception_tag": "assuming_injury_enhances_yield", "explanation_or": "ଶେଷରେ ସମଗ୍ର ଗଛ ମରିଯିବ।"},
            {"index": 3, "text_or": "କୌଣସି ଅଂଶ ମରିବ ନାହିଁ କାରଣ ଫ୍ଲୋଏମ ଏକ ଅଦରକାରୀ ଟିସ୍ୟୁ", "misconception_tag": "denying_phloem_vital_importance", "explanation_or": "ଫ୍ଲୋଏମ ବିନା ଖାଦ୍ୟ ସ୍ଥାନାନ୍ତର ଅସମ୍ଭବ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଜାଇଲମ ଅକ୍ଷୁଣ୍ଣ ଥିବାରୁ ପତ୍ରକୁ ଜଳ ଯିବ, ମାତ୍ର ଫ୍ଲୋଏମ କଟିଯିବାରୁ ପତ୍ର ପ୍ରସ୍ତୁତ ଖାଦ୍ୟ ତଳକୁ ଯାଇପାରିବ ନାହିଁ; ଫଳରେ ମୂଳ ଭୋକରେ ପ୍ରଥମେ ମରିଯିବ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # 10. Hard - Evaluate
    q.append({
        "question_id": "q_ch03_c0008_10",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ଜାଇଲମ ପାରେନକାଇମା ଏବଂ ଜାଇଲମ ଭେସେଲ ମଧ୍ୟରେ କୋଷୀୟ ଜୀବନ୍ତତା (cellular viability) ସମ୍ବନ୍ଧୀୟ କେଉଁ ବିଚାରଟି ସଠିକ୍?",
        "options": [
            {"index": 0, "text_or": "ଜାଇଲମ ପାରେନକାଇମା ହେଉଛି ଜାଇଲମର ଏକମାତ୍ର ଜୀବନ୍ତ ଉପାଦାନ, ଅନ୍ୟ ସମସ୍ତ (ଟ୍ରାକିଡ, ଭେସେଲ, ତନ୍ତୁ) ମୃତ କୋଷ ଅଟନ୍ତି", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଜାଇଲମର ସମସ୍ତ ଚାରୋଟି ଯାକ ଉପାଦାନ ସର୍ବଦା ଜୀବନ୍ତ ଥାଆନ୍ତି", "misconception_tag": "assuming_all_xylem_cells_are_living", "explanation_or": "ଜାଇଲମର ଅଧିକାଂଶ କୋଷ ମୃତ ହୋଇଥାନ୍ତି।"},
            {"index": 2, "text_or": "ଭେସେଲ ଜୀବନ୍ତ କିନ୍ତୁ ପାରେନକାଇମା ମୃତ", "misconception_tag": "reversing_xylem_cell_viability", "explanation_or": "ଭେସେଲରେ କୋଷଜୀବକ ନଥାଏ, ଏହା ମୃତ।"},
            {"index": 3, "text_or": "ଜାଇଲମରେ କୌଣସି କୋଷୀୟ ଗଠନ ନଥାଏ", "misconception_tag": "denying_cellular_nature_of_xylem", "explanation_or": "ଜାଇଲମ କୋଷମାନଙ୍କ ବିଶେଷୀକୃତ ସମଷ୍ଟି।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଜାଇଲମର ୪ଟି ଉପାଦାନ ମଧ୍ୟରୁ କେବଳ ଜାଇଲମ ପାରେନକାଇମା ଜୀବନ୍ତ ରହି ଖାଦ୍ୟ ସଂଚୟ ଓ ପାର୍ଶ୍ୱୀୟ ଜଳ ପରିବହନ କରେ; ବାକି ୩ଟି ମୃତ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # 11. Hard - Create
    q.append({
        "question_id": "q_ch03_c0008_11",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ଉଦ୍ଭିଦରେ ଜାଇଲମ ଦ୍ୱାରା ଜଳ ପରିବହନ ପରୀକ୍ଷାମୂଳକ ଭାବେ ପ୍ରମାଣ କରିବା ପାଇଁ ଆପଣ ଏକ ଧଳା ଫୁଲ ଥିବା ଡାଳ (ଯଥା ବାଲସମ୍) କୁ କିପରି ସଜାଇବେ?",
        "options": [
            {"index": 0, "text_or": "ଲାଲ ଇଙ୍କ ବା ଇଓସିନ୍ ମିଶା ପାଣିରେ ଡାଳଟିକୁ କିଛି ଘଣ୍ଟା ବୁଡ଼ାଇ ରଖି କାଣ୍ଡ କାଟି ଜାଇଲମ ଲାଲ ରଙ୍ଗ ହୋଇଥିବା ଦେଖାଇବା", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଡାଳଟିକୁ ଗରମ ତେଲରେ ଭାଜି ଦେଖିବା", "misconception_tag": "destructive_botanical_test", "explanation_or": "ଏଥିରେ କୋଷ ନଷ୍ଟ ହୋଇଯିବ ଏବଂ ଜଳ ପରିବହନ ଦେଖାଯିବ ନାହିଁ।"},
            {"index": 2, "text_or": "ପତ୍ରଗୁଡ଼ିକୁ କଳା ରଙ୍ଗରେ ବୋଳି ଅନ୍ଧାରରେ ରଖିବା", "misconception_tag": "confusing_with_starch_test", "explanation_or": "ଏହା ଆଲୋକଶ୍ଳେଷଣ ପରୀକ୍ଷା ପାଇଁ ବ୍ୟବହୃତ ହୁଏ।"},
            {"index": 3, "text_or": "ଡାଳକୁ ଶୁଖିଲା ବାଲିରେ ପୋତି ରଖିବା", "misconception_tag": "preventing_water_uptake", "explanation_or": "ଶୁଖିଲା ବାଲିରେ ଜଳ ପରିବହନ ହୋଇପାରିବ ନାହିଁ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ରଙ୍ଗୀନ ପାଣି ଜାଇଲମ ନଳୀ ଦେଇ ଉପରକୁ ଉଠି ଫୁଲ ଓ ପତ୍ରର ଶିରାପ୍ରଶିରାକୁ ଲାଲ କରିଦିଏ, ଯାହା ଜାଇଲମର ଜଳ ପରିବହନ କାର୍ଯ୍ୟକୁ ପ୍ରମାଣ କରେ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # 12. Hard - Create
    q.append({
        "question_id": "q_ch03_c0008_12",
        "concept_id": "c0008",
        "chapter_id": "ch003",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ମରୁଭୂମିରେ ବଢୁଥିବା କ୍ୟାକଟସ୍ (Xerophytic plants) ର ପତ୍ର କଣ୍ଟାରେ ରୂପାନ୍ତରିତ ହେବା ଏବଂ କାଣ୍ଡ ସବୁଜ ଓ ମୋଟା ହେବା ପଛରେ କେଉଁ ଟିସ୍ୟୁଗତ ରୂପାନ୍ତରଣ ଯୋଜନା କରାଯାଇଛି?",
        "options": [
            {"index": 0, "text_or": "ବାଷ୍ପମୋଚନ ରୋକିବା ପାଇଁ ପତ୍ର ସଂକୁଚିତ ହୋଇଛି ଏବଂ କାଣ୍ଡର ପାରେନକାଇମା କ୍ଲୋରୋଫିଲ ଯୁକ୍ତ ହୋଇ ଜଳ ସଂଚୟ ଓ ଆଲୋକଶ୍ଳେଷଣ କରୁଛି", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "କ୍ୟାକଟସରେ କୌଣସି ଟିସ୍ୟୁ ନଥାଏ, ଏହା ଏକ ପଥର ସଦୃଶ", "misconception_tag": "denying_cactus_biology", "explanation_or": "କ୍ୟାକଟସ୍ ଏକ ସଜୀବ ଉଦ୍ଭିଦ।"},
            {"index": 2, "text_or": "କଣ୍ଟାଗୁଡ଼ିକ ମାଟିରୁ ସିଧା ବାୟୁ ଶୋଷଣ କରନ୍ତି", "misconception_tag": "attributing_root_function_to_spines", "explanation_or": "କଣ୍ଟା ସୁରକ୍ଷା ଓ ଜଳକ୍ଷୟ ରୋକିବା ପାଇଁ ଅଟେ।"},
            {"index": 3, "text_or": "କାଣ୍ଡଟି ସମ୍ପୂର୍ଣ୍ଣ ରକ୍ତ କଣିକାରେ ଭର୍ତ୍ତି ଥାଏ", "misconception_tag": "attributing_blood_to_plants", "explanation_or": "ଉଦ୍ଭିଦରେ ରକ୍ତ ନଥାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "କ୍ୟାକଟସ୍‌ରେ କ୍ଲୋରେନକାଇମା ଯୁକ୍ତ ମାଂସଳ କାଣ୍ଡ ଖାଦ୍ୟ ତିଆରି ଓ ଜଳ ସଂଚୟ କରେ ଏବଂ କଣ୍ଟା ଉତ୍ସ୍ୱେଦନ ହାରକୁ ସର୍ବନିମ୍ନ କରିଦିଏ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.2",
        "revision": 1,
        "status": "active"
    })

    # ------------------------------------------------------------------------
    # CONCEPT c0009: Animal Tissues (ପ୍ରାଣୀ ଟିସ୍ୟୁ)
    # ------------------------------------------------------------------------
    # 1. Easy - Remember
    q.append({
        "question_id": "q_ch03_c0009_01",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "ପ୍ରାଣୀ ଶରୀରର ବାହ୍ୟ ପୃଷ୍ଠ ଏବଂ ଆଭ୍ୟନ୍ତରୀଣ ଅଙ୍ଗର ଆସ୍ତରଣ ସୃଷ୍ଟି କରୁଥିବା ସୁରକ୍ଷାକାରୀ ଟିସ୍ୟୁ କେଉଁଟି?",
        "options": [
            {"index": 0, "text_or": "ଏପିଥେଲିଆଲ ଟିସ୍ୟୁ (Epithelial tissue)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ସଂଯୋଜକ ଟିସ୍ୟୁ (Connective tissue)", "misconception_tag": "confusing_epithelium_with_connective", "explanation_or": "ସଂଯୋଜକ ଟିସ୍ୟୁ ଅଙ୍ଗମାନଙ୍କୁ ଯୋଡ଼ି ରଖେ।"},
            {"index": 2, "text_or": "ପେଶୀ ଟିସ୍ୟୁ (Muscular tissue)", "misconception_tag": "confusing_epithelium_with_muscle", "explanation_or": "ପେଶୀ ଟିସ୍ୟୁ ଚଳନ ପାଇଁ ଉଦ୍ଦିଷ୍ଟ।"},
            {"index": 3, "text_or": "ସ୍ନାୟୁ ଟିସ୍ୟୁ (Nervous tissue)", "misconception_tag": "confusing_epithelium_with_nervous", "explanation_or": "ସ୍ନାୟୁ ଟିସ୍ୟୁ ସନ୍ଦେଶ ପ୍ରେରଣ କରେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଏପିଥେଲିଆଲ ଟିସ୍ୟୁ ଶରୀର ଏବଂ ବିଭିନ୍ନ ଅଙ୍ଗଗହ୍ୱରକୁ ଆବୃତ କରି ବାହ୍ୟ ଆଘାତ ଓ ସଂକ୍ରମଣରୁ ସୁରକ୍ଷା ପ୍ରଦାନ କରେ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    # 2. Easy - Remember
    q.append({
        "question_id": "q_ch03_c0009_02",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "ସ୍ନାୟୁତନ୍ତ୍ରର ଗଠନମୂଳକ ଏବଂ କାର୍ଯ୍ୟକାରୀ ଏକକ (functional unit) କେଉଁଟି ଅଟେ?",
        "options": [
            {"index": 0, "text_or": "ନେଫ୍ରନ (Nephron)", "misconception_tag": "confusing_neuron_with_nephron", "explanation_or": "ନେଫ୍ରନ ହେଉଛି ବୃକ୍‌କର (kidney) କାର୍ଯ୍ୟକାରୀ ଏକକ।"},
            {"index": 1, "text_or": "ନ୍ୟୁରନ ବା ସ୍ନାୟୁକୋଷ (Neuron)", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ସାର୍କୋମିୟର", "misconception_tag": "confusing_neuron_with_muscle_unit", "explanation_or": "ଏହା ପେଶୀ ତନ୍ତୁର ଏକକ।"},
            {"index": 3, "text_or": "ଲିମ୍ଫୋସାଇଟ", "misconception_tag": "confusing_neuron_with_white_blood_cell", "explanation_or": "ଏହା ରକ୍ତର ଏକ ଶ୍ୱେତ ରକ୍ତକଣିକା।"}
        ],
        "correct_option": 1,
        "explanation_or": "ନ୍ୟୁରନ (Neuron) ବା ସ୍ନାୟୁକୋଷ ହେଉଛି ସ୍ନାୟୁତନ୍ତ୍ରର ମୂଳ କାର୍ଯ୍ୟକାରୀ ଏକକ ଯାହା ସ୍ନାୟୁ ଆବେଗ ସଞ୍ଚାଳନ କରେ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    # 3. Easy - Understand
    q.append({
        "question_id": "q_ch03_c0009_03",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "understand",
        "qtype": "mcq",
        "prompt_or": "ଐଚ୍ଛିକ ପେଶୀ (Voluntary muscle) ଏବଂ ଅନୈଚ୍ଛିକ ପେଶୀ (Involuntary muscle) ମଧ୍ୟରେ ମୁଖ୍ୟ ପାର୍ଥକ୍ୟ କଣ?",
        "options": [
            {"index": 0, "text_or": "ଐଚ୍ଛିକ ପେଶୀ ଆମ ଇଚ୍ଛାଧୀନ ଭାବେ ସଙ୍କୋଚିତ ହୁଏ (ଯଥା ହାତର ପେଶୀ), କିନ୍ତୁ ଅନୈଚ୍ଛିକ ପେଶୀ ଆମ ଇଚ୍ଛା ବିନା ସ୍ୱତଃ କାର୍ଯ୍ୟ କରେ (ଯଥା ଖାଦ୍ୟନଳୀ)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଐଚ୍ଛିକ ପେଶୀରେ କୌଣସି ରକ୍ତ ପ୍ରବାହ ନଥାଏ", "misconception_tag": "assuming_voluntary_muscle_lacks_blood", "explanation_or": "ପେଶୀକୁ ପ୍ରଚୁର ରକ୍ତ ସଞ୍ଚାଳନ ଦରକାର ହୁଏ।"},
            {"index": 2, "text_or": "ଅନୈଚ୍ଛିକ ପେଶୀ କେବଳ ମୃତ ଶରୀରରେ କାର୍ଯ୍ୟ କରେ", "misconception_tag": "confusing_involuntary_with_dead", "explanation_or": "ଜୀବନ୍ତ ଶରୀରରେ ଅନୈଚ୍ଛିକ ପେଶୀ ନିରନ୍ତର କାର୍ଯ୍ୟ କରେ।"},
            {"index": 3, "text_or": "ଐଚ୍ଛିକ ପେଶୀ କେବେହେଲେ ଥକିପଡ଼େ ନାହିଁ", "misconception_tag": "attributing_fatigue_resistance_to_skeletal_muscle", "explanation_or": "ଐଚ୍ଛିକ ପେଶୀ ଲାକ୍ଟିକ ଏସିଡ ଜମିଲେ ଶୀଘ୍ର ଥକିଯାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଆମ ନିୟନ୍ତ୍ରଣରେ ଥିବା ପେଶୀ ଐଚ୍ଛିକ (ରେଖିତ) ଏବଂ ଅନ୍ତରଙ୍ଗ ଅଙ୍ଗରେ ସ୍ୱୟଂଚାଳିତ ଭାବେ କାର୍ଯ୍ୟ କରୁଥିବା ପେଶୀ ଅନୈଚ୍ଛିକ (ଅଣରେଖିତ) ଅଟେ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    # 4. Easy - Understand
    q.append({
        "question_id": "q_ch03_c0009_04",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "understand",
        "qtype": "mcq",
        "prompt_or": "ଗୋଟିଏ ନ୍ୟୁରନରେ ସନ୍ଦେଶ ଗ୍ରହଣ କରିବା ଏବଂ ସନ୍ଦେଶ ପ୍ରେରଣ କରିବା କାର୍ଯ୍ୟ କେଉଁ ଅଂଶଗୁଡ଼ିକ ଦ୍ୱାରା ହୋଇଥାଏ?",
        "options": [
            {"index": 0, "text_or": "ଡେଣ୍ଡ୍ରାଇଟ ସନ୍ଦେଶ ଗ୍ରହଣ କରେ ଏବଂ ଆକ୍ସନ ସନ୍ଦେଶ ପ୍ରେରଣ କରେ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଆକ୍ସନ ସନ୍ଦେଶ ଗ୍ରହଣ କରେ ଏବଂ ଡେଣ୍ଡ୍ରାଇଟ ପ୍ରେରଣ କରେ", "misconception_tag": "reversing_dendrite_axon_signal_direction", "explanation_or": "ସନ୍ଦେଶ ସର୍ବଦା ଡେଣ୍ଡ୍ରାଇଟ୍‌ରୁ କୋଷକାୟ ଦେଇ ଆକ୍ସନ୍ ଆଡ଼କୁ ଯାଏ।"},
            {"index": 2, "text_or": "କେବଳ ନ୍ୟୁକ୍ଲିୟସ ହିଁ ସିଧାସଳଖ ଶରୀର ସାରା ଦୌଡ଼ିଥାଏ", "misconception_tag": "believing_nucleus_migrates", "explanation_or": "ନ୍ୟୁକ୍ଲିୟସ କୋଷକାୟ ଭିତରେ ସ୍ଥିର ରହେ।"},
            {"index": 3, "text_or": "ରକ୍ତ କଣିକା ସ୍ନାୟୁ ସନ୍ଦେଶ ବହନ କରନ୍ତି", "misconception_tag": "confusing_blood_with_nerve_impulse", "explanation_or": "ସ୍ନାୟୁ ସନ୍ଦେଶ ବିଦ୍ୟୁତ୍-ରାସାୟନିକ ଆବେଗ ଆକାରରେ ନ୍ୟୁରନ ଦ୍ୱାରା ପ୍ରବାହିତ ହୁଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଡେଣ୍ଡ୍ରାଇଟ (Dendrite) ଉଦ୍ଦୀପନା ଗ୍ରହଣ କରି କୋଷକାୟକୁ ପଠାଏ ଏବଂ ଆକ୍ସନ (Axon) ତାହାକୁ ଅନ୍ୟ ନ୍ୟୁରନ ବା ପେଶୀକୁ ପ୍ରେରଣ କରେ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    # 5. Medium - Apply
    q.append({
        "question_id": "q_ch03_c0009_05",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "ପାଟିର ଭିତର ପାର୍ଶ୍ୱ ଗାଲର ଆସ୍ତରଣ ଏବଂ ଖାଦ୍ୟନଳୀର ଭିତର ପୃଷ୍ଠରେ କେଉଁ ପ୍ରକାରର ଏପିଥେଲିଆଲ ଟିସ୍ୟୁ ଦେଖାଯାଏ?",
        "options": [
            {"index": 0, "text_or": "ଚଟକା ବା ସ୍କ୍ୱାମସ୍ ଏପିଥେଲିୟମ୍ (Squamous epithelium)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ସ୍ତମ୍ଭାକାର ଏପିଥେଲିୟମ୍", "misconception_tag": "confusing_squamous_with_columnar", "explanation_or": "ସ୍ତମ୍ଭାକାର ଏପିଥେଲିୟମ୍ ଅନ୍ତ୍ରନଳୀରେ ଶୋଷଣ କାର୍ଯ୍ୟ କରେ।"},
            {"index": 2, "text_or": "ଘନାକାର ଏପିଥେଲିୟମ୍", "misconception_tag": "confusing_squamous_with_cuboidal", "explanation_or": "ଘନାକାର ବୃକ୍‌କ ନଳୀରେ ଥାଏ।"},
            {"index": 3, "text_or": "ପେଶୀ ତନ୍ତୁ", "misconception_tag": "confusing_epithelial_lining_with_muscle", "explanation_or": "ଆସ୍ତରଣ ଏପିଥେଲିଆଲ ଟିସ୍ୟୁ ଦ୍ୱାରା ଗଠିତ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ପତଳା ଓ ଚେପ୍ଟା କୋଷବିଶିଷ୍ଟ ସ୍କ୍ୱାମସ୍ ଏପିଥେଲିୟମ୍ ମୁଖଗହ୍ୱର, ଗାଲ ଏବଂ ଖାଦ୍ୟନଳୀର ଭିତର ଆସ୍ତରଣ ସୃଷ୍ଟି କରି ଘର୍ଷଣରୁ ରକ୍ଷା କରେ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    # 6. Medium - Apply
    q.append({
        "question_id": "q_ch03_c0009_06",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "ଦୁଇଟି ଅସ୍ଥିକୁ (Bone to Bone) ପରସ୍ପର ସହିତ ଯୋଡ଼ି ରଖୁଥିବା ଟିସ୍ୟୁକୁ କଣ କୁହାଯାଏ?",
        "options": [
            {"index": 0, "text_or": "ଲିଗାମେଣ୍ଟ ବା ଅସ୍ଥିବନ୍ଧନୀ (Ligament)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଟେଣ୍ଡନ୍ ବା କଣ୍ଡରା (Tendon)", "misconception_tag": "confusing_ligament_with_tendon", "explanation_or": "ଟେଣ୍ଡନ୍ ମାଂସପେଶୀକୁ ଅସ୍ଥି ସହିତ ଯୋଡ଼ିଥାଏ।"},
            {"index": 2, "text_or": "ଏରିଓଲାର ଟିସ୍ୟୁ", "misconception_tag": "confusing_ligament_with_areolar", "explanation_or": "ଏରିଓଲାର ଚର୍ମ ଓ ମାଂସପେଶୀ ମଝିରେ ଖାଲି ସ୍ଥାନ ପୂରଣ କରେ।"},
            {"index": 3, "text_or": "ମେଦ ଟିସ୍ୟୁ", "misconception_tag": "confusing_ligament_with_adipose", "explanation_or": "ମେଦ ଟିସ୍ୟୁ ଚର୍ବି ସଂଚୟ କରେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଲିଗାମେଣ୍ଟ ଏକ ଖୁବ୍ ନମନୀୟ ସଂଯୋଜକ ଟିସ୍ୟୁ ଯାହା ଅସ୍ଥିକୁ ଅନ୍ୟ ଅସ୍ଥି ସହିତ ସଂଯୋଗ କରି ଗଣ୍ଠିକୁ ସ୍ଥିର ରଖେ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    # 7. Medium - Analyze
    q.append({
        "question_id": "q_ch03_c0009_07",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "ହୃତ୍‌ପିଣ୍ଡର ପେଶୀ (Cardiac muscle) ଜୀବନସାରା ବିନା ଥକିପଡ଼ି ଅବିରତ ସଙ୍କୋଚିତ ଓ ପ୍ରସାରିତ ହୋଇପାରିବାର କାରଣ କଣ?",
        "options": [
            {"index": 0, "text_or": "ଏହାର କୋଷଗୁଡ଼ିକ ଶାଖାଯୁକ୍ତ, ପ୍ରଚୁର ମାଇଟୋକଣ୍ଡ୍ରିଆ ବିଶିଷ୍ଟ ଏବଂ ଇଣ୍ଟରକାଲେଟେଡ୍ ଡିସ୍କ ଦ୍ୱାରା ଦ୍ରୁତ ସମନ୍ୱୟ ରକ୍ଷା କରନ୍ତି", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଏହା କେବଳ ଚର୍ବି ଦ୍ୱାରା ତିଆରି ହୋଇଥାଏ", "misconception_tag": "assuming_cardiac_muscle_is_fat", "explanation_or": "ହୃତ୍‌ପିଣ୍ଡ ସମ୍ପୂର୍ଣ୍ଣ ରୂପେ ଶକ୍ତିଶାଳୀ ପେଶୀ ଟିସ୍ୟୁରେ ଗଠିତ।"},
            {"index": 2, "text_or": "ହୃତ୍‌ପିଣ୍ଡରେ କୌଣସି ଶକ୍ତି ବ୍ୟୟ ହୁଏ ନାହିଁ", "misconception_tag": "violating_energy_conservation_in_heart", "explanation_or": "ହୃତ୍‌ପିଣ୍ଡ ପ୍ରଚୁର ATP ଶକ୍ତି ବ୍ୟବହାର କରେ।"},
            {"index": 3, "text_or": "ହୃତ୍‌ପିଣ୍ଡ ପ୍ରତି ୫ ମିନିଟରେ ୨ ମିନିଟ ପାଇଁ ଶୋଇପଡ଼େ", "misconception_tag": "assuming_heart_sleeps_cyclically", "explanation_or": "ହୃତ୍‌ପିଣ୍ଡ ନିରନ୍ତର ସ୍ପନ୍ଦିତ ହୁଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ହୃତ୍‌ପେଶୀ ଅନୈଚ୍ଛିକ, ଶାଖାନ୍ୱିତ ଏବଂ ପ୍ରଚୁର ରକ୍ତ ସଞ୍ଚାଳନ ସହ ଅମ୍ଳଜାନ ପାଉଥିବାରୁ ଏଥିରେ କେବେହେଲେ ଲାକ୍ଟିକ ଏସିଡ ଜମି କ୍ଳାନ୍ତି ଆସେ ନାହିଁ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    # 8. Medium - Analyze
    q.append({
        "question_id": "q_ch03_c0009_08",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "ରକ୍ତରେ ଥିବା ବିଭିନ୍ନ ଉପାଦାନ ଏବଂ ସେମାନଙ୍କ କାର୍ଯ୍ୟର କେଉଁ ଯୋଡ଼ିଟି ସଠିକ୍ ଭାବେ ମେଳ ଖାଉଛି?",
        "options": [
            {"index": 0, "text_or": "ଲୋହିତ ରକ୍ତକଣିକା (RBC): ଅମ୍ଳଜାନ ପରିବହନ, ଶ୍ୱେତ ରକ୍ତକଣିକା (WBC): ରୋଗ ପ୍ରତିରୋଧ, ଅଣୁଚକ୍ରିକା (Platelets): ରକ୍ତ ଜମାଟ ବାନ୍ଧିବା", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "RBC: ରୋଗ ପ୍ରତିରୋଧ, WBC: ରକ୍ତ ଜମାଟ, Platelets: ଅମ୍ଳଜାନ", "misconception_tag": "scrambling_blood_cell_functions", "explanation_or": "ହିମୋଗ୍ଲୋବିନ RBC ରେ ଥାଏ ଯାହା ଅମ୍ଳଜାନ ବହନ କରେ।"},
            {"index": 2, "text_or": "ପ୍ଲାଜମା କେବଳ ହାଡ଼ ତିଆରି କରେ", "misconception_tag": "confusing_plasma_with_bone_matrix", "explanation_or": "ପ୍ଲାଜମା ରକ୍ତର ତରଳ ମାତୃକା ଅଟେ।"},
            {"index": 3, "text_or": "ରକ୍ତ କୌଣସି ପଦାର୍ଥ ପରିବହନ କରେ ନାହିଁ", "misconception_tag": "denying_transport_function_of_blood", "explanation_or": "ରକ୍ତ ହର୍ମୋନ, ଖାଦ୍ୟ ଓ ଗ୍ୟାସ ପରିବହନ କରେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "RBC ହିମୋଗ୍ଲୋବିନ ଦ୍ୱାରା O₂ ନିଏ, WBC ଜୀବାଣୁ ମାରି ରୋଗ ପ୍ରତିରୋଧ କରେ ଏବଂ ପ୍ଲେଟଲେଟ୍ କ୍ଷତ ସ୍ଥାନରେ ରକ୍ତ ଜମାଟ ବାନ୍ଧେ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    # 9. Hard - Evaluate
    q.append({
        "question_id": "q_ch03_c0009_09",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ବୃଦ୍ଧାବସ୍ଥାରେ ଗଣ୍ଠିବାତ (Osteoarthritis) ରୋଗରେ ଗଣ୍ଠିରେ ଅସହ୍ୟ ଯନ୍ତ୍ରଣା ହେବାର ପ୍ରକୃତ କାରଣ କେଉଁ ଟିସ୍ୟୁର କ୍ଷୟ ଯୋଗୁଁ ଘଟେ ବୋଲି ଆପଣ ମୂଲ୍ୟାୟନ କରିବେ?",
        "options": [
            {"index": 0, "text_or": "ଅସ୍ଥିର ମୁଣ୍ଡରେ ଥିବା ଚିକ୍କଣ ତରୁଣାସ୍ଥି (Cartilage) କ୍ଷୟ ହୋଇଯିବା ଫଳରେ ଅସ୍ଥିଗୁଡ଼ିକ ପରସ୍ପର ସହିତ ଘଷି ହୁଅନ୍ତି", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଶରୀରର ସମସ୍ତ ସ୍ନାୟୁ ଛିଣ୍ଡିଯିବା ଯୋଗୁଁ", "misconception_tag": "assuming_complete_nerve_severing", "explanation_or": "ଏହା ସ୍ନାୟୁ ଛିଣ୍ଡିବା ରୋଗ ନୁହେଁ।"},
            {"index": 2, "text_or": "ମାଂସପେଶୀ ହଠାତ୍ ଅସ୍ଥିରେ ପରିଣତ ହୋଇଯିବା ଯୋଗୁଁ", "misconception_tag": "assuming_muscle_ossification", "explanation_or": "ଏହା ସାଧାରଣ ବାର୍ଦ୍ଧକ୍ୟଜନିତ ଘଟଣା ନୁହେଁ।"},
            {"index": 3, "text_or": "ରକ୍ତରେ ଜଳର ପରିମାଣ ଶୂନ ହୋଇଯିବା ଯୋଗୁଁ", "misconception_tag": "assuming_complete_dehydration_of_blood", "explanation_or": "ରକ୍ତରେ ସର୍ବଦା ଜଳ ରହିଥାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ତରୁଣାସ୍ଥି (Cartilage) ଗଣ୍ଠି ପୃଷ୍ଠକୁ ଚିକ୍କଣ ରଖି ଘର୍ଷଣ ରୋକେ; ଏହାର କ୍ଷୟ ହେଲେ ଅସ୍ଥି ସିଧା ଘଷି ହୋଇ ଯନ୍ତ୍ରଣା ହୁଏ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    # 10. Hard - Evaluate
    q.append({
        "question_id": "q_ch03_c0009_10",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ଦୁଇଟି ନ୍ୟୁରନ ମଧ୍ୟବର୍ତ୍ତୀ ସାଇନାପ୍ସ (Synapse) ରେ ସ୍ନାୟୁ ସନ୍ଦେଶର ପ୍ରବାହ କେବଳ ଗୋଟିଏ ଦିଗରେ ହିଁ କାହିଁକି ସମ୍ଭବ ହୁଏ?",
        "options": [
            {"index": 0, "text_or": "କାରଣ ରାସାୟନିକ ନ୍ୟୁରୋଟ୍ରାନ୍ସମିଟର କେବଳ ଆକ୍ସନର ଶେଷ ଭାଗରୁ ହିଁ ନିର୍ଗତ ହୋଇ ଡେଣ୍ଡ୍ରାଇଟର ଗ୍ରାହକ ଦ୍ୱାରା ଗ୍ରହଣ ହୁଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "କାରଣ ମସ୍ତିଷ୍କ ଇଚ୍ଛାକୃତ ଭାବେ ରାସ୍ତା ବନ୍ଦ କରିଦିଏ", "misconception_tag": "attributing_conscious_traffic_control_to_brain", "explanation_or": "ଏହା ଏକ ଜୈବ-ରାସାୟନିକ ନିୟମ ଅଟେ।"},
            {"index": 2, "text_or": "କାରଣ ସ୍ନାୟୁରେ ଗୋଟିଏ ଦିଗରେ ଚୁମ୍ବକୀୟ ବଳ ଥାଏ", "misconception_tag": "confusing_synapse_with_magnetic_diode", "explanation_or": "ଏହା ଚୁମ୍ବକୀୟ ନୁହେଁ, ରାସାୟନିକ ସଞ୍ଚାଳନ ଅଟେ।"},
            {"index": 3, "text_or": "କାରଣ ଡେଣ୍ଡ୍ରାଇଟରେ କୌଣସି ରନ୍ଧ୍ର ନଥାଏ", "misconception_tag": "anatomical_misconception", "explanation_or": "ଡେଣ୍ଡ୍ରାଇଟ୍‌ରେ ନ୍ୟୁରୋଟ୍ରାନ୍ସମିଟର ପାଇଁ ରିସେପ୍ଟର ଥାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ସାଇନାପ୍ଟିକ୍ ଭେସିକିଲ କେବଳ ପ୍ରି-ସାଇନାପ୍ଟିକ୍ ଆକ୍ସନ ଅଗ୍ରରେ ଥାଏ, ତେଣୁ ସନ୍ଦେଶ ସର୍ବଦା ଆକ୍ସନରୁ ପରବର୍ତ୍ତୀ ଡେଣ୍ଡ୍ରାଇଟ ଆଡ଼କୁ ଏକମୁଖୀ ପ୍ରବାହିତ ହୁଏ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    # 11. Hard - Create
    q.append({
        "question_id": "q_ch03_c0009_11",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ଉତ୍ତପ୍ତ ପାତ୍ର ସ୍ପର୍ଶ କଲେ ହାତ ଆପେ ଆପେ ତୁରନ୍ତ ପଛକୁ ଘୁଞ୍ଚିଆସିବା (ପ୍ରତୀପ କ୍ରିୟା ବା Reflex Arc) ର ସଠିକ୍ ପଥଟି କିପରି ସଜ୍ଜିତ ହେବା ଉଚିତ?",
        "options": [
            {"index": 0, "text_or": "ଗ୍ରାହକ (ଚର୍ମ) → ସମ୍ବେଦୀ ସ୍ନାୟୁ → ସୁଷୁମ୍ନାକାଣ୍ଡ → ପ୍ରେରକ ସ୍ନାୟୁ → କାର୍ଯ୍ୟକାରୀ ଅଙ୍ଗ (ହାତର ପେଶୀ)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ପେଶୀ → ପ୍ରେରକ ସ୍ନାୟୁ → ମସ୍ତିଷ୍କ → ଚର୍ମ", "misconception_tag": "reversing_sensory_motor_pathway", "explanation_or": "ପ୍ରଥମେ ଚର୍ମରୁ ସମ୍ବେଦୀ ସ୍ନାୟୁ ସନ୍ଦେଶ ନିଏ।"},
            {"index": 2, "text_or": "ମସ୍ତିଷ୍କ → ଚର୍ମ → ରକ୍ତ → ପେଶୀ", "misconception_tag": "confusing_reflex_arc_with_brain_processing", "explanation_or": "ପ୍ରତୀପ କ୍ରିୟା ସୁଷୁମ୍ନାକାଣ୍ଡ ଦ୍ୱାରା ଦ୍ରୁତ ନିୟନ୍ତ୍ରିତ ହୁଏ।"},
            {"index": 3, "text_or": "ଚର୍ମ → ରକ୍ତକଣିକା → ହାଡ଼ → ପେଶୀ", "misconception_tag": "bypassing_nervous_system_in_reflex", "explanation_or": "ସ୍ନାୟୁତନ୍ତ୍ର ହିଁ ପ୍ରତୀପ କ୍ରିୟା ପରିଚାଳନା କରେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ରିଫ୍ଲେକ୍ସ ଆର୍କରେ ରିସେପ୍ଟରରୁ ସେନ୍ସରି ନ୍ୟୁରନ୍ ସୁଷୁମ୍ନାକାଣ୍ଡକୁ ସନ୍ଦେଶ ନିଏ ଏବଂ ମୋଟର ନ୍ୟୁରନ୍ ଇଫେକ୍ଟର ପେଶୀକୁ ସଙ୍କୋଚନ ନିର୍ଦ୍ଦେଶ ଦିଏ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    # 12. Hard - Create
    q.append({
        "question_id": "q_ch03_c0009_12",
        "concept_id": "c0009",
        "chapter_id": "ch003",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ଶରୀରର ସ୍ନାୟୁତନ୍ତ୍ରକୁ ଏକ ଟେଲିଫୋନ୍ ନେଟୱାର୍କ ସହ ତୁଳନା କଲେ, ମୁଖ୍ୟ ଟେଲିଫୋନ୍ ଏକ୍ସଚେଞ୍ଜ୍ ଏବଂ ସଂଯୋଗକାରୀ ତାର କେଉଁ କେଉଁ ଅଙ୍ଗ/ଟିସ୍ୟୁ ସହ ତୁଳନୀୟ?",
        "options": [
            {"index": 0, "text_or": "ମସ୍ତିଷ୍କ ଓ ସୁଷୁମ୍ନାକାଣ୍ଡ (କେନ୍ଦ୍ରୀୟ ଏକ୍ସଚେଞ୍ଜ୍) ଏବଂ ସ୍ନାୟୁର ଆକ୍ସନ ତନ୍ତୁ (ସଂଯୋଗକାରୀ ତାର)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ରକ୍ତ ନଳୀ (ଏକ୍ସଚେଞ୍ଜ୍) ଏବଂ ହାଡ଼ (ତାର)", "misconception_tag": "misidentifying_communication_tissue", "explanation_or": "ସନ୍ଦେଶ ସଞ୍ଚାଳନ ସ୍ନାୟୁ ଟିସ୍ୟୁର କାର୍ଯ୍ୟ।"},
            {"index": 2, "text_or": "ଫୁସଫୁସ୍ (ଏକ୍ସଚେଞ୍ଜ୍) ଏବଂ ଶ୍ୱାସନଳୀ (ତାର)", "misconception_tag": "confusing_respiratory_with_nervous", "explanation_or": "ଫୁସଫୁସ୍ ଶ୍ୱାସକ୍ରିୟା କରେ।"},
            {"index": 3, "text_or": "ଯକୃତ (ଏକ୍ସଚେଞ୍ଜ୍) ଏବଂ ପିତ୍ତକୋଷ (ତାର)", "misconception_tag": "confusing_digestive_with_nervous", "explanation_or": "ଯକୃତ ପାଚନ ଅଙ୍ଗ ଅଟେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ମସ୍ତିଷ୍କ ଓ ସୁଷୁମ୍ନାକାଣ୍ଡ ସୂଚନା ପ୍ରକ୍ରିୟାକରଣ କେନ୍ଦ୍ର ଭାବେ ଏବଂ ଆକ୍ସନ ତନ୍ତୁ ବିଦ୍ୟୁତ୍-ରାସାୟନିକ ତାର ଭାବେ ସନ୍ଦେଶ ପ୍ରେରଣ କରନ୍ତି।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch03 §6.3",
        "revision": 1,
        "status": "active"
    })

    return q
