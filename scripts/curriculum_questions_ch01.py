# Chapter 1: Matter in Our Surroundings Questions
# Concepts: c0001 (States of Matter), c0002 (Density), c0003 (Changes of State)
# Each concept has 12 questions: 4 easy, 4 medium, 4 hard.
# Bloom levels cover: remember, understand, apply, analyze, evaluate, create.

def get_ch01_questions():
    q = []
    
    # ------------------------------------------------------------------------
    # CONCEPT c0001: States of Matter (ପଦାର୍ଥର ସ୍ଥିତି)
    # ------------------------------------------------------------------------
    # 1. Easy - Remember
    q.append({
        "question_id": "q_ch01_c0001_01",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "କଠିନ ପଦାର୍ଥର ନିମ୍ନଲିଖିତ ମଧ୍ୟରୁ କେଉଁଟି ଏକ ପ୍ରମୁଖ ବୈଶିଷ୍ଟ୍ୟ ଅଟେ?",
        "options": [
            {"index": 0, "text_or": "ନିର୍ଦ୍ଦିଷ୍ଟ ଆକାର ନାହିଁ କିନ୍ତୁ ଆୟତନ ଅଛି", "misconception_tag": "confusing_solid_with_liquid", "explanation_or": "ଏହା ତରଳ ପଦାର୍ଥର ଧର୍ମ, କଠିନ ପଦାର୍ଥର ନୁହେଁ।"},
            {"index": 1, "text_or": "ଆକାର ଓ ଆୟତନ କୌଣସିଟି ନିର୍ଦ୍ଦିଷ୍ଟ ନୁହେଁ", "misconception_tag": "confusing_solid_with_gas", "explanation_or": "ଏହା ଗ୍ୟାସୀୟ ପଦାର୍ଥର ଲକ୍ଷଣ ଅଟେ।"},
            {"index": 2, "text_or": "ନିର୍ଦ୍ଦିଷ୍ଟ ଆକାର ଓ ନିର୍ଦ୍ଦିଷ୍ଟ ଆୟତନ ଉଭୟ ଥାଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 3, "text_or": "ଏହାକୁ ସହଜରେ ଚାପ ପ୍ରୟୋଗ କରି ସଙ୍କୁଚିତ କରାଯାଇପାରେ", "misconception_tag": "confusing_compressibility", "explanation_or": "କଠିନ ପଦାର୍ଥ ସହଜରେ ସଙ୍କୁଚିତ ହୁଏ ନାହିଁ।"}
        ],
        "correct_option": 2,
        "explanation_or": "କଠିନ ପଦାର୍ଥର କଣିକାଗୁଡ଼ିକ ଅତି ନିକଟରେ ଥିବାରୁ ଏହାର ଏକ ନିର୍ଦ୍ଦିଷ୍ଟ ଆକାର ଏବଂ ନିର୍ଦ୍ଦିଷ୍ଟ ଆୟତନ ଥାଏ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # 2. Easy - Remember
    q.append({
        "question_id": "q_ch01_c0001_02",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "ତରଳ ପଦାର୍ଥର ଆକାର ଓ ଆୟତନ ସମ୍ପର୍କରେ କେଉଁ କଥାଟି ସତ୍ୟ?",
        "options": [
            {"index": 0, "text_or": "ଏହାର ନିର୍ଦ୍ଦିଷ୍ଟ ଆୟତନ ଥାଏ କିନ୍ତୁ ନିର୍ଦ୍ଦିଷ୍ଟ ଆକାର ନଥାଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଏହାର ନିର୍ଦ୍ଦିଷ୍ଟ ଆକାର ଥାଏ କିନ୍ତୁ ନିର୍ଦ୍ଦିଷ୍ଟ ଆୟତନ ନଥାଏ", "misconception_tag": "reversing_shape_volume", "explanation_or": "ତରଳ ପାତ୍ରର ଆକାର ନିଏ, ତେଣୁ ଏହାର ନିଜସ୍ୱ ଆକାର ନାହିଁ।"},
            {"index": 2, "text_or": "ଏହାର ଆକାର ଓ ଆୟତନ ଉଭୟ ନିର୍ଦ୍ଦିଷ୍ଟ", "misconception_tag": "confusing_liquid_with_solid", "explanation_or": "ଉଭୟ ନିର୍ଦ୍ଦିଷ୍ଟ ଥିବା କେବଳ କଠିନ ପଦାର୍ଥର ଧର୍ମ।"},
            {"index": 3, "text_or": "ଏହାର କୌଣସି ନିର୍ଦ୍ଦିଷ୍ଟ ଭୌତିକ ସୀମା ନଥାଏ", "misconception_tag": "confusing_liquid_with_gas", "explanation_or": "ତରଳର ମୁକ୍ତ ଉପରିଭାଗ ସୀମା ଥାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ତରଳ ପଦାର୍ଥର ନିର୍ଦ୍ଦିଷ୍ଟ ଆୟତନ ଥାଏ, ମାତ୍ର ଏହାକୁ ଯେଉଁ ପାତ୍ରରେ ରଖାଯାଏ ତାହାର ଆକାର ଧାରଣ କରେ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # 3. Easy - Understand
    q.append({
        "question_id": "q_ch01_c0001_03",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "understand",
        "qtype": "mcq",
        "prompt_or": "ଗ୍ୟାସୀୟ ପଦାର୍ଥ ପାତ୍ରର କାନ୍ଥ ଉପରେ ଚାପ କାହିଁକି ପ୍ରୟୋଗ କରେ?",
        "options": [
            {"index": 0, "text_or": "ଗ୍ୟାସ କଣିକାଗୁଡ଼ିକ ସ୍ଥିର ରହୁଥିବାରୁ", "misconception_tag": "believing_gas_is_stationary", "explanation_or": "ଗ୍ୟାସ କଣିକା କେବେ ସ୍ଥିର ରହନ୍ତି ନାହିଁ, ସେମାନେ ଦ୍ରୁତ ଗତିଶୀଳ।"},
            {"index": 1, "text_or": "କଣିକାଗୁଡ଼ିକ ଦ୍ରୁତ ଗତି କରି ପାତ୍ର କାନ୍ଥରେ ଧକ୍କା ଖାଉଥିବାରୁ", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "କଣିକାମାନଙ୍କ ମଧ୍ୟରେ ଆକର୍ଷଣ ବଳ ବହୁତ ଅଧିକ ଥିବାରୁ", "misconception_tag": "overestimating_intermolecular_force", "explanation_or": "ଗ୍ୟାସରେ ଆକର୍ଷଣ ବଳ ଅତି ନଗଣ୍ୟ ଥାଏ।"},
            {"index": 3, "text_or": "ଗ୍ୟାସର ବସ୍ତୁତ୍ୱ ଅତ୍ୟଧିକ ଭାରୀ ହୋଇଥିବାରୁ", "misconception_tag": "confusing_mass_with_pressure", "explanation_or": "ଚାପ କଣିକାମାନଙ୍କ ନିରନ୍ତର ଧକ୍କା ଯୋଗୁଁ ସୃଷ୍ଟି ହୁଏ, ଭାର ଯୋଗୁଁ ନୁହେଁ।"}
        ],
        "correct_option": 1,
        "explanation_or": "ଗ୍ୟାସ କଣିକାଗୁଡ଼ିକ ଉଚ୍ଚ ଗତିଜ ଶକ୍ତି ସହ ଦ୍ରୁତ ଗତି କରି ପାତ୍ରର ଭିତର କାନ୍ଥ ଉପରେ ନିରନ୍ତର ଆଘାତ କରି ଚାପ ସୃଷ୍ଟି କରନ୍ତି।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # 4. Easy - Understand
    q.append({
        "question_id": "q_ch01_c0001_04",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "understand",
        "qtype": "mcq",
        "prompt_or": "କଠିନ, ତରଳ ଓ ଗ୍ୟାସ ମଧ୍ୟରେ ଆନ୍ତଃକଣିକା ଆକର୍ଷଣ ବଳର ସଠିକ୍ କ୍ରମ କେଉଁଟି?",
        "options": [
            {"index": 0, "text_or": "କଠିନ > ତରଳ > ଗ୍ୟାସ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଗ୍ୟାସ > ତରଳ > କଠିନ", "misconception_tag": "reversing_force_order", "explanation_or": "ଗ୍ୟାସରେ ଆକର୍ଷଣ ବଳ ସବୁଠାରୁ କମ୍, ସର୍ବାଧିକ ନୁହେଁ।"},
            {"index": 2, "text_or": "ତରଳ > କଠିନ > ଗ୍ୟାସ", "misconception_tag": "overestimating_liquid_force", "explanation_or": "କଠିନରେ କଣିକା ଅତି ନିକଟରେ ଥିବାରୁ ତାର ବଳ ତରଳ ଅପେକ୍ଷା ଅଧିକ।"},
            {"index": 3, "text_or": "ସମସ୍ତଙ୍କ କ୍ଷେତ୍ରରେ ସମାନ ଥାଏ", "misconception_tag": "assuming_uniform_forces", "explanation_or": "ଭିନ୍ନ ଅବସ୍ଥାରେ ଆନ୍ତଃକଣିକା ବଳ ସମ୍ପୂର୍ଣ୍ଣ ଭିନ୍ନ ହୋଇଥାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "କଠିନରେ ଆନ୍ତଃକଣିକା ଆକର୍ଷଣ ବଳ ସର୍ବାଧିକ, ତରଳରେ ମଧ୍ୟମ ଏବଂ ଗ୍ୟାସରେ ସବୁଠାରୁ କମ୍ ଥାଏ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # 5. Medium - Apply
    q.append({
        "question_id": "q_ch01_c0001_05",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "ରୋଷେଇ ଗ୍ୟାସ ସିଲିଣ୍ଡର (LPG) ରେ ବହୁତ ପରିମାଣର ଗ୍ୟାସକୁ କିପରି ସୀମିତ ଜାଗାରେ ଭର୍ତ୍ତି କରାଯାଇଥାଏ?",
        "options": [
            {"index": 0, "text_or": "କଠିନ ଅବସ୍ଥାକୁ ରୂପାନ୍ତରିତ କରି", "misconception_tag": "assuming_solidification", "explanation_or": "LPG କୁ କଠିନ କରାଯାଏ ନାହିଁ, ଚାପ ଦେଇ ତରଳ କରାଯାଏ।"},
            {"index": 1, "text_or": "ଉଚ୍ଚ ଚାପ ପ୍ରୟୋଗ କରି ସଙ୍କୁଚିତ କରାଯାଇ ତରଳ ରୂପରେ", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ଅତ୍ୟଧିକ ଗରମ କରି କଣିକା ସଂଖ୍ୟା କମାଇ", "misconception_tag": "heating_causes_expansion", "explanation_or": "ଗରମ କଲେ ଗ୍ୟାସ ପ୍ରସାରିତ ହୋଇ ଫାଟିଯିବାର ଆଶଙ୍କା ଥାଏ।"},
            {"index": 3, "text_or": "ସିଲିଣ୍ଡର ଭିତରେ ଶୂନ୍ୟସ୍ଥାନ ସୃଷ୍ଟି କରି", "misconception_tag": "confusing_vacuum", "explanation_or": "ଶୂନ୍ୟସ୍ଥାନ ଗ୍ୟାସ ଭର୍ତ୍ତି କରିବା ପ୍ରକ୍ରିୟା ନୁହେଁ।"}
        ],
        "correct_option": 1,
        "explanation_or": "ଗ୍ୟାସର ଉଚ୍ଚ ସଙ୍କୋଚନଶୀଳତା ଧର୍ମ ଯୋଗୁଁ ଉଚ୍ଚ ଚାପ ପ୍ରୟୋଗ କରି ବିପୁଳ ପରିମାଣର ଗ୍ୟାସକୁ ତରଳୀକୃତ କରି ସିଲିଣ୍ଡରରେ ରଖାଯାଏ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # 6. Medium - Apply
    q.append({
        "question_id": "q_ch01_c0001_06",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "ସ୍ପଞ୍ଜ (sponge) ଏକ କଠିନ ପଦାର୍ଥ ହେଲେ ମଧ୍ୟ ଏହାକୁ ହାତରେ ଚିପିଦେଲେ ସଙ୍କୁଚିତ ହୁଏ କାହିଁକି?",
        "options": [
            {"index": 0, "text_or": "ଏହା ଏକ ତରଳ ପଦାର୍ଥର ମିଶ୍ରଣ ଅଟେ", "misconception_tag": "misclassifying_state", "explanation_or": "ସ୍ପଞ୍ଜ ସମ୍ପୂର୍ଣ୍ଣ ରୂପେ ଏକ କଠିନ ପଦାର୍ଥ।"},
            {"index": 1, "text_or": "ଏହାର କ୍ଷୁଦ୍ର ରନ୍ଧ୍ର ମଧ୍ୟରେ ଥିବା ବାୟୁ ବାହାରିଯାଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ଏହାର କଠିନ କଣିକାଗୁଡ଼ିକ ତରଳି ଯାଆନ୍ତି", "misconception_tag": "assuming_phase_change", "explanation_or": "ଚାପ ଦେଲେ ସ୍ପଞ୍ଜ ତରଳେ ନାହିଁ।"},
            {"index": 3, "text_or": "ସ୍ପଞ୍ଜର କୌଣସି ବସ୍ତୁତ୍ୱ ନଥାଏ", "misconception_tag": "denying_matter_nature", "explanation_or": "ପ୍ରତ୍ୟେକ ପଦାର୍ଥର ନିର୍ଦ୍ଦିଷ୍ଟ ବସ୍ତୁତ୍ୱ ଥାଏ।"}
        ],
        "correct_option": 1,
        "explanation_or": "ସ୍ପଞ୍ଜରେ ଅନେକ ସୂକ୍ଷ୍ମ ରନ୍ଧ୍ର ଥାଏ ଯେଉଁଥିରେ ବାୟୁ ଥାଏ; ଚାପ ଦେବା ଫଳରେ ସେହି ବାୟୁ ବାହାରିଯାଇ ଏହା ସଙ୍କୁଚିତ ହୁଏ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # 7. Medium - Analyze
    q.append({
        "question_id": "q_ch01_c0001_07",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "ଲୁହା ଖଣ୍ଡ, ଜଳ ଏବଂ ଅମ୍ଳଜାନ ଗ୍ୟାସ ମଧ୍ୟରେ କଣିକାମାନଙ୍କ ଗତିଜ ଶକ୍ତିର ତୁଳନା କଲେ କେଉଁ ବିଶ୍ଳେଷଣଟି ସଠିକ୍?",
        "options": [
            {"index": 0, "text_or": "ଲୁହାର କଣିକାର ଗତିଜ ଶକ୍ତି ସର୍ବାଧିକ", "misconception_tag": "confusing_strength_with_kinetic_energy", "explanation_or": "କଠିନରେ କଣିକା କେବଳ ସ୍ପନ୍ଦିତ ହୁଅନ୍ତି, ସେମାନଙ୍କ ଗତିଜ ଶକ୍ତି ସର୍ବନିମ୍ନ।"},
            {"index": 1, "text_or": "ଅମ୍ଳଜାନ ଗ୍ୟାସର କଣିକାର ଗତିଜ ଶକ୍ତି ସର୍ବାଧିକ", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ଜଳର କଣିକାର ଗତିଜ ଶକ୍ତି ଅମ୍ଳଜାନଠାରୁ ଅଧିକ", "misconception_tag": "underestimating_gas_motion", "explanation_or": "ଗ୍ୟାସ କଣିକା ମୁକ୍ତ ଭାବେ ଉଚ୍ଚ ବେଗରେ ଗତି କରନ୍ତି।"},
            {"index": 3, "text_or": "ତିନୋଟି ଯାକର କଣିକାର ଗତିଜ ଶକ୍ତି ସର୍ବଦା ଶୂନ", "misconception_tag": "ignoring_particle_motion", "explanation_or": "ପରମଶୂନ୍ୟ ତାପମାତ୍ରା ବ୍ୟତୀତ ସବୁ ପଦାର୍ଥର କଣିକାର ଗତିଜ ଶକ୍ତି ଥାଏ।"}
        ],
        "correct_option": 1,
        "explanation_or": "ଗ୍ୟାସରେ ଆକର୍ଷଣ ବଳ ସର୍ବନିମ୍ନ ହୋଇଥିବାରୁ କଣିକାଗୁଡ଼ିକ ଦ୍ରୁତ ଗତି କରନ୍ତି ଏବଂ ସେମାନଙ୍କ ଗତିଜ ଶକ୍ତି ସର୍ବାଧିକ ଥାଏ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # 8. Medium - Analyze
    q.append({
        "question_id": "q_ch01_c0001_08",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "ପାଣିରେ ଏକ ବୁନ୍ଦା ଇଙ୍କ ପକାଇଲେ ତାହା ଆପେ ଆପେ ମିଶିଯାଏ, ଏଥିରୁ ପଦାର୍ଥ କଣିକା ସମ୍ବନ୍ଧରେ କଣ ଜଣାପଡ଼େ?",
        "options": [
            {"index": 0, "text_or": "ପଦାର୍ଥର କଣିକାଗୁଡ଼ିକ ନିରନ୍ତର ଗତିଶୀଳ ଅଟନ୍ତି", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ପାଣିରେ କୌଣସି ଆନ୍ତଃକଣିକା ସ୍ଥାନ ନଥାଏ", "misconception_tag": "denying_intermolecular_spaces", "explanation_or": "କଣିକା ମଧ୍ୟରେ ସ୍ଥାନ ଥିବାରୁ ହିଁ ଇଙ୍କ କଣିକା ପ୍ରବେଶ କରେ।"},
            {"index": 2, "text_or": "ଇଙ୍କ କଣିକାଗୁଡ଼ିକ କେବଳ ତଳେ ଜମା ହୋଇ ରହନ୍ତି", "misconception_tag": "ignoring_diffusion", "explanation_or": "ଇଙ୍କ ସମଗ୍ର ପାଣିରେ ବ୍ୟାପିଯାଏ, ଏହାକୁ ବ୍ୟାପନ କୁହାଯାଏ।"},
            {"index": 3, "text_or": "ଏହା କେବଳ ଉତ୍ତାପ ପ୍ରୟୋଗ କଲେ ହିଁ ସମ୍ଭବ ହୁଏ", "misconception_tag": "assuming_external_heat_required", "explanation_or": "କୋଠରୀ ତାପମାତ୍ରାରେ ମଧ୍ୟ ଆପେ ଆପେ ବ୍ୟାପନ ଘଟେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଏହି ଘଟଣା ପ୍ରମାଣ କରେ ଯେ ତରଳରେ ଥିବା କଣିକାଗୁଡ଼ିକ ନିରନ୍ତର ଗତି କରନ୍ତି ଏବଂ ପରସ୍ପର ମଧ୍ୟରେ ବ୍ୟାପି ଯାଆନ୍ତି (ବ୍ୟାପନ ପ୍ରକ୍ରିୟା)।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # 9. Hard - Evaluate
    q.append({
        "question_id": "q_ch01_c0001_09",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ଜଣେ ଛାତ୍ର କହିଲେ: 'ଗନ୍ଧବସ୍ତୁ (perfume) ବାୟୁରେ ମିଶି କୋଠରୀ ସାରା ବ୍ୟାପିବା ଏବଂ ପାଣିରେ ଚିନି ମିଳାଇବା ଉଭୟ ଏକା ନିୟମ ଅନୁସାରେ ଘଟେ।' ଏହି ଯୁକ୍ତିର ମୂଲ୍ୟାୟନ କର।",
        "options": [
            {"index": 0, "text_or": "ଯୁକ୍ତିଟି ସଠିକ୍, କାରଣ ଉଭୟ ଘଟଣା କଣିକାମାନଙ୍କ ସ୍ୱତଃସ୍ଫୂର୍ତ୍ତ ବ୍ୟାପନ (diffusion) ଧର୍ମ ଉପରେ ଆଧାରିତ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଯୁକ୍ତିଟି ଭୁଲ, କାରଣ ଗ୍ୟାସରେ ବ୍ୟାପନ ହୁଏ କିନ୍ତୁ ତରଳରେ ବ୍ୟାପନ ହୋଇପାରେ ନାହିଁ", "misconception_tag": "limiting_diffusion_to_gases", "explanation_or": "ତରଳ ପଦାର୍ଥରେ ମଧ୍ୟ କଣିକାମାନଙ୍କ ବ୍ୟାପନ ଘଟିଥାଏ।"},
            {"index": 2, "text_or": "ଯୁକ୍ତିଟି ଭୁଲ, କାରଣ ଚିନି ମିଳାଇବା ପାଇଁ ରାସାୟନିକ ପ୍ରତିକ୍ରିୟା ଘଟେ", "misconception_tag": "confusing_dissolution_with_chemical_rxn", "explanation_or": "ଚିନି ପାଣିରେ ମିଶିବା ଏକ ଭୌତିକ ପ୍ରକ୍ରିୟା, ରାସାୟନିକ ନୁହେଁ।"},
            {"index": 3, "text_or": "ଯୁକ୍ତିଟି ଅସମ୍ପୂର୍ଣ୍ଣ କାରଣ ପରଫ୍ୟୁମ ଏକ କଠିନ ପଦାର୍ଥ ଅଟେ", "misconception_tag": "misidentifying_perfume_state", "explanation_or": "ପରଫ୍ୟୁମ ବାଷ୍ପୀଭୂତ ହୋଇ ଗ୍ୟାସୀୟ ରୂପରେ ବାୟୁରେ ବ୍ୟାପେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଉଭୟ ଘଟଣା ବ୍ୟାପନ (diffusion) ର ଉଦାହରଣ, ଯେଉଁଥିରେ ପଦାର୍ଥର କଣିକାଗୁଡ଼ିକ ଉଚ୍ଚ ସାନ୍ଦ୍ରତା ବିଶିଷ୍ଟ ଅଞ୍ଚଳରୁ ନିମ୍ନ ସାନ୍ଦ୍ରତା ଆଡ଼କୁ ଆପେ ଆପେ ଗତି କରନ୍ତି।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # 10. Hard - Evaluate
    q.append({
        "question_id": "q_ch01_c0001_10",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ପଦାର୍ଥର କଣିକା ତତ୍ତ୍ୱ (particulate nature) ଆଧାରରେ ନିମ୍ନୋକ୍ତ ମଧ୍ୟରୁ କେଉଁ ପରୀକ୍ଷାମୂଳକ ନିଷ୍କର୍ଷଟି ସବୁଠାରୁ ଅଧିକ ଯୁକ୍ତିଯୁକ୍ତ?",
        "options": [
            {"index": 0, "text_or": "ପାଣିରେ ଲୁଣ ମିଶାଇଲେ ଜଳସ୍ତର ନ ବଢ଼ିବା ପ୍ରମାଣ କରେ ଯେ ଜଳ କଣିକା ମଧ୍ୟରେ ଫାଙ୍କା ସ୍ଥାନ ଅଛି", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଲୁଣ ମିଳାଇବା ପରେ ଜଳସ୍ତର ନ ବଢ଼ିବାର କାରଣ ଲୁଣର କୌଣସି ଆୟତନ ନାହିଁ", "misconception_tag": "denying_volume_of_solute", "explanation_or": "ଲୁଣ ଏକ କଠିନ ପଦାର୍ଥ ଏବଂ ଏହାର ଆୟତନ ରହିଛି।"},
            {"index": 2, "text_or": "କଠିନ ପଦାର୍ଥରେ କଣିକା ସମ୍ପୂର୍ଣ୍ଣ ଗତିହୀନ ହୋଇ ସ୍ଥିର ରହନ୍ତି", "misconception_tag": "assuming_zero_motion_in_solids", "explanation_or": "କଠିନର କଣିକା ନିଜ ସ୍ଥିତିରେ କମ୍ପନ କରନ୍ତି।"},
            {"index": 3, "text_or": "ଗ୍ୟାସ କଣିକା ମଧ୍ୟରେ କୌଣସି ଫାଙ୍କା ସ୍ଥାନ ନଥାଏ", "misconception_tag": "misunderstanding_gas_porosity", "explanation_or": "ଗ୍ୟାସରେ ଆନ୍ତଃକଣିକା ସ୍ଥାନ ସବୁଠାରୁ ଅଧିକ ଥାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ପାଣିରେ ଲୁଣ ମିଶିବା ପରେ ମୋଟ ଆୟତନ ନ ବଢ଼ିବା ଏହା ପ୍ରମାଣ କରେ ଯେ ଜଳ କଣିକାମାନଙ୍କ ମଧ୍ୟରେ ଥିବା ଆନ୍ତଃକଣିକା ସ୍ଥାନ ମଧ୍ୟରେ ଲୁଣ କଣିକା ପ୍ରବେଶ କରେ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # 11. Hard - Create
    q.append({
        "question_id": "q_ch01_c0001_11",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ଏକ ସିରିଞ୍ଜ ସାହାଯ୍ୟରେ କଠିନ, ତରଳ ଓ ଗ୍ୟାସର ସଙ୍କୋଚନଶୀଳତା ତୁଳନା କରିବା ପାଇଁ ଏକ ପରୀକ୍ଷା ପ୍ରସ୍ତୁତ କରାଗଲା। ପିଷ୍ଟନ ଉପରେ ଚାପ ପ୍ରୟୋଗ କଲେ କେଉଁ କ୍ରମରେ ପିଷ୍ଟନ ସର୍ବାଧିକରୁ ସର୍ବନିମ୍ନ ଦୂରତା ଗତି କରିବ?",
        "options": [
            {"index": 0, "text_or": "ଗ୍ୟାସ (ବାୟୁ) > ତରଳ (ଜଳ) > କଠିନ (ଚକ୍ ଗୁଣ୍ଡ)", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "କଠିନ (ଚକ୍ ଗୁଣ୍ଡ) > ତରଳ (ଜଳ) > ଗ୍ୟାସ (ବାୟୁ)", "misconception_tag": "reversing_compressibility", "explanation_or": "କଠିନରେ ଆଦୌ ସଙ୍କୋଚନ ହୁଏ ନାହିଁ, ଗ୍ୟାସରେ ସର୍ବାଧିକ ହୁଏ।"},
            {"index": 2, "text_or": "ତରଳ (ଜଳ) > ଗ୍ୟାସ (ବାୟୁ) > କଠିନ (ଚକ୍ ଗୁଣ୍ଡ)", "misconception_tag": "overestimating_liquid_compressibility", "explanation_or": "ଜଳ ଅସଙ୍କୋଚ୍ୟ ପ୍ରାୟ, ଗ୍ୟାସ ତୁଳନାରେ ଏହାର ସଙ୍କୋଚନ ନଗଣ୍ୟ।"},
            {"index": 3, "text_or": "ତିନୋଟି ଯାକ କ୍ଷେତ୍ରରେ ପିଷ୍ଟନ ସମାନ ଦୂରତା ଗତି କରିବ", "misconception_tag": "assuming_equal_compressibility", "explanation_or": "ପଦାର୍ଥର ଭିନ୍ନ ସ୍ଥିତିରେ ସଙ୍କୋଚନଶୀଳତା ସମ୍ପୂର୍ଣ୍ଣ ଭିନ୍ନ ହୋଇଥାଏ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଗ୍ୟାସରେ ଆନ୍ତଃକଣିକା ସ୍ଥାନ ସର୍ବାଧିକ ଥିବାରୁ ଏହା ସହଜରେ ସଙ୍କୁଚିତ ହୁଏ; ତରଳ ସାମାନ୍ୟ ଏବଂ କଠିନ ଆଦୌ ସଙ୍କୁଚିତ ହୁଏ ନାହିଁ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # 12. Hard - Create
    q.append({
        "question_id": "q_ch01_c0001_12",
        "concept_id": "c0001",
        "chapter_id": "ch001",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ପଦାର୍ଥର ତିନି ଅବସ୍ଥାରେ କଣିକାମାନଙ୍କ ଆଚରଣ ବୁଝାଇବା ପାଇଁ ଛାତ୍ରମାନଙ୍କ ଦ୍ୱାରା ଏକ ଅଭିନୟ ମଡେଲ ପ୍ରସ୍ତୁତ କରାଗଲା। କଠିନ ଅବସ୍ଥା ଦର୍ଶାଇବା ପାଇଁ ଛାତ୍ରମାନେ କିପରି ଠିଆ ହେବା ଉଚିତ?",
        "options": [
            {"index": 0, "text_or": "ଦୂରେଇ ରହି ମୁକ୍ତ ଭାବରେ ଦୌଡ଼ିବା", "misconception_tag": "representing_gas_as_solid", "explanation_or": "ଏହା ଗ୍ୟାସ କଣିକାମାନଙ୍କ ଗତିର ଉଦାହରଣ।"},
            {"index": 1, "text_or": "ପରସ୍ପର ହାତ ଧରି ପାଖାପାଖି ରହି ଧୀରେ ଧୀରେ ଘୁରିବା", "misconception_tag": "representing_liquid_as_solid", "explanation_or": "ଏହା ତରଳ ପଦାର୍ଥର ପ୍ରବାହଶୀଳତାକୁ ବୁଝାଏ।"},
            {"index": 2, "text_or": "ପରସ୍ପରକୁ ଜାବୁଡ଼ି ଧରି ଅତି ନିକଟରେ ରହି କେବଳ ନିଜ ସ୍ଥାନରେ କମ୍ପିତ ହେବା", "misconception_tag": None, "explanation_or": None},
            {"index": 3, "text_or": "ଏକାକୀ କୋଠରୀର ଚାରିକୋଣରେ ବସି ରହିବା", "misconception_tag": "isolating_particles", "explanation_or": "କଠିନରେ କଣିକାଗୁଡ଼ିକ ଏକତ୍ର ନିବିଡ଼ ଭାବେ ରହିଥାନ୍ତି।"}
        ],
        "correct_option": 2,
        "explanation_or": "କଠିନ ପଦାର୍ଥରେ କଣିକାଗୁଡ଼ିକ ଅତି ନିବିଡ଼ ଭାବେ ବାନ୍ଧି ହୋଇ ରହିଥାନ୍ତି ଏବଂ ସ୍ଥାନ ପରିବର୍ତ୍ତନ ନକରି କେବଳ ସ୍ପନ୍ଦିତ ହୁଅନ୍ତି।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.2",
        "revision": 1,
        "status": "active"
    })

    # ------------------------------------------------------------------------
    # CONCEPT c0002: Density (ଘନତ୍ୱ)
    # ------------------------------------------------------------------------
    # 1. Easy - Remember
    q.append({
        "question_id": "q_ch01_c0002_01",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "ଘନତ୍ୱ (Density) ର ଗାଣିତିକ ସୂତ୍ରଟି କଣ ଅଟେ?",
        "options": [
            {"index": 0, "text_or": "ଘନତ୍ୱ = ବସ୍ତୁତ୍ୱ × ଆୟତନ", "misconception_tag": "multiplying_mass_and_volume", "explanation_or": "ବସ୍ତୁତ୍ୱ ଓ ଆୟତନର ଗୁଣନଫଳ ଘନତ୍ୱ ନୁହେଁ।"},
            {"index": 1, "text_or": "ଘନତ୍ୱ = ବସ୍ତୁତ୍ୱ / ଆୟତନ", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ଘନତ୍ୱ = ଆୟତନ / ବସ୍ତୁତ୍ୱ", "misconception_tag": "inverting_density_ratio", "explanation_or": "ଆୟତନକୁ ବସ୍ତୁତ୍ୱ ଦ୍ୱାରା ଭାଗ କଲେ ଘନତ୍ୱ ମିଳେ ନାହିଁ।"},
            {"index": 3, "text_or": "ଘନତ୍ୱ = ବସ୍ତୁତ୍ୱ + ଆୟତନ", "misconception_tag": "adding_mass_and_volume", "explanation_or": "ଏକକ ଆୟତନର ବସ୍ତୁତ୍ୱ ହିଁ ଘନତ୍ୱ ଅଟେ, ଯୋଗଫଳ ନୁହେଁ।"}
        ],
        "correct_option": 1,
        "explanation_or": "ଘନତ୍ୱ = ବସ୍ତୁତ୍ୱ / ଆୟତନ (d = M / V), ଯାହା ଏକକ ଆୟତନର ବସ୍ତୁତ୍ୱକୁ ବୁଝାଏ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # 2. Easy - Remember
    q.append({
        "question_id": "q_ch01_c0002_02",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "ଆନ୍ତର୍ଜାତୀୟ SI ପଦ୍ଧତିରେ ଘନତ୍ୱର ଏକକ କଣ?",
        "options": [
            {"index": 0, "text_or": "କିଲୋଗ୍ରାମ (kg)", "misconception_tag": "confusing_density_with_mass", "explanation_or": "କିଲୋଗ୍ରାମ ହେଉଛି କେବଳ ବସ୍ତୁତ୍ୱର ଏକକ।"},
            {"index": 1, "text_or": "ମିଟର କ୍ୟୁବ (m³)", "misconception_tag": "confusing_density_with_volume", "explanation_or": "ମିଟର କ୍ୟୁବ ହେଉଛି ଆୟତନର ଏକକ।"},
            {"index": 2, "text_or": "କିଲୋଗ୍ରାମ ପ୍ରତି ଘନ ମିଟର (kg/m³)", "misconception_tag": None, "explanation_or": None},
            {"index": 3, "text_or": "ଗ୍ରାମ ପ୍ରତି ସେକେଣ୍ଡ (g/s)", "misconception_tag": "introducing_time_into_density", "explanation_or": "ଘନତ୍ୱରେ ସମୟର କୌଣସି ସମ୍ପର୍କ ନାହିଁ।"}
        ],
        "correct_option": 2,
        "explanation_or": "ବସ୍ତୁତ୍ୱ (kg) କୁ ଆୟତନ (m³) ଦ୍ୱାରା ଭାଗ କରାଯାଉଥିବାରୁ SI ଏକକ ହେଉଛି kg/m³।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # 3. Easy - Understand
    q.append({
        "question_id": "q_ch01_c0002_03",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "understand",
        "qtype": "short_answer",
        "prompt_or": "ଅପେକ୍ଷା ଘନତ୍ୱର ପରିଭାଷା ଲେଖ।",
        "rubric_or": "ପଦାର୍ଥ ଘନତ୍ୱ ଓ ଜଳ ଘନତ୍ୱର ଅନୁପାତ; ଏକକ ନାହିଁ।",
        "expected_concepts": [
            "relative density",
            "water",
            "ratio"
        ],
        "options": [],
        "correct_option": None,
        "explanation_or": "ଅପେକ୍ଷା ଘନତ୍ୱ ହେଉଛି ପଦାର୍ଥ ଘନତ୍ୱ ଓ ଜଳ ଘନତ୍ୱର ଅନୁପାତ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # 4. Easy - Understand
    q.append({
        "question_id": "q_ch01_c0002_04",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "understand",
        "qtype": "mcq",
        "prompt_or": "ଆପେକ୍ଷିକ ଘନତ୍ୱ (Relative Density) ର ଏକକ କଣ ଅଟେ?",
        "options": [
            {"index": 0, "text_or": "kg/m³", "misconception_tag": "confusing_relative_density_with_absolute", "explanation_or": "kg/m³ ହେଉଛି ସାଧାରଣ ଘନତ୍ୱର ଏକକ।"},
            {"index": 1, "text_or": "g/cm³", "misconception_tag": "confusing_cgs_density", "explanation_or": "g/cm³ CGS ପଦ୍ଧତିରେ ଘନତ୍ୱର ଏକକ।"},
            {"index": 2, "text_or": "ଏହାର କୌଣସି ଏକକ ନାହିଁ, ଏହା ଏକ ବିଶୁଦ୍ଧ ସଂଖ୍ୟା", "misconception_tag": None, "explanation_or": None},
            {"index": 3, "text_or": "ନ୍ୟୁଟନ (N)", "misconception_tag": "confusing_density_with_force", "explanation_or": "ନ୍ୟୁଟନ ହେଉଛି ବଳର ଏକକ।"}
        ],
        "correct_option": 2,
        "explanation_or": "ଆପେକ୍ଷିକ ଘନତ୍ୱ ହେଉଛି ଦୁଇଟି ସମାନ ରାଶିର (ବସ୍ତୁର ଘନତ୍ୱ ଓ ଜଳର ଘନତ୍ୱ) ଅନୁପାତ, ତେଣୁ ଏହାର କୌଣସି ଏକକ ନଥାଏ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # 5. Medium - Apply
    q.append({
        "question_id": "q_ch01_c0002_05",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "ଗୋଟିଏ ଧାତୁ ଖଣ୍ଡର ବସ୍ତୁତ୍ୱ ୫୦୦ ଗ୍ରାମ ଏବଂ ଆୟତନ ୧୦୦ ଘନ ସେଣ୍ଟିମିଟର (cm³) ହେଲେ, ତାର ଘନତ୍ୱ କେତେ ହେବ?",
        "options": [
            {"index": 0, "text_or": "୦.୨ g/cm³", "misconception_tag": "dividing_volume_by_mass", "explanation_or": "ଆୟତନକୁ ବସ୍ତୁତ୍ୱ ଦ୍ୱାରା ଭାଗ କରାଯାଇଛି, ଯାହା ଭୁଲ।"},
            {"index": 1, "text_or": "୫ g/cm³", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "୫୦,୦୦୦ g/cm³", "misconception_tag": "multiplying_mass_and_volume", "explanation_or": "ବସ୍ତୁତ୍ୱ ଏବଂ ଆୟତନକୁ ଗୁଣନ କରାଯାଇଛି।"},
            {"index": 3, "text_or": "୪୦୦ g/cm³", "misconception_tag": "subtracting_volume_from_mass", "explanation_or": "ବସ୍ତୁତ୍ୱରୁ ଆୟତନ ବିୟୋଗ କରାଯାଇଛି।"}
        ],
        "correct_option": 1,
        "explanation_or": "ଘନତ୍ୱ = ବସ୍ତୁତ୍ୱ / ଆୟତନ = ୫୦୦ / ୧୦୦ = ୫ g/cm³।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # 6. Medium - Apply
    q.append({
        "question_id": "q_ch01_c0002_06",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "ବରଫ ଜଳରେ କାହିଁକି ଭାସେ ଏବଂ ଏହାର ଘନତ୍ୱ ଜଳ ତୁଳନାରେ କିପରି ଥାଏ?",
        "options": [
            {"index": 0, "text_or": "ବରଫର ଘନତ୍ୱ ଜଳ ଅପେକ୍ଷା କମ୍ ଥାଏ କାରଣ ଜମାଟ ବାନ୍ଧିବା ବେଳେ ଏହାର ଆୟତନ ବଢ଼ିଯାଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ବରଫ କଠିନ ହୋଇଥିବାରୁ ଏହାର ଘନତ୍ୱ ସର୍ବଦା ଜଳଠାରୁ ଅଧିକ ଥାଏ", "misconception_tag": "assuming_all_solids_are_denser_than_liquids", "explanation_or": "ଜଳର ବ୍ୟତିକ୍ରମ ପ୍ରସାରଣ ଯୋଗୁଁ ବରଫର ଘନତ୍ୱ ଜଳଠାରୁ କମ୍ ହୁଏ।"},
            {"index": 2, "text_or": "ବରଫ ଭିତରେ ବାୟୁ ଶୂନ୍ୟ ଥିବାରୁ ଏହା ଭାସେ", "misconception_tag": "confusing_density_with_vacuum", "explanation_or": "ବରଫର ସ୍ଫଟିକ ଗଠନରେ ଖାଲି ଜାଗା ଥାଏ, ଶୂନ୍ୟତା ନୁହେଁ।"},
            {"index": 3, "text_or": "କେବଳ ସମୁଦ୍ର ପାଣିରେ ହିଁ ବରଫ ଭାସିଥାଏ", "misconception_tag": "limiting_buoyancy_to_seawater", "explanation_or": "ମିଠା ପାଣିରେ ମଧ୍ୟ ବରଫ ଭାସେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଜଳ ୦°C ରେ ବରଫ ହେବା ବେଳେ ପ୍ରସାରିତ ହୋଇ ତାର ଆୟତନ ବଢ଼ିଯାଏ, ତେଣୁ ଘନତ୍ୱ କମିଯାଇ ଏହା ପାଣିରେ ଭାସେ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # 7. Medium - Analyze
    q.append({
        "question_id": "q_ch01_c0002_07",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "ଗୋଟିଏ ଖୋଲା ପାତ୍ରରେ ଥିବା ବାୟୁକୁ ଗରମ କଲେ ତାର ଘନତ୍ୱ ଉପରେ କି ପ୍ରଭାବ ପଡ଼ିବ?",
        "options": [
            {"index": 0, "text_or": "ଘନତ୍ୱ ବୃଦ୍ଧି ପାଇବ କାରଣ ତାପମାତ୍ରା ବଢ଼ିଛି", "misconception_tag": "confusing_temperature_with_density", "explanation_or": "ଗରମ କଲେ ଗ୍ୟାସ ପ୍ରସାରିତ ହୁଏ, ଘନତ୍ୱ ବଢ଼େ ନାହିଁ।"},
            {"index": 1, "text_or": "ଘନତ୍ୱ ହ୍ରାସ ପାଇବ କାରଣ ପ୍ରସାରଣ ଯୋଗୁଁ ଏକକ ଆୟତନରେ ବାୟୁ କଣିକା ସଂଖ୍ୟା କମିଯିବ", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ଘନତ୍ୱ ଅପରିବର୍ତ୍ତିତ ରହିବ କାରଣ ବାୟୁର ବସ୍ତୁତ୍ୱ ସ୍ଥିର", "misconception_tag": "ignoring_gas_expansion", "explanation_or": "ଖୋଲା ପାତ୍ରରୁ ବାୟୁ ବାହାରିଯାଏ, ତେଣୁ ସେହି ସ୍ଥାନରେ ବସ୍ତୁତ୍ୱ କମିଯାଏ।"},
            {"index": 3, "text_or": "ପ୍ରଥମେ କମି ପରେ ଶୂନ ହୋଇଯିବ", "misconception_tag": "assuming_zero_density", "explanation_or": "କୌଣସି ପଦାର୍ଥର ଘନତ୍ୱ ଶୂନ ହୋଇପାରେ ନାହିଁ।"}
        ],
        "correct_option": 1,
        "explanation_or": "ଗରମ କଲେ ବାୟୁ ପ୍ରସାରିତ ହୋଇ ହାଲୁକା ହୁଏ ଏବଂ ଏହାର ଘନତ୍ୱ ହ୍ରାସ ପାଏ; ତେଣୁ ଉତ୍ତପ୍ତ ବାୟୁ ଉପରକୁ ଉଠିଯାଏ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # 8. Medium - Analyze
    q.append({
        "question_id": "q_ch01_c0002_08",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "ବସ୍ତୁତ୍ୱ-ଆୟତନ ଗ୍ରାଫ୍ (Mass-Volume graph) ରେ ଏକ ସରଳରେଖାର ଢାଳୁ ବା ସ୍ଲୋପ୍ (slope) କେଉଁ ଭୌତିକ ରାଶିକୁ ସୂଚାଏ?",
        "options": [
            {"index": 0, "text_or": "ବେଗ", "misconception_tag": "confusing_with_motion_graph", "explanation_or": "ବେଗ ହେଉଛି ଦୂରତା-ସମୟ ଗ୍ରାଫର ଢାଳୁ।"},
            {"index": 1, "text_or": "ତ୍ୱରଣ", "misconception_tag": "confusing_with_velocity_time_graph", "explanation_or": "ତ୍ୱରଣ ବେଗତା-ସମୟ ଗ୍ରାଫର ଢାଳୁ ଅଟେ।"},
            {"index": 2, "text_or": "ଘନତ୍ୱ", "misconception_tag": None, "explanation_or": None},
            {"index": 3, "text_or": "ଆପେକ୍ଷିକ ଗତି", "misconception_tag": "introducing_irrelevant_motion_concept", "explanation_or": "ଏଠାରେ ବସ୍ତୁତ୍ୱ ଓ ଆୟତନର ସମ୍ପର୍କ ଆଲୋଚିତ।"}
        ],
        "correct_option": 2,
        "explanation_or": "Mass-Volume ଗ୍ରାଫରେ Y-ଅକ୍ଷ ବସ୍ତୁତ୍ୱ ଏବଂ X-ଅକ୍ଷ ଆୟତନ ହେଲେ, slope = ΔM / ΔV = ଘନତ୍ୱ (Density)।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # 9. Hard - Evaluate
    q.append({
        "question_id": "q_ch01_c0002_09",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ଜଣେ କାରିଗର ଦାବି କଲେ ଯେ ତାଙ୍କ ତିଆରି ସୁନା ମୁକୁଟ ବିଶୁଦ୍ଧ ସୁନାରେ ତିଆରି। ମୁକୁଟର ବସ୍ତୁତ୍ୱ ୩୮୬ ଗ୍ରାମ ଓ ଆୟତନ ୨୫ cm³ ମପାଗଲା। ବିଶୁଦ୍ଧ ସୁନାର ଘନତ୍ୱ ୧୯.୩ g/cm³ ହୋଇଥିଲେ, ଏହି ଦାବିର ସତ୍ୟତା ମୂଲ୍ୟାୟନ କର।",
        "options": [
            {"index": 0, "text_or": "ଦାବିଟି ଭୁଲ, କାରଣ ମୁକୁଟର ଘନତ୍ୱ ୧୫.୪୪ g/cm³, ଯାହା ବିଶୁଦ୍ଧ ସୁନାଠାରୁ କମ୍", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଦାବିଟି ସଠିକ୍, କାରଣ ୩୮୬ ଗ୍ରାମ ବହୁତ ଭାରୀ", "misconception_tag": "judging_purity_by_mass_alone", "explanation_or": "କେବଳ ଭାରରୁ ବିଶୁଦ୍ଧତା ଜଣାପଡ଼େ ନାହିଁ, ଘନତ୍ୱ ନିର୍ଣ୍ଣୟ କରିବା ଆବଶ୍ୟକ।"},
            {"index": 2, "text_or": "ଦାବିଟି ସଠିକ୍, କାରଣ ସୁନାର ଆୟତନ ସର୍ବଦା ୨୫ cm³ ହୁଏ", "misconception_tag": "assuming_fixed_volume_for_element", "explanation_or": "ଆୟତନ ପଦାର୍ଥର ଆକାର ଉପରେ ନିର୍ଭର କରେ।"},
            {"index": 3, "text_or": "ଦାବି ସମ୍ପର୍କରେ କିଛି କହିହେବ ନାହିଁ କାରଣ ପାଣି ବିନା ପରୀକ୍ଷା ସମ୍ଭବ ନୁହେଁ", "misconception_tag": "believing_only_water_can_test_density", "explanation_or": "ସିଧାସଳଖ M/V ସୂତ୍ରରୁ ଘନତ୍ୱ ଗଣନା କରି ସତ୍ୟତା ଜାଣିହେବ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ମୁକୁଟର ଘନତ୍ୱ = ୩୮୬ / ୨୫ = ୧୫.୪୪ g/cm³, ଯାହା ବିଶୁଦ୍ଧ ସୁନାର ଘନତ୍ୱ (୧୯.୩ g/cm³) ଠାରୁ କମ୍। ତେଣୁ ଏଥିରେ ଅପମିଶ୍ରଣ ଅଛି।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # 10. Hard - Evaluate
    q.append({
        "question_id": "q_ch01_c0002_10",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ଶୀତ ପ୍ରଧାନ ଅଞ୍ଚଳରେ ହ୍ରଦର ଉପରିଭାଗ ବରଫ ପାଲଟିଗଲେ ମଧ୍ୟ ତଳେ ଥିବା ମାଛମାନେ କାହିଁକି ବଞ୍ଚି ରହନ୍ତି? ଜଳର କେଉଁ ଧର୍ମ ଏଥିପାଇଁ ଦାୟୀ?",
        "options": [
            {"index": 0, "text_or": "୪°C ରେ ଜଳର ଘନତ୍ୱ ସର୍ବାଧିକ ଥିବାରୁ ଏହି ତାପମାତ୍ରାର ଭାରୀ ଜଳ ତଳେ ରହି ଜୀବମାନଙ୍କୁ ସୁରକ୍ଷା ଦିଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ବରଫ ଅତ୍ୟନ୍ତ ଉତ୍ତପ୍ତ ହୋଇ ତଳ ଜଳକୁ ଗରମ ରଖେ", "misconception_tag": "believing_ice_produces_heat", "explanation_or": "ବରଫ ଥଣ୍ଡା, ତେବେ ଏହା ତାପ ଅନ୍ତରକ ଭାବେ କାର୍ଯ୍ୟ କରେ।"},
            {"index": 2, "text_or": "ମାଛମାନେ କଠିନ ବରଫ ଭିତରେ ଶ୍ୱାସକ୍ରିୟା କରିପାରନ୍ତି", "misconception_tag": "assuming_fish_breathe_in_ice", "explanation_or": "ମାଛ ତରଳ ଜଳରେ ଦ୍ରବୀଭୂତ ଅମ୍ଳଜାନ ନିଅନ୍ତି।"},
            {"index": 3, "text_or": "ସମସ୍ତ ଜଳ ଏକା ସାଙ୍ଗରେ ବରଫ ହୋଇପାରେ ନାହିଁ କାରଣ ପାଣିରେ ଲୁଣ ଥାଏ", "misconception_tag": "attributing_to_salinity_only", "explanation_or": "ଜଳର ବ୍ୟତିକ୍ରମ ପ୍ରସାରଣ ହିଁ ମୂଳ କାରଣ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଜଳର ଘନତ୍ୱ ୪°C ରେ ସର୍ବାଧିକ ହୋଇଥିବାରୁ ୪°C ର ଜଳ ହ୍ରଦର ତଳଭାଗରେ ରହେ ଏବଂ କମ୍ ଘନତ୍ୱ ବିଶିଷ୍ଟ ବରଫ ଉପରେ ଭାସି ତାପ ଅନ୍ତରକ ସାଜେ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # 11. Hard - Create
    q.append({
        "question_id": "q_ch01_c0002_11",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ଏକ ଅନିୟମିତ ଆକାରର ପଥର ଖଣ୍ଡର ଘନତ୍ୱ ନିର୍ଣ୍ଣୟ କରିବା ପାଇଁ ଆପଣ କେଉଁ ଉପକରଣ ଓ ପଦ୍ଧତିର ଯୋଜନା କରିବେ?",
        "options": [
            {"index": 0, "text_or": "ସ୍ପ୍ରିଙ୍ଗ ତୁଳା ଦ୍ୱାରା ବସ୍ତୁତ୍ୱ ଏବଂ ମାପକ ସିଲିଣ୍ଡରରେ ଜଳ ବିସ୍ଥାପନ ଦ୍ୱାରା ଆୟତନ ମାପି", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ସ୍କେଲ ସାହାଯ୍ୟରେ ଦୈର୍ଘ୍ୟ ଓ ପ୍ରସ୍ଥ ମାପି କ୍ଷେତ୍ରଫଳ ବାହାର କରି", "misconception_tag": "confusing_area_with_volume", "explanation_or": "ଅନିୟମିତ ପଥରର ଆୟତନ ସ୍କେଲରେ ମପାଯାଇପାରିବ ନାହିଁ।"},
            {"index": 2, "text_or": "ପଥରକୁ ଗରମ କରି ବାଷ୍ପ ବାହାର କରି", "misconception_tag": "confusing_heating_with_density", "explanation_or": "ଗରମ କଲେ ଆୟତନ ବା ବସ୍ତୁତ୍ୱ ନିର୍ଣ୍ଣୟ ହୁଏ ନାହିଁ।"},
            {"index": 3, "text_or": "କେବଳ ଏକ ଷ୍ଟପୱାଚ୍ ଦ୍ୱାରା ପାଣିରେ ବୁଡ଼ିବା ସମୟ ହିସାବ କରି", "misconception_tag": "confusing_falling_time_with_density", "explanation_or": "ବୁଡ଼ିବା ସମୟ ଘନତ୍ୱ ସୂତ୍ରରେ ଆସେ ନାହିଁ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ପଥରର ବସ୍ତୁତ୍ୱ ସ୍ପ୍ରିଙ୍ଗ ତୁଳା ଦ୍ୱାରା ଏବଂ ଆୟତନ ଜଳ ବିସ୍ଥାପନ ପଦ୍ଧତି ଦ୍ୱାରା ମାପି ଘନତ୍ୱ = M/V ସୂତ୍ରରୁ ନିର୍ଣ୍ଣୟ କରାଯାଏ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # 12. Hard - Create
    q.append({
        "question_id": "q_ch01_c0002_12",
        "concept_id": "c0002",
        "chapter_id": "ch001",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ତେଲ, ପାଣି ଏବଂ ମହୁ — ଏହି ତିନୋଟି ତରଳକୁ ନେଇ ଏକ 'ଘନତ୍ୱ ସ୍ତମ୍ଭ' (Density column) ତିଆରି କଲେ, ଉପରୁ ତଳ କ୍ରମରେ କିପରି ସ୍ତର ସଜ୍ଜିତ ହେବ?",
        "options": [
            {"index": 0, "text_or": "ମହୁ (ସବୁଠାରୁ ଉପରେ), ପାଣି (ମଝିରେ), ତେଲ (ତଳେ)", "misconception_tag": "reversing_density_stack", "explanation_or": "ଅଧିକ ଘନ ପଦାର୍ଥ ତଳେ ରହେ, ଉପରେ ନୁହେଁ।"},
            {"index": 1, "text_or": "ତେଲ (ସବୁଠାରୁ ଉପରେ), ପାଣି (ମଝିରେ), ମହୁ (ସବୁଠାରୁ ତଳେ)", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ପାଣି (ଉପରେ), ତେଲ (ମଝିରେ), ମହୁ (ତଳେ)", "misconception_tag": "confusing_oil_water_density", "explanation_or": "ତେଲର ଘନତ୍ୱ ପାଣିଠାରୁ କମ୍, ତେଣୁ ତେଲ ପାଣି ଉପରେ ଭାସେ।"},
            {"index": 3, "text_or": "ସମସ୍ତେ ସମ୍ପୂର୍ଣ୍ଣ ମିଶିଯାଇ ଏକକ ସ୍ତର ହୋଇଯିବେ", "misconception_tag": "assuming_all_liquids_are_miscible", "explanation_or": "ତେଲ ଏବଂ ଜଳ ଅମିଶ୍ରଣୀୟ ଏବଂ ଭିନ୍ନ ଘନତ୍ୱ ଯୋଗୁଁ ଅଲଗା ସ୍ତର ଗଠନ କରନ୍ତି।"}
        ],
        "correct_option": 1,
        "explanation_or": "ତେଲର ଘନତ୍ୱ ସର୍ବନିମ୍ନ ହୋଇଥିବାରୁ ଉପରେ ରହେ, ପାଣି ମଝିରେ ଏବଂ ସର୍ବାଧିକ ଘନତ୍ୱ ବିଶିଷ୍ଟ ମହୁ ତଳେ ରହେ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.3",
        "revision": 1,
        "status": "active"
    })

    # ------------------------------------------------------------------------
    # CONCEPT c0003: Changes of State (ଅବସ୍ଥା ପରିବର୍ତ୍ତନ)
    # ------------------------------------------------------------------------
    # 1. Easy - Remember
    q.append({
        "question_id": "q_ch01_c0003_01",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "ଏକ ବାୟୁମଣ୍ଡଳୀୟ ଚାପରେ ବରଫ ଯେଉଁ ତାପମାତ୍ରାରେ ତରଳି ଜଳରେ ପରିଣତ ହୁଏ ତାହାକୁ କଣ କୁହାଯାଏ?",
        "options": [
            {"index": 0, "text_or": "ସ୍ଫୁଟନାଙ୍କ (Boiling point)", "misconception_tag": "confusing_melting_with_boiling", "explanation_or": "ସ୍ଫୁଟନାଙ୍କ ହେଉଛି ତରଳ ବାଷ୍ପ ହେବାର ତାପମାତ୍ରା।"},
            {"index": 1, "text_or": "ଗଳନାଙ୍କ (Melting point)", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ହିମାଙ୍କ (Freezing point)", "misconception_tag": "confusing_melting_with_freezing", "explanation_or": "ହିମାଙ୍କ ହେଉଛି ତରଳ କଠିନ ହେବାର ତାପମାତ୍ରା।"},
            {"index": 3, "text_or": "ଊର୍ଦ୍ଧ୍ୱପାତନ ବିନ୍ଦୁ", "misconception_tag": "confusing_sublimation", "explanation_or": "ଏହା କଠିନରୁ ସିଧା ଗ୍ୟାସ ହେବାର ପ୍ରକ୍ରିୟା ନୁହେଁ।"}
        ],
        "correct_option": 1,
        "explanation_or": "ଯେଉଁ ନିର୍ଦ୍ଦିଷ୍ଟ ତାପମାତ୍ରାରେ କଠିନ ତରଳରେ ପରିଣତ ହୁଏ ତାହାକୁ ଗଳନାଙ୍କ କୁହାଯାଏ; ବରଫ ପାଇଁ ଏହା ୦°C।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    # 2. Easy - Remember
    q.append({
        "question_id": "q_ch01_c0003_02",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "remember",
        "qtype": "mcq",
        "prompt_or": "କଠିନ ପଦାର୍ଥ ତରଳ ଅବସ୍ଥାକୁ ନଯାଇ ସିଧାସଳଖ ଗ୍ୟାସୀୟ ଅବସ୍ଥାରେ ପରିଣତ ହେବା ପ୍ରକ୍ରିୟାକୁ କଣ କୁହାଯାଏ?",
        "options": [
            {"index": 0, "text_or": "ବାଷ୍ପୀଭବନ (Evaporation)", "misconception_tag": "confusing_sublimation_with_evaporation", "explanation_or": "ବାଷ୍ପୀଭବନରେ ତରଳ ପଦାର୍ଥ ଗ୍ୟାସରେ ପରିଣତ ହୁଏ।"},
            {"index": 1, "text_or": "ଘନୀଭବନ (Condensation)", "misconception_tag": "confusing_sublimation_with_condensation", "explanation_or": "ଘନୀଭବନ ହେଉଛି ଗ୍ୟାସରୁ ତରଳ ହେବା।"},
            {"index": 2, "text_or": "ଊର୍ଦ୍ଧ୍ୱପାତନ (Sublimation)", "misconception_tag": None, "explanation_or": None},
            {"index": 3, "text_or": "ତରଳୀକରଣ (Liquefaction)", "misconception_tag": "confusing_sublimation_with_liquefaction", "explanation_or": "ଏହା ଗ୍ୟାସରୁ ତରଳ ହେବା ପ୍ରକ୍ରିୟା।"}
        ],
        "correct_option": 2,
        "explanation_or": "କଠିନରୁ ସିଧାସଳଖ ବାଷ୍ପ ବା ଗ୍ୟାସ ହେବା ପ୍ରକ୍ରିୟାକୁ ଊର୍ଦ୍ଧ୍ୱପାତନ କୁହାଯାଏ (ଯଥା କର୍ପୂର, ଆମୋନିୟମ କ୍ଲୋରାଇଡ)।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    # 3. Easy - Understand
    q.append({
        "question_id": "q_ch01_c0003_03",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "understand",
        "qtype": "mcq",
        "prompt_or": "ବରଫ ତରଳିବା ସମୟରେ ତାପ ଯୋଗ କରାଗଲେ ମଧ୍ୟ ତାପମାତ୍ରା କାହିଁକି ବଢ଼େ ନାହିଁ?",
        "options": [
            {"index": 0, "text_or": "ଯୋଗ କରାଯାଉଥିବା ତାପ କଣିକାମାନଙ୍କ ଆନ୍ତଃକଣିକା ଆକର୍ଷଣ ବଳକୁ ଭାଙ୍ଗିବାରେ ବ୍ୟୟ ହୁଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ବରଫର ଥର୍ମୋମିଟର ଉପରେ କୌଣସି ପ୍ରଭାବ ପଡ଼େ ନାହିଁ", "misconception_tag": "blaming_measuring_instrument", "explanation_or": "ଥର୍ମୋମିଟର ସଠିକ୍ କାର୍ଯ୍ୟ କରେ, ତାପମାତ୍ରା ବାସ୍ତବରେ ସ୍ଥିର ଥାଏ।"},
            {"index": 2, "text_or": "ସମସ୍ତ ତାପ ବାୟୁମଣ୍ଡଳକୁ ତୁରନ୍ତ ଚାଲିଯାଏ", "misconception_tag": "assuming_immediate_heat_loss", "explanation_or": "ପାତ୍ର ଭିତରେ ଥିବା ବରଫ ହିଁ ସେହି ତାପ ଶକ୍ତି ଶୋଷଣ କରେ।"},
            {"index": 3, "text_or": "ବରଫ କେବଳ ଥଣ୍ଡା ତାପ ଶକ୍ତି ଗ୍ରହଣ କରେ", "misconception_tag": "believing_in_cold_energy", "explanation_or": "ବିଜ୍ଞାନରେ 'ଥଣ୍ଡା ଶକ୍ତି' ବୋଲି କିଛି ନାହିଁ, ତାପର ଅନୁପସ୍ଥିତି ହିଁ ଥଣ୍ଡା।"}
        ],
        "correct_option": 0,
        "explanation_or": "ଅବସ୍ଥା ପରିବର୍ତ୍ତନ ସମୟରେ ତାପ ଶକ୍ତି ଲୁକ୍କାୟିତ ଭାବେ କଣିକାମାନଙ୍କ ଆକର୍ଷଣ ଭାଙ୍ଗିବାରେ ଲାଗେ, ଯାହାକୁ ଗଳନର ଗୁପ୍ତତାପ କୁହାଯାଏ।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    # 4. Easy - Understand
    q.append({
        "question_id": "q_ch01_c0003_04",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "understand",
        "qtype": "mcq",
        "prompt_or": "ନିମ୍ନଲିଖିତ ମଧ୍ୟରୁ କେଉଁ କାରକଟି ବାଷ୍ପୀଭବନର (evaporation) ହାରକୁ ବୃଦ୍ଧି କରାଏ?",
        "options": [
            {"index": 0, "text_or": "ପୃଷ୍ଠତଳ କ୍ଷେତ୍ରଫଳ ବୃଦ୍ଧି", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ତାପମାତ୍ରା ହ୍ରାସ ପାଇବା", "misconception_tag": "cooling_increases_evaporation", "explanation_or": "ତାପମାତ୍ରା କମିଲେ ବାଷ୍ପୀଭବନ ହାର କମିଯାଏ।"},
            {"index": 2, "text_or": "ବାୟୁମଣ୍ଡଳରେ ଆର୍ଦ୍ରତା ବୃଦ୍ଧି ପାଇବା", "misconception_tag": "humidity_increases_evaporation", "explanation_or": "ବାୟୁରେ ଜଳୀୟବାଷ୍ପ ଅଧିକ ଥିଲେ ବାଷ୍ପୀଭବନ ଧୀର ହୁଏ।"},
            {"index": 3, "text_or": "ପବନର ବେଗ କମିଯିବା", "misconception_tag": "low_wind_increases_evaporation", "explanation_or": "ପବନ ବେଗ କମିଲେ ବାଷ୍ପୀଭବନ ହାର କମେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ପୃଷ୍ଠତଳ କ୍ଷେତ୍ରଫଳ ବଢ଼ିଲେ ଅଧିକ ସଂଖ୍ୟକ ତରଳ କଣିକା ବାୟୁ ସଂସ୍ପର୍ଶରେ ଆସି ବାଷ୍ପୀଭବନ ହାର ବଢ଼ାନ୍ତି (ଯଥା ଲୁଗା ମେଲାଇ ଶୁଖାଇବା)।",
        "difficulty": "easy",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    # 5. Medium - Apply
    q.append({
        "question_id": "q_ch01_c0003_05",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "ଗ୍ରୀଷ୍ମ ଋତୁରେ ମାଟିପାତ୍ରରେ (ସୁରେଇ ବା ମାଠିଆ) ରଖାଯାଇଥିବା ପାଣି ଥଣ୍ଡା ରହେ କାହିଁକି?",
        "options": [
            {"index": 0, "text_or": "ମାଟିପାତ୍ର ନିଜେ ଥଣ୍ଡା ଉତ୍ପାଦନ କରେ", "misconception_tag": "attributing_refrigeration_to_clay", "explanation_or": "ମାଟି ନିଜେ କୌଣସି ଶୀତଳତା ସୃଷ୍ଟି କରେ ନାହିଁ।"},
            {"index": 1, "text_or": "ସୂକ୍ଷ୍ମ ରନ୍ଧ୍ର ଦେଇ ଜଳ ନିର୍ଗତ ହୋଇ ବାଷ୍ପୀଭୂତ ହେବା ଫଳରେ ଶୀତଳତା ସୃଷ୍ଟି ହୁଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ମାଟିପାତ୍ର ଭିତରକୁ ଆଲୋକ ପ୍ରବେଶ କରେ ନାହିଁ", "misconception_tag": "blaming_absence_of_light", "explanation_or": "ଆଲୋକ ନ ପଡ଼ିବା ମୁଖ୍ୟ କାରଣ ନୁହେଁ।"},
            {"index": 3, "text_or": "ଜଳର ଗୁପ୍ତତାପ ଶୂନ ହୋଇଯାଏ", "misconception_tag": "assuming_zero_latent_heat", "explanation_or": "ଜଳ ପାତ୍ରରୁ ଗୁପ୍ତତାପ ଶୋଷଣ କରି ହିଁ ବାଷ୍ପୀଭୂତ ହୁଏ।"}
        ],
        "correct_option": 1,
        "explanation_or": "ମାଠିଆର ସୂକ୍ଷ୍ମ ରନ୍ଧ୍ର ଦେଇ ପାଣି ବାହାରକୁ ଆସି ବାଷ୍ପୀଭୂତ ହୁଏ ଏବଂ ଏଥିପାଇଁ ଆବଶ୍ୟକ ତାପ ପାଣିରୁ ଗ୍ରହଣ କରିବାରୁ ପାଣି ଥଣ୍ଡା ରହେ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    # 6. Medium - Apply
    q.append({
        "question_id": "q_ch01_c0003_06",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "apply",
        "qtype": "mcq",
        "prompt_or": "କୋଠରୀର ତାପମାତ୍ରା ୨୫ ଡିଗ୍ରୀ ସେଲସିୟସ (°C) ହେଲେ, କେଲଭିନ (Kelvin) ସ୍କେଲରେ ଏହାର ମାନ କେତେ ହେବ?",
        "options": [
            {"index": 0, "text_or": "୨୪୮ K", "misconception_tag": "subtracting_273", "explanation_or": "ସେଲସିୟସରୁ କେଲଭିନ କରିବା ପାଇଁ ୨୭୩ ଯୋଗ କରାଯାଏ, ବିୟୋଗ ନୁହେଁ।"},
            {"index": 1, "text_or": "୨୯୮ K", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "୩୦୦ K", "misconception_tag": "adding_275", "explanation_or": "ସଠିକ୍ ଯୋଗ ସଂଖ୍ୟା ହେଉଛି ୨୭୩।"},
            {"index": 3, "text_or": "-୨୪୮ K", "misconception_tag": "negative_kelvin_misconception", "explanation_or": "କେଲଭିନ ସ୍କେଲ କଦାପି ଋଣାତ୍ମକ ହୁଏ ନାହିଁ।"}
        ],
        "correct_option": 1,
        "explanation_or": "T(K) = T(°C) + ୨୭୩ = ୨୫ + ୨୭୩ = ୨୯୮ K।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    # 7. Medium - Analyze
    q.append({
        "question_id": "q_ch01_c0003_07",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "ବାଷ୍ପୀଭବନ (Evaporation) ଏବଂ ସ୍ଫୁଟନ (Boiling) ମଧ୍ୟରେ ମୁଖ୍ୟ ପାର୍ଥକ୍ୟ କଣ?",
        "options": [
            {"index": 0, "text_or": "ବାଷ୍ପୀଭବନ ଏକ ପୃଷ୍ଠୀୟ ଘଟଣା ଯାହା ଯେକୌଣସି ତାପମାତ୍ରାରେ ଘଟେ, କିନ୍ତୁ ସ୍ଫୁଟନ ଏକ ନିର୍ଦ୍ଦିଷ୍ଟ ତାପମାତ୍ରାରେ ସମଗ୍ର ତରଳରେ ଘଟେ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ବାଷ୍ପୀଭବନ କେବଳ ୧୦୦°C ରେ ଘଟେ କିନ୍ତୁ ସ୍ଫୁଟନ ୦°C ରେ ଘଟେ", "misconception_tag": "reversing_temperatures", "explanation_or": "ଜଳର ସ୍ଫୁଟନ ୧୦୦°C ରେ ଘଟେ, ୦°C ରେ ନୁହେଁ।"},
            {"index": 2, "text_or": "ସ୍ଫୁଟନରେ ଶୀତଳତା ସୃଷ୍ଟି ହୁଏ କିନ୍ତୁ ବାଷ୍ପୀଭବନରେ ତାପ ସୃଷ୍ଟି ହୁଏ", "misconception_tag": "reversing_cooling_effect", "explanation_or": "ବାଷ୍ପୀଭବନ ଶୀତଳତା ସୃଷ୍ଟି କରେ।"},
            {"index": 3, "text_or": "ଦୁହିଁଙ୍କ ମଧ୍ୟରେ କୌଣସି ପ୍ରକୃତ ପାର୍ଥକ୍ୟ ନାହିଁ", "misconception_tag": "treating_as_identical", "explanation_or": "ବାଷ୍ପୀଭବନ surface phenomenon ଏବଂ ସ୍ଫୁଟନ bulk phenomenon ଅଟେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ବାଷ୍ପୀଭବନ ସ୍ଫୁଟନାଙ୍କଠାରୁ କମ୍ ଯେକୌଣସି ତାପମାତ୍ରାରେ ତରଳର ଉପରିଭାଗରୁ ଘଟେ, ମାତ୍ର ସ୍ଫୁଟନ ନିର୍ଦ୍ଦିଷ୍ଟ ସ୍ଫୁଟନାଙ୍କରେ ସମଗ୍ର ତରଳ ଭିତରେ ଘଟେ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    # 8. Medium - Analyze
    q.append({
        "question_id": "q_ch01_c0003_08",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "analyze",
        "qtype": "mcq",
        "prompt_or": "୧୦୦°C ରେ ଥିବା ଫୁଟୁଥିବା ପାଣି ଅପେକ୍ଷା ୧୦୦°C ର ବାଷ୍ପ (steam) ଦ୍ୱାରା ଦେହ ଅଧିକ ଗଭୀର ଭାବେ ପୋଡ଼ିଯାଏ କାହିଁକି?",
        "options": [
            {"index": 0, "text_or": "ବାଷ୍ପର ତାପମାତ୍ରା ପାଣି ଅପେକ୍ଷା ୨୦୦°C ଅଧିକ ଥାଏ", "misconception_tag": "assuming_steam_has_higher_temperature", "explanation_or": "ଉଭୟଙ୍କ ତାପମାତ୍ରା ସମାନ ୧୦୦°C ହିଁ ଥାଏ।"},
            {"index": 1, "text_or": "ବାଷ୍ପ ମଧ୍ୟରେ ବାଷ୍ପୀଭବନର ଗୁପ୍ତତାପ ଆକାରରେ ଅଧିକ ତାପ ଶକ୍ତି ଥାଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ବାଷ୍ପରେ ଏକ ବିଷାକ୍ତ ଗ୍ୟାସ ଥାଏ", "misconception_tag": "attributing_toxicity", "explanation_or": "ଜଳୀୟ ବାଷ୍ପ ଶୁଦ୍ଧ ଜଳର ଗ୍ୟାସୀୟ ରୂପ, ବିଷାକ୍ତ ନୁହେଁ।"},
            {"index": 3, "text_or": "ଫୁଟୁଥିବା ପାଣି ଶରୀର ତାପ ଶୋଷଣ କରେ", "misconception_tag": "reversing_heat_transfer_direction", "explanation_or": "ଫୁଟୁଥିବା ପାଣି ଶରୀରକୁ ତାପ ଦିଏ, ଶୋଷଣ କରେ ନାହିଁ।"}
        ],
        "correct_option": 1,
        "explanation_or": "୧୦୦°C ରେ ଥିବା ବାଷ୍ପରେ ପ୍ରତି ଗ୍ରାମ ପିଛା ପ୍ରାୟ ୨୨.୬ × ୧୦⁵ J ଗୁପ୍ତତାପ ଥାଏ, ଯାହା ଶରୀର ସଂସ୍ପର୍ଶରେ ତରଳ ହେବା ବେଳେ ମୁକ୍ତ ହୋଇ ଅଧିକ ଜଳାପୋଡ଼ା କରେ।",
        "difficulty": "medium",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    # 9. Hard - Evaluate
    q.append({
        "question_id": "q_ch01_c0003_09",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ଗ୍ରୀଷ୍ମଦିନେ ଝାଳ ବାହାରିଲେ ଫ୍ୟାନ୍ ତଳେ ବସିଲେ ଆମକୁ ଶାନ୍ତି ଲାଗେ। ଏହି ପରିସ୍ଥିତିରେ ଆର୍ଦ୍ର ପାଗ (humid weather) ତୁଳନାରେ ଶୁଷ୍କ ପାଗରେ ଅଧିକ ଆରାମ ମିଳିବାର ଯଥାର୍ଥତା କଣ?",
        "options": [
            {"index": 0, "text_or": "ଶୁଷ୍କ ପାଗରେ ବାୟୁରେ ଜଳୀୟବାଷ୍ପ କମ୍ ଥିବାରୁ ଝାଳ ଦ୍ରୁତ ବାଷ୍ପୀଭୂତ ହୋଇ ଅଧିକ ଶୀତଳତା ଦିଏ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଆର୍ଦ୍ର ପାଗରେ ଫ୍ୟାନ୍ ଗରମ ପବନ ଫିଙ୍ଗିଥାଏ", "misconception_tag": "attributing_heat_to_fan", "explanation_or": "ଫ୍ୟାନ୍ କେବଳ ପବନ ଗତିଶୀଳ କରେ, ତାପମାତ୍ରା ବଦଳାଏ ନାହିଁ।"},
            {"index": 2, "text_or": "ଶୁଷ୍କ ପାଗରେ ଝାଳ ଆଦୌ ବାଷ୍ପୀଭୂତ ହୁଏ ନାହିଁ", "misconception_tag": "denying_evaporation_in_dry_air", "explanation_or": "ଶୁଷ୍କ ପାଗରେ ବାଷ୍ପୀଭବନ ସର୍ବାଧିକ ହୁଏ।"},
            {"index": 3, "text_or": "ଆର୍ଦ୍ର ପାଗରେ ଶରୀରର ତାପମାତ୍ରା କେବେ ବଢ଼ିପାରେ ନାହିଁ", "misconception_tag": "ignoring_thermal_regulation", "explanation_or": "ଆର୍ଦ୍ରତାରେ ଝାଳ ନ ଶୁଖିବାରୁ ଶରୀର ଅଧିକ ଗରମ ଅନୁଭବ କରେ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ବାୟୁର ଆର୍ଦ୍ରତା କମ୍ ଥିଲେ ବାଷ୍ପୀଭବନ ହାର ଅଧିକ ହୁଏ, ଯାହା ଶରୀରରୁ ଗୁପ୍ତତାପ ଗ୍ରହଣ କରି ଶୀଘ୍ର ଥଣ୍ଡା ଅନୁଭବ କରାଏ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    # 10. Hard - Evaluate
    q.append({
        "question_id": "q_ch01_c0003_10",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "evaluate",
        "qtype": "mcq",
        "prompt_or": "ଶୁଷ୍କ ବରଫ (Dry Ice) କୁ ସାଧାରଣ ବରଫ ତୁଳନାରେ ଶୀତଳୀକରଣ ପାଇଁ ଅଧିକ ଉପଯୋଗୀ କୁହାଯାଏ କାହିଁକି?",
        "options": [
            {"index": 0, "text_or": "ଏହା କଠିନ କାର୍ବନ ଡାଇଅକ୍ସାଇଡ ଯାହା ତରଳ ନହୋଇ ସିଧା ବାଷ୍ପ ହୋଇଯାଏ ଓ ବସ୍ତୁକୁ ଓଦା କରେ ନାହିଁ", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଏହା ସାଧାରଣ ଜଳର ବରଫ ଅପେକ୍ଷା ଶସ୍ତା ଅଟେ", "misconception_tag": "economic_reasoning_instead_of_scientific", "explanation_or": "ଏହା ଏକ ବୈଜ୍ଞାନିକ ଧର୍ମ ଉପରେ ଆଧାରିତ କାରଣ ନୁହେଁ।"},
            {"index": 2, "text_or": "ଏହା କେବେହେଲେ ଉତ୍ତାପ ଶୋଷଣ କରେ ନାହିଁ", "misconception_tag": "violating_conservation_of_energy", "explanation_or": "ଏହା ବାଷ୍ପୀଭୂତ ହେବା ପାଇଁ ପରିବେଶରୁ ପ୍ରଚୁର ଗୁପ୍ତତାପ ଶୋଷେ।"},
            {"index": 3, "text_or": "ଏହା ଏକ ତରଳ ପଦାର୍ଥ ଭାବେ ରହେ", "misconception_tag": "confusing_dry_ice_state", "explanation_or": "ଡ୍ରାଏ ଆଇସ୍ ସାଧାରଣ ଚାପରେ ତରଳ ଅବସ୍ଥା ଦେଇ ଗତି କରେ ନାହିଁ।"}
        ],
        "correct_option": 0,
        "explanation_or": "କଠିନ CO₂ ଊର୍ଦ୍ଧ୍ୱପାତନ ଯୋଗୁଁ ସିଧା ଗ୍ୟାସରେ ପରିଣତ ହୁଏ, ତେଣୁ ଏହା ପରିବହନ ସମୟରେ ଖାଦ୍ୟ କିମ୍ବା ଔଷଧକୁ ଓଦା କରେ ନାହିଁ ଏବଂ ଅତ୍ୟଧିକ ଥଣ୍ଡା ରଖେ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    # 11. Hard - Create
    q.append({
        "question_id": "q_ch01_c0003_11",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ଲୁଣ ଏବଂ କର୍ପୂରର ଏକ ମିଶ୍ରଣରୁ ଉଭୟ ଉପାଦାନକୁ ଅଲଗା କରିବା ପାଇଁ ଆପଣ କେଉଁ ପରୀକ୍ଷାମୂଳକ ଯୋଜନା କରିବେ?",
        "options": [
            {"index": 0, "text_or": "ଚାମଚରେ ଛାଣି ଅଲଗା କରିବା", "misconception_tag": "confusing_sieving", "explanation_or": "ଉଭୟ ଗୁଣ୍ଡ ଆକାରରେ ଥିଲେ ଚାଲୁଣିରେ ଅଲଗା କରାଯାଇପାରିବ ନାହିଁ।"},
            {"index": 1, "text_or": "ମିଶ୍ରଣକୁ ଏକ ଫନେଲ ଘୋଡ଼ାଇ ଧୀରେ ଧୀରେ ଗରମ କରି କର୍ପୂରର ଊର୍ଦ୍ଧ୍ୱପାତନ ଘଟାଇବା", "misconception_tag": None, "explanation_or": None},
            {"index": 2, "text_or": "ପାଣିରେ ଫୁଟାଇ ଉଭୟଙ୍କୁ ବାଷ୍ପରେ ପରିଣତ କରିବା", "misconception_tag": "destructive_separation", "explanation_or": "ଏହାଦ୍ୱାରା ଉଭୟ ଉପାଦାନ ନଷ୍ଟ ହୋଇଯିବେ।"},
            {"index": 3, "text_or": "ଚୁମ୍ବକ ପ୍ରୟୋଗ କରି କର୍ପୂରକୁ ଟାଣିବା", "misconception_tag": "assuming_magnetic_properties", "explanation_or": "ଲୁଣ ବା କର୍ପୂର କେହି ଚୁମ୍ବକୀୟ ନୁହଁନ୍ତି।"}
        ],
        "correct_option": 1,
        "explanation_or": "କର୍ପୂର ଉତ୍ତାପ ପାଇଲେ ଊର୍ଦ୍ଧ୍ୱପାତନ ଯୋଗୁଁ ବାଷ୍ପୀଭୂତ ହୋଇ ଫନେଲ କାନ୍ଥରେ ଜମା ହୁଏ ଏବଂ ଲୁଣ ପାତ୍ରରେ ରହିଯାଏ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    # 12. Hard - Create
    q.append({
        "question_id": "q_ch01_c0003_12",
        "concept_id": "c0003",
        "chapter_id": "ch001",
        "bloom_level": "create",
        "qtype": "mcq",
        "prompt_or": "ଜଳର ବାଷ୍ପୀଭବନ ହାର ଉପରେ ପବନର ବେଗର ପ୍ରଭାବ ପ୍ରମାଣ କରିବାକୁ ଏକ ଡିଜାଇନ ପ୍ରସ୍ତୁତ କରାଗଲା। ପରୀକ୍ଷାଟିକୁ ବୈଜ୍ଞାନିକ ଭାବେ ନିର୍ଭୁଲ କରିବା ପାଇଁ କେଉଁ କାରକଟିକୁ ସ୍ଥିର (controlled variable) ରଖିବା ବାଧ୍ୟତାମୂଳକ?",
        "options": [
            {"index": 0, "text_or": "ଜଳର ପ୍ରାରମ୍ଭିକ ପରିମାଣ, ପାତ୍ରର କ୍ଷେତ୍ରଫଳ ଏବଂ କୋଠରୀର ତାପମାତ୍ରାକୁ ସମାନ ରଖିବା", "misconception_tag": None, "explanation_or": None},
            {"index": 1, "text_or": "ଗୋଟିଏ ପାତ୍ରକୁ ବନ୍ଦ କରି ଅନ୍ୟଟିକୁ ଖୋଲା ରଖିବା", "misconception_tag": "introducing_confounding_variable", "explanation_or": "ବନ୍ଦ ପାତ୍ରରେ ବାଷ୍ପୀଭବନ ସ୍ତମ୍ଭିତ ହୋଇଯିବ, ଏହା ତୁଳନାଯୋଗ୍ୟ ନୁହେଁ।"},
            {"index": 2, "text_or": "ଗୋଟିଏ ପାତ୍ରରେ ପାଣି ଓ ଅନ୍ୟଟିରେ ତେଲ ବ୍ୟବହାର କରିବା", "misconception_tag": "changing_liquid_identity", "explanation_or": "ଭିନ୍ନ ତରଳ ବ୍ୟବହାର କଲେ ପବନର ପ୍ରଭାବ ନିର୍ଣ୍ଣୟ ହୋଇପାରିବ ନାହିଁ।"},
            {"index": 3, "text_or": "ଉଭୟ ପାତ୍ରକୁ ଅଲଗା ଅଲଗା ଦିନରେ ପରୀକ୍ଷା କରିବା", "misconception_tag": "temporal_inconsistency", "explanation_or": "ଅଲଗା ଦିନର ପାଗ ଓ ଆର୍ଦ୍ରତା ଫଳାଫଳକୁ ପ୍ରଭାବିତ କରିବ।"}
        ],
        "correct_option": 0,
        "explanation_or": "ବୈଜ୍ଞାନିକ ପରୀକ୍ଷଣରେ କେବଳ ପରୀକ୍ଷିତ କାରକ (ପବନ ବେଗ) ବଦଳିବ ଏବଂ ଅନ୍ୟ ସମସ୍ତ କାରକ (ଜଳ ପରିମାଣ, କ୍ଷେତ୍ରଫଳ, ତାପମାତ୍ରା) ନିୟନ୍ତ୍ରିତ ରହିବ।",
        "difficulty": "hard",
        "misconception_tag": None,
        "source_ref": "ch01 §1.4",
        "revision": 1,
        "status": "active"
    })

    return q
