"""Odia learner-facing reason messages — shipped, not LLM-generated.

Reason codes are stable (Design v2 Appendix A): never renamed, only added.
"""
REASON_MESSAGES = {
    "STATE_INVALID_FALLBACK": "ଅସ୍ଥାୟୀ ସମସ୍ୟା। ପୁଣି ଚେଷ୍ଟା କର।",
    "COLD_START": "ପ୍ରଥମ ଧାରଣା ଆରମ୍ଭ କର।",
    "WEAK_PREREQ_GAP": "ପ୍ରଥମେ ଆଧାର ଧାରଣା ବଦ୍ଧ କର।",
    "WEAK_CONCEPT": "ଏହି ଧାରଣା ପୁଣି ଶିଖ।",
    "WRONG_RETRY": "ଉତ୍ତର ଭୁଲ ଥିଲା। ପୁଣି ଚେଷ୍ଟା କର।",
    "PARTIAL_PRACTICE": "ଭଲ ହେଲା! ଆଉ ଏକ ଅଭ୍ୟାସ କର।",
    "MASTERED_ADVANCE": "ବାହ୍! ପରବର୍ତ୍ତୀ ଧାରଣା କୁ ଯାଅ।",
    "NO_GAIN_ALT_CONTENT": "ଅନ୍ୟ ଉପାୟରେ ପାଠ ପଢ।",
    "NO_GAIN_REMEDIATE_PREREQ": "ପ୍ରଥମେ ଆଧାର ଧାରଣା ବଦ୍ଧ କର।",
    "INTERVENTIONS_EXHAUSTED": "ଶିକ୍ଷକଙ୍କ ସହିତ ଯୋଗାଯୋଗ କର।",
    "SLICE_COMPLETE": "ସମସ୍ତ ପାଠ ସମ୍ପୂର୍ଣ୍ଣ! ପୁଣି ରିଭିଜନ୍ କର।",
    "BLOCKED_BY_PREREQ": "ପ୍ରଥମେ ଆଧାର ଧାରଣା ଶିଖ।",
    "CONTENT_NOT_AVAILABLE_OFFLINE": "ଏହି ପାଠ ଅଫଲାଇନ୍ ଉପଲବ୍ଧ ନାହିଁ। ଅନ୍ୟ ପାଠ ପଢ।",
    # Non-decision strings retained from v1
    "content.out_of_lessons": "ଏହି ପ୍ରଶ୍ନ ଆମ ପାଠ୍ୟକ୍ରମ ବାହାରେ। ସାମ୍ନାରେ ଥିବା ଧାରଣା ପଢ।",
    "translation.unavailable": "ଅନୁବାଦ ସେବା ଅନୁପଲବ୍ଧ। ମୂଳ ଓଡ଼ିଆ ପ୍ରଶ୍ନ ସହ ପାଠ ଖୋଜାଯାଉ।",
    "generation.basic_answer": "ଆମ ଉତ୍ତର ପାଠ୍ୟରୁ।",
}

__all__ = ["REASON_MESSAGES"]
