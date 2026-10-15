import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import "fake-indexeddb/auto";
import { IDBFactory } from "fake-indexeddb";
import {
  downloadPackResumable,
  validatePackPayload,
  decompressArchive,
} from "../src/lib/pack_downloader";
import {
  getSharedInstalledPacks,
  getPartialDownload,
} from "../src/store/profile_session";
import { getInstalledPack } from "../src/lib/sync";
import { offlineRetrieve } from "../src/lib/offline_retrieval";

// Helper to gzip bytes using node's zlib in test environment
import * as zlib from "zlib";

function gzipSync(content: string): Uint8Array {
  return new Uint8Array(zlib.gzipSync(Buffer.from(content, "utf-8"), { mtime: 0 }));
}

async function sha256Hex(bytes: Uint8Array): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", bytes as unknown as BufferSource);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

const SAMPLE_PACK_PAYLOAD = {
  manifest: {
    pack_id: "pack_test_sci",
    version: "1.0.0",
    content_version: "2026.10.001",
    language: "or",
    min_app_version: "1.0.0",
    licence: "CC-BY 4.0",
    source_refs: ["Test syllabus"],
    chapters: ["ch001"],
    created_at: Date.now(),
  },
  chapters: [
    {
      chapter_id: "ch001",
      subject: "science",
      grade: "class9",
      title_or: "ପଦାର୍ଥ",
      title_en: "Matter",
      summary_or: "ପଦାର୍ଥର ଅବସ୍ଥା",
      source_refs: ["ch01"],
    },
  ],
  concepts: [
    {
      concept_id: "c0001",
      chapter_id: "ch001",
      title_or: "ପଦାର୍ଥର ଭୌତିକ ସ୍ୱରୂପ",
      title_en: "Physical Nature of Matter",
      summary_or: "ପଦାର୍ଥ କଣିକା ଦ୍ୱାରା ଗଠିତ।",
      prerequisites: [],
      source_refs: ["ch01 §1.1"],
    },
  ],
  chunks: [
    {
      chunk_id: "chunk_c0001_01",
      concept_id: "c0001",
      chapter_id: "ch001",
      ordinal: 1,
      text_or: "ପଦାର୍ଥ କଣିକାଗୁଡ଼ିକ ମଧ୍ୟରେ ଖାଲି ସ୍ଥାନ ଥାଏ। ଏହି କଣିକାଗୁଡ଼ିକ ନିରନ୍ତର ଗତିଶୀଳ ଏବଂ ପରସ୍ପରକୁ ଆକର୍ଷଣ କରନ୍ତି।",
      source_ref: "ch01 §1.1",
      glossary_refs: ["ପଦାର୍ଥ"],
    },
  ],
  questions: [
    {
      question_id: "q_c0001_01",
      concept_id: "c0001",
      chapter_id: "ch001",
      qtype: "mcq",
      prompt_or: "ପଦାର୍ଥ କଣ ଦ୍ୱାରା ଗଠିତ?",
      options: ["କଣିକା", "ତରଳ", "ବାଷ୍ପ", "ଆଲୋକ"],
      correct_option: 0,
      difficulty: "easy",
      bloom_level: "remember",
      explanation_or: "ପଦାର୍ଥ କ୍ଷୁଦ୍ର କଣିକା ଦ୍ୱାରା ଗଠିତ।",
      source_ref: "ch01 §1.1",
    },
  ],
  glossary: [
    {
      term_or: "ପଦାର୍ଥ",
      term_en: "Matter",
      definition_or: "ଯାହାର ବସ୍ତୁତ୍ୱ ଅଛି ଓ ସ୍ଥାନ ଅଧିକାର କରେ।",
      definition_en: "Anything that has mass and takes up space.",
    },
  ],
};

