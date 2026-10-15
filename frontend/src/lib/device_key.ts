// Device key — non-extractable WebCrypto ECDSA P-256 key pair (v2 Section 8).
//
// The private key is generated with extractable=false and never leaves the
// device; only the SPKI public key is exported and registered at
// POST /devices. The key handle lives in the shared IndexedDB database.
// If site data is cleared the key (and the local outbox) is lost together —
// the phone re-registers as a new device (documented v2 limitation).

const ALGO = { name: "ECDSA", namedCurve: "P-256" } as const;
const SIGN_ALGO = { name: "ECDSA", hash: "SHA-256" } as const;

export interface DeviceKeyPairHandle {
  publicKey: CryptoKey;
  privateKey: CryptoKey;
}

export async function generateDeviceKey(): Promise<DeviceKeyPairHandle> {
  const pair = await crypto.subtle.generateKey(ALGO, false /* extractable */,
                                               ["sign", "verify"]);
  return pair as unknown as DeviceKeyPairHandle;
}

export async function exportPublicKeySpki(key: CryptoKey): Promise<string> {
  const spki = await crypto.subtle.exportKey("spki", key);
  return base64UrlEncode(new Uint8Array(spki));
}

export async function signChallenge(privateKey: CryptoKey,
                                    nonce: string): Promise<string> {
  const sig = await crypto.subtle.sign(
    SIGN_ALGO, privateKey, new TextEncoder().encode(nonce));
  // WebCrypto produces raw r||s (64 bytes for P-256) — the server accepts
  // both raw and DER.
  return base64UrlEncode(new Uint8Array(sig));
}

export async function verifyDeviceKeyPair(pair: DeviceKeyPairHandle):
  Promise<boolean> {
  // Round-trip check that the key pair is usable for sign/verify.
  const probe = crypto.getRandomValues(new Uint8Array(32));
  const sig = await crypto.subtle.sign(SIGN_ALGO, pair.privateKey, probe);
  return crypto.subtle.verify(SIGN_ALGO, pair.publicKey, sig, probe);
}

export function base64UrlEncode(bytes: Uint8Array): string {
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
