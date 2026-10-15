"""Demo question bank for Karana Study Rooms — Class 9 Science.

All content is seeded/demo material for the deterministic DemoKaranaAgent.
A real agent integration would replace the agent, not this data.
"""

# ---- Doubt Relay bank -------------------------------------------------
# Each entry: question, known correct answer (substring-matched), the
# explanation shown at step 6, a follow-up per decision pattern, and a
# fresh verification question.
RELAY_BANK = [
    {
        "id": "rel-matter-evaporation",
        "chapter_hint": "matter",
        "question": "Why does sweat cool our body on a hot day?",
        "correct_answer": "evaporation",
        "keywords": ["evaporation", "evaporates", "evaporate", "vaporisation", "latent"],
        "keywords_or": ["ବାଷ୍ପୀଭବନ", "ବାଷ୍ପୀଭୂତ", "ବାଷ୍ପ ହୋଇ", "ଲୁଚ୍ଚ ତାପ"],
        "expected_answer": "Sweat absorbs heat from the skin and evaporates; "
                           "this latent heat of vaporisation is taken away from the body, "
                           "so the skin cools down.",
        "explanation": "Evaporation is a surface phenomenon: particles at the liquid "
                       "surface escape by absorbing energy from their surroundings. When "
                       "sweat evaporates, it draws the latent heat of vaporisation from the "
                       "skin, lowering the skin temperature. That is why a breeze or fan "
                       "helps — it speeds evaporation.",
        "followups": {
            "agree": "You all mentioned evaporation. Can anyone explain why we feel even "
                     "cooler under a fan, using what you wrote?",
            "disagree": "Some of you said evaporation and some said sweat is cold water. "
                        "Compare your two answers: where does the 'cold' come from if sweat "
                        "leaves the body at skin temperature?",
            "insufficient": "Your answers were too short to compare. Try again: what happens "
                            "to the heat of the skin when sweat turns into vapour?",
        },
        "verification": {
            "question": "Why does sprinkling water on a roof cool the room below in summer?",
            "options": [
                "Water is always colder than air",
                "Evaporating water absorbs latent heat from the roof",
                "Water reflects sunlight away",
                "Water conducts heat into the ground",
            ],
            "correct_option": 1,
            "explanation": "The water absorbs latent heat as it evaporates, taking energy "
                           "from the roof surface, which cools the room below.",
        },
    },
    {
        "id": "rel-cell-plasma",
        "chapter_hint": "tissue",
        "question": "What is the main difference between plasma and lymph?",
        "correct_answer": "protein",
        "keywords": ["protein", "proteins", "red blood cells", "rbc"],
        "keywords_or": ["ପ୍ରୋଟିନ", "ଆଲବୁମିନ", "ଲୋହିତ ରକ୍ତ କଣିକା"],
        "expected_answer": "Plasma is the fluid part of blood containing proteins like "
                           "albumin; lymph is tissue fluid that has entered lymph vessels and "
                           "has fewer proteins and no red blood cells.",
        "explanation": "Blood = plasma + cells. Plasma carries dissolved proteins and "
                       "nutrients. As plasma leaks through capillary walls it becomes tissue "
                       "fluid; collected into lymph vessels it is called lymph. Lymph has "
                       "fewer proteins and lacks RBCs, and it carries digested fat and extra "
                       "fluid back toward the heart.",
        "followups": {
            "agree": "Good agreement. Now: which components of blood would you NOT expect "
                     "to find in lymph, and why?",
            "disagree": "One of you said lymph is 'just another blood'. Compare: which "
                        "protein-rich part of blood is missing in lymph and where does lymph "
                        "actually come from?",
            "insufficient": "Give one specific component that differs between plasma and "
                            "lymph so we can compare your ideas.",
        },
        "verification": {
            "question": "Which of these flows inside lymph vessels?",
            "options": [
                "Lymph rich in proteins, same as plasma",
                "Lymph with fewer proteins and no red blood cells",
                "Whole blood with platelets",
                "Only water with salts",
            ],
            "correct_option": 1,
            "explanation": "Lymph forms when some plasma leaks out of capillaries; most "
                           "proteins stay in the blood, and RBCs never leave them.",
        },
    },
    {
        "id": "rel-motion-distance",
        "chapter_hint": "motion",
        "question": "Can the distance travelled by an object be less than the magnitude "
                    "of its displacement? Why?",
        "correct_answer": "never",
        "keywords": ["never", "no,", "cannot", "can't", "always greater", "displacement is the shortest", "shortest"],
        "keywords_or": ["କେବେ ନାହିଁ", "କେବେଁ ନାହିଁ", "ଅପସରଣ ସର୍ବଦା", "ଅପସରଣ ହେଉଛି କ୍ଷୁଦ୍ରତମ"],
        "expected_answer": "No — distance is the total path length and displacement is the "
                           "shortest straight-line change of position, so distance is always "
                           "greater than or equal to |displacement|.",
        "explanation": "Distance adds up every step of the path; displacement only measures "
                       "the straight gap between start and end points. Walking in a circle "
                       "gives large distance but zero displacement, so distance ≥ "
                       "|displacement| always, with equality on a straight path without "
                       "turning.",
        "followups": {
            "agree": "You all said 'never'. Give one everyday example where distance and "
                     "displacement are equal, and one where they are wildly different.",
            "disagree": "Some of you think distance can be smaller. Draw a round trip: what "
                        "is the displacement after returning to the start, and how does that "
                        "compare with the distance walked?",
            "insufficient": "Say yes or no with a reason: what does displacement measure that "
                            "distance does not?",
        },
        "verification": {
            "question": "An athlete completes one lap of a circular track of radius 50 m. "
                        "What is the magnitude of displacement?",
            "options": ["100 m", "314 m", "0 m", "157 m"],
            "correct_option": 2,
            "explanation": "Start and end points coincide, so the straight-line displacement "
                           "is zero even though distance is the full circumference.",
        },
    },
]

