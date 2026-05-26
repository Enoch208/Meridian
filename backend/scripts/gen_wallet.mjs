// Generate a fresh Solana keypair (ed25519) using Node's built-in crypto.
// Writes the secret ONLY to gitignored files (wallet.json + backend/.env);
// prints ONLY the public address to stdout so the private key never lands in logs.
//
// Usage: node scripts/gen_wallet.mjs
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const BS58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
function base58(bytes) {
  let num = BigInt(0);
  for (const b of bytes) num = num * 256n + BigInt(b);
  let out = "";
  while (num > 0n) { out = BS58[Number(num % 58n)] + out; num /= 58n; }
  for (const b of bytes) { if (b === 0) out = "1" + out; else break; }
  return out;
}

// ed25519 keypair; extract raw 32-byte seed (tail of PKCS8 DER) + 32-byte pubkey (tail of SPKI DER)
const { publicKey, privateKey } = crypto.generateKeyPairSync("ed25519");
const seed = privateKey.export({ type: "pkcs8", format: "der" }).subarray(-32);
const pub = publicKey.export({ type: "spki", format: "der" }).subarray(-32);
const secretKey64 = Buffer.concat([seed, pub]); // Solana/Phantom secret-key format

const address = base58(pub);
const secretBase58 = base58(secretKey64); // Phantom "import private key" format

const here = path.dirname(fileURLToPath(import.meta.url));
const backendDir = path.resolve(here, "..");

// 1) wallet.json (gitignored): both array + base58 forms
fs.writeFileSync(
  path.join(backendDir, "wallet.json"),
  JSON.stringify({ publicKey: address, secretKeyBase58: secretBase58, secretKeyArray: Array.from(secretKey64) }, null, 2)
);

// 2) fill the CREATOR_WALLET_* lines in backend/.env (gitignored)
const envPath = path.join(backendDir, ".env");
let env = fs.readFileSync(envPath, "utf8");
env = env.replace(/^CREATOR_WALLET_PUBKEY=.*$/m, `CREATOR_WALLET_PUBKEY=${address}`);
env = env.replace(/^CREATOR_WALLET_PRIVATE_KEY=.*$/m, `CREATOR_WALLET_PRIVATE_KEY=${secretBase58}`);
fs.writeFileSync(envPath, env);

console.log("Solana wallet generated.");
console.log("PUBLIC ADDRESS (safe to share / fund):");
console.log(address);
console.log("Private key written to gitignored backend/wallet.json and backend/.env only.");
