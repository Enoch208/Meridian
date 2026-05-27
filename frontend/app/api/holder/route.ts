import { NextResponse, type NextRequest } from "next/server";

import { TOKEN } from "@/lib/links";

// Server-side so the RPC endpoint stays private and there are no browser CORS
// limits. Queries the wallet's SPL token accounts for the $MRDN mint and sums
// the balance. A wallet "holds" if its balance exceeds MRDN_MIN_HOLD.
const RPC = process.env.SOLANA_RPC_URL || "https://api.mainnet-beta.solana.com";
const MIN_HOLD = Number(process.env.MRDN_MIN_HOLD ?? "0");

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const wallet = req.nextUrl.searchParams.get("wallet");
  if (!wallet) {
    return NextResponse.json({ error: "wallet required" }, { status: 400 });
  }

  try {
    const res = await fetch(RPC, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "getTokenAccountsByOwner",
        params: [wallet, { mint: TOKEN.mint }, { encoding: "jsonParsed" }],
      }),
      cache: "no-store",
    });

    const data = await res.json();
    const accounts: unknown[] = data?.result?.value ?? [];

    let balance = 0;
    for (const acc of accounts as Array<{
      account?: { data?: { parsed?: { info?: { tokenAmount?: { uiAmount?: number } } } } };
    }>) {
      balance += acc?.account?.data?.parsed?.info?.tokenAmount?.uiAmount ?? 0;
    }

    return NextResponse.json({ wallet, balance, holds: balance > MIN_HOLD });
  } catch {
    return NextResponse.json({ error: "rpc failed" }, { status: 502 });
  }
}