# ---- Find the Mistake bank --------------------------------------------
MISTAKE_BANK = [
    {
        "id": "mist-boiling-temp",
        "topic_hint": "matter",
        "title": "Boiling water experiment",
        "problem_lines": [
            "A student boils water on a Himalayan trek and records these observations:",
            "1. Water starts boiling at 100 °C.",
            "2. The student adds more fuel and the boiling water gets hotter.",
            "3. Steam condensing on a lid releases heat to the lid.",
            "4. The student concludes: at boiling, temperature stays constant.",
        ],
        "mistake_index": 2,  # 0-based line number of the seeded error
        "expected_answer": "Line 2 is wrong: boiling water stays at its boiling point; "
                           "extra heat goes into converting liquid to vapour (latent heat of "
                           "vaporisation), not into raising the temperature.",
        "explanation": "Once boiling starts, all supplied heat is consumed as latent heat of "
                       "vaporisation. The temperature plateaus at the boiling point until all "
                       "the liquid is gone. (At high altitude the boiling point itself is "
                       "lower than 100 °C, so line 1 is also imprecise on a trek — but the "
                       "seeded error to catch is line 2.)",
        "followup": "If boiling water cannot get hotter, how does a pressure cooker cook "
                    "food faster?",
    },
    {
        "id": "mist-cell-wall",
        "topic_hint": "tissue",
        "title": "Comparing plant and animal cells",
        "problem_lines": [
            "A student wrote these notes comparing cells:",
            "1. Plant cells have a cell wall made of cellulose outside the membrane.",
            "2. Animal cells have a cell wall made of protein.",
            "3. Plastids are present only in plant cells.",
            "4. The cell membrane controls what enters and leaves the cell.",
        ],
        "mistake_index": 2,
        "expected_answer": "Line 2 is wrong: animal cells do NOT have a cell wall; their "
                           "boundary is only the plasma membrane.",
        "explanation": "A cell wall is a rigid outer layer found in plants (cellulose), "
                       "fungi (chitin) and bacteria — never in animal cells. Animal cells rely "
                       "on the flexible plasma membrane alone, which is why they can change "
                       "shape.",
        "followup": "Why would a cell wall be a disadvantage for cells that must change "
                    "shape, like muscle cells?",
    },
]
