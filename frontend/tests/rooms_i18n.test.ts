import { describe, expect, it } from 'vitest';
import { OR } from '../src/i18n/or';

describe('room localization', () => {
  it('keeps the study room UI in Odia', () => {
    expect(OR.rooms_title).toContain('କ');
    expect(OR.rooms_create).toContain('ସୃଷ୍ଟି');
    expect(OR.rooms_chat).toBe('ଚାଟ');
    expect(OR.rooms_history).toContain('ଇତିହାସ');
    expect(OR.rooms_start_relay).toContain('ଡାଉବ୍ଟ');
    expect(OR.rooms_game).toContain('ତ୍ରୁଟି');
  });
});