describe("Resumable Pack Downloader & Offline Flow", () => {
  beforeEach(() => {
    globalThis.indexedDB = new IDBFactory();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("decompressArchive decompresses gzip-compressed archive correctly", async () => {
    const rawJson = JSON.stringify(SAMPLE_PACK_PAYLOAD);
    const gzipped = gzipSync(rawJson);

    const decompressed = await decompressArchive(gzipped);
    expect(decompressed).toBe(rawJson);

    const parsed = JSON.parse(decompressed);
    expect(parsed.manifest.pack_id).toBe("pack_test_sci");
    expect(parsed.concepts.length).toBe(1);
    expect(parsed.chunks.length).toBe(1);
  });

  it("validatePackPayload enforces required manifest and sections", () => {
    expect(() => validatePackPayload(SAMPLE_PACK_PAYLOAD, "pack_test_sci")).not.toThrow();

    // Mismatched pack_id
    expect(() => validatePackPayload(SAMPLE_PACK_PAYLOAD, "pack_other")).toThrow(
      /pack_id mismatch/
    );

    // Missing questions
    const corrupt = { ...SAMPLE_PACK_PAYLOAD, questions: undefined };
    expect(() => validatePackPayload(corrupt, "pack_test_sci")).toThrow(/missing or not arrays/);
  });

  it("enforces minimum app version compatibility", async () => {
    const res = await downloadPackResumable({
      pack_id: "pack_test_sci",
      version: "1.0.0",
      expected_byte_size: 1000,
      expected_checksum_sha256: "dummy",
      min_app_version: "9.9.9",
    });

    expect(res.success).toBe(false);
    expect(res.error).toContain("Pack requires app version >= 9.9.9");
  });

  it("downloads, verifies checksum, decompresses, and installs pack atomically (HTTP 200 full)", async () => {
    const rawJson = JSON.stringify(SAMPLE_PACK_PAYLOAD);
    const gzipped = gzipSync(rawJson);
    const expectedSha = await sha256Hex(gzipped);

    // Mock fetch returning full HTTP 200
    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 200,
      headers: new Headers({
        "Content-Length": String(gzipped.byteLength),
      }),
      arrayBuffer: async () => gzipped.buffer.slice(gzipped.byteOffset, gzipped.byteOffset + gzipped.byteLength),
    } as any);

    const res = await downloadPackResumable({
      pack_id: "pack_test_sci",
      version: "1.0.0",
      expected_byte_size: gzipped.byteLength,
      expected_checksum_sha256: expectedSha,
      min_app_version: "1.0.0",
    });

    expect(res.success).toBe(true);
    expect(res.bytesDownloaded).toBe(gzipped.byteLength);

    // Verify pack is saved in saarthi-shared database
    const installed = await getSharedInstalledPacks();
    expect(installed.length).toBe(1);
    expect(installed[0].pack_id).toBe("pack_test_sci");
    expect(installed[0].checksum_sha256).toBe(expectedSha);

    // Verify manifest_json in DB is valid decompressed JSON, NOT binary garbage!
    const parsedStored = JSON.parse(installed[0].manifest_json);
    expect(parsedStored.manifest.pack_id).toBe("pack_test_sci");
    expect(parsedStored.chunks[0].chunk_id).toBe("chunk_c0001_01");

    // Verify offline doubt retrieval works directly against stored pack
    const pack = await getInstalledPack();
    expect(pack).toBeDefined();
    const manifest = JSON.parse(pack!.manifest_json);
    const retrieved = offlineRetrieve("ପଦାର୍ଥ କଣ", manifest.chunks, manifest.glossary, 5);
    expect(retrieved.length).toBeGreaterThan(0);
    expect(retrieved[0].chunk_id).toBe("chunk_c0001_01");
  });

  it("performs resumable Range download (HTTP 206) across multiple segments and restarts", async () => {
    const rawJson = JSON.stringify(SAMPLE_PACK_PAYLOAD);
    const gzipped = gzipSync(rawJson);
    const totalSize = gzipped.byteLength;
    const expectedSha = await sha256Hex(gzipped);

    // Split at 250 bytes with segment_size: 250
    const seg1Size = 250;
    expect(totalSize).toBeGreaterThan(seg1Size);
    const part1 = gzipped.slice(0, seg1Size);
    const part2 = gzipped.slice(seg1Size);

    let fetchCallCount = 0;

    // First download attempt: simulate interruption after segment 1
    globalThis.fetch = vi.fn().mockImplementation(async (_url, opts) => {
      fetchCallCount++;
      const range = opts?.headers?.Range || "";
      if (fetchCallCount === 1) {
        expect(range).toBe(`bytes=0-${seg1Size - 1}`);
        return {
          status: 206,
          headers: new Headers({
            "Content-Range": `bytes 0-${seg1Size - 1}/${totalSize}`,
            "Content-Length": String(seg1Size),
          }),
          arrayBuffer: async () => part1.buffer.slice(part1.byteOffset, part1.byteOffset + part1.byteLength),
        };
      }
      // Simulate network drop during segment 2
      throw new Error("Simulated network loss during second segment");
    });

    const res1 = await downloadPackResumable({
      pack_id: "pack_test_sci",
      version: "1.0.0",
      expected_byte_size: totalSize,
      expected_checksum_sha256: expectedSha,
      segment_size: seg1Size,
    });

    expect(res1.success).toBe(false);
    expect(res1.error).toContain("Simulated network loss");

    // Partial segments should be persisted in IndexedDB!
    const partial = await getPartialDownload("pack_test_sci:1.0.0");
    expect(partial).toBeDefined();
    expect(partial?.segments.length).toBe(1);
    expect(partial?.segments[0].bytes.byteLength).toBe(seg1Size);

    // Pack is NOT yet installed
    let installed = await getSharedInstalledPacks();
    expect(installed.length).toBe(0);

    // Second download attempt (resume after restart):
    // Client should resume from seg1Size to end in chunks of seg1Size
    globalThis.fetch = vi.fn().mockImplementation(async (_url, opts) => {
      const range = opts?.headers?.Range || "";
      const match = range.match(/bytes=(\d+)-(\d+)/);
      const start = match ? parseInt(match[1], 10) : 0;
      const end = match ? parseInt(match[2], 10) : totalSize - 1;
      expect(start).toBeGreaterThanOrEqual(seg1Size);
      const slice = gzipped.slice(start, end + 1);
      return {
        status: 206,
        headers: new Headers({
          "Content-Range": `bytes ${start}-${end}/${totalSize}`,
          "Content-Length": String(slice.length),
        }),
        arrayBuffer: async () => slice.buffer.slice(slice.byteOffset, slice.byteOffset + slice.byteLength),
      };
    });

    const res2 = await downloadPackResumable({
      pack_id: "pack_test_sci",
      version: "1.0.0",
      expected_byte_size: totalSize,
      expected_checksum_sha256: expectedSha,
      segment_size: seg1Size,
    });

    expect(res2.success).toBe(true);
    expect(res2.resumed).toBe(true);
    expect(res2.bytesDownloaded).toBe(totalSize);

    // Partial download is cleaned up after successful install
    const partialAfter = await getPartialDownload("pack_test_sci:1.0.0");
    expect(partialAfter).toBeUndefined();

    // Pack is installed and valid
    installed = await getSharedInstalledPacks();
    expect(installed.length).toBe(1);
    expect(installed[0].pack_id).toBe("pack_test_sci");
    expect(installed[0].checksum_sha256).toBe(expectedSha);
  });

  it("rejects corrupted archive with checksum mismatch and preserves existing valid pack", async () => {
    // 1. Install an existing valid pack v0.9.0
    const rawJson = JSON.stringify(SAMPLE_PACK_PAYLOAD);
    const validGz = gzipSync(rawJson);
    const validSha = await sha256Hex(validGz);

    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 200,
      headers: new Headers({ "Content-Length": String(validGz.byteLength) }),
      arrayBuffer: async () => validGz.buffer.slice(validGz.byteOffset, validGz.byteOffset + validGz.byteLength),
    } as any);

    await downloadPackResumable({
      pack_id: "pack_test_sci",
      version: "0.9.0",
      expected_byte_size: validGz.byteLength,
      expected_checksum_sha256: validSha,
    });

    let installed = await getSharedInstalledPacks();
    expect(installed.length).toBe(1);
    expect(installed[0].version).toBe("0.9.0");

    // 2. Try upgrading to v1.0.0 with corrupted bytes
    const corruptBytes = new Uint8Array(validGz);
    corruptBytes[5] ^= 0xff; // Flip bits to corrupt archive

    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 200,
      headers: new Headers({ "Content-Length": String(corruptBytes.byteLength) }),
      arrayBuffer: async () => corruptBytes.buffer.slice(corruptBytes.byteOffset, corruptBytes.byteOffset + corruptBytes.byteLength),
    } as any);

    const res = await downloadPackResumable({
      pack_id: "pack_test_sci",
      version: "1.0.0",
      expected_byte_size: corruptBytes.byteLength,
      expected_checksum_sha256: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", // wrong hash
    });

    expect(res.success).toBe(false);
    expect(res.error).toContain("Checksum mismatch");

    // Existing valid pack v0.9.0 must be retained!
    installed = await getSharedInstalledPacks();
    expect(installed.length).toBe(1);
    expect(installed[0].version).toBe("0.9.0");
  });
});
