import { describe, expect, it } from 'vitest';
import { getDraftValue, syncRoomDraftField } from '../src/lib/roomDrafts';
describe('room draft state', () => {
  it('preserves create-room input values across rerenders', () => {
    const drafts = {};
    syncRoomDraftField(drafts, 'rTitle', 'Evaporation doubts');
    syncRoomDraftField(drafts, 'rTopic', 'Boiling and particles');
    syncRoomDraftField(drafts, 'rChapter', 'ch02');
    syncRoomDraftField(drafts, 'rLanguage', 'en');
    syncRoomDraftField(drafts, 'rCap', '5');

    expect(getDraftValue(drafts, 'rTitle')).toBe('Evaporation doubts');
    expect(getDraftValue(drafts, 'rTopic')).toBe('Boiling and particles');
    expect(getDraftValue(drafts, 'rChapter')).toBe('ch02');
    expect(getDraftValue(drafts, 'rLanguage')).toBe('en');
    expect(drafts.cap).toBe(5);

    syncRoomDraftField(drafts, 'rTitle', 'Evaporation doubts revised');
    expect(getDraftValue(drafts, 'rTitle')).toBe('Evaporation doubts revised');
  });
});
