"""Build the address-label table used in the revision (Ethereum mainnet only).

Source: dawsbot/eth-labels (MIT licence), a public copy of Etherscan name tags,
pinned at commit d9b21aefeded56f7fce7208d6fa173d128526c1b (2026-09-25).
Input:  data/csv/accounts.csv from that repository (columns address, chainId, label, nameTag)
Output: ../data/labels_eth_mainnet.csv  (address, category, name_tag)

Categories (one per address; priority order resolves addresses with several tags):
  psp     payment service providers / merchant acquirers (BitPay, Coinbase Commerce,
          Upay, AlphaPo, B2BinPay, Paykassa, WooCommerce gateway, ...)  -> payment ground truth
  issuer  stablecoin issuer treasury / mint / redemption addresses (Circle, Tether, Paxos)
  cex     centralised exchanges: hot wallets, deposit addresses, fiat gateways
  defi    DEXs, aggregators/routers, lending, bridges, MEV bots/builders, ERC-4337 infrastructure
  other   any other Etherscan-tagged address

Usage: python build_labels.py /path/to/eth-labels/data/csv/accounts.csv
"""
import csv, re, sys, collections

SRC = sys.argv[1] if len(sys.argv) > 1 else "accounts.csv"
OUT = "../data/labels_eth_mainnet.csv"

CEX_PREFIX = ["binance", "coinbase", "kraken", "okx", "okex", "bitget", "bybit", "kucoin",
              "gate.io", "huobi", "htx", "crypto.com", "bitfinex", "gemini", "upbit", "bithumb",
              "mexc", "bitstamp", "robinhood", "poloniex", "bittrex", "deribit", "bitvavo",
              "coinone", "korbit", "uphold", "luno", "liquid", "bitflyer", "bitso", "bitpanda",
              "kraken", "blofin", "delta exchange"]
CEX_LABELS = {"coinbase", "kraken", "okx", "bitget", "kucoin", "gate-io", "crypto-com", "bitfinex",
              "gemini", "upbit", "bithumb", "mexc", "bitstamp", "deribit", "poloniex", "bittrex",
              "fiat-gateway", "bilaxy", "blofin-exchange", "delta-exchange"}
# tags that carry an exchange name but are not exchange custody flows
CEX_EXCLUDE = re.compile(r"exploit|charity|avs operator|deployer|commerce", re.I)

PSP_LABELS = {"payments", "bitpay"}
PSP_NAME = re.compile(r"coinbase commerce|commerce fee|^coinbase: commerce|bitpay|woocommerce|"
                      r"b2binpay|alphapo\b|upay|paykassa|coinpayments|nowpayments|cryptomus", re.I)
PSP_EXCLUDE = re.compile(r"token|deployer|sotradefx|cryptoproworld", re.I)

ISSUER_LABELS = {"circle", "tether", "paxos"}
ISSUER_EXCLUDE = re.compile(r"cctp|message|token messenger|blacklister|pauser|eurc|xaut|cnht|mxnt|"
                            r"eurt|usat|gold|token$|stablecoin|usdt0|deployer|owner", re.I)

DEFI_LABELS = {"dex", "defi", "router", "bridge", "allbridge", "debridge", "stargate", "wormhole",
               "hop-protocol", "synapse", "multichain", "layer-2", "arbitrum", "optimism", "polygon",
               "1inch", "0x-protocol", "cow-protocol", "paraswap", "kyberswap", "sushiswap",
               "curve-finance", "curve-fi", "balancer", "bancor", "aave", "compound", "lido", "pendle",
               "yearn", "maker", "sky", "metamask", "dydx", "synthetix", "liquity", "frax-finance",
               "mev-bot", "mev-builder", "mev-protection", "mev-relay", "erc-4337-bundler",
               "paymaster", "pimlico", "zapper-fi", "yield-farming", "vaults", "morpho", "uniswap",
               "ethena", "eigenlayer", "symbiotic", "tokemak", "idle-finance", "mstable",
               "set-protocol", "origin-protocol", "spool-finance", "cream-finance", "wintermute"}

PRIORITY = {"psp": 0, "issuer": 1, "cex": 2, "defi": 3, "other": 4}


def classify(label, tag):
    t = tag.strip()
    tl = t.lower()
    if (label in PSP_LABELS or PSP_NAME.search(t)) and not PSP_EXCLUDE.search(t):
        return "psp"
    if label in ISSUER_LABELS and not ISSUER_EXCLUDE.search(t):
        return "issuer"
    if not CEX_EXCLUDE.search(t) and (label in CEX_LABELS or any(tl.startswith(p) for p in CEX_PREFIX)):
        return "cex"
    if label in DEFI_LABELS:
        return "defi"
    return "other"


best = {}
with open(SRC, newline="") as f:
    for r in csv.DictReader(f):
        if r["chainId"] != "1":
            continue
        a = r["address"].strip().lower()
        if not re.fullmatch(r"0x[0-9a-f]{40}", a):
            continue
        cat = classify(r["label"].strip().lower(), r["nameTag"])
        if a not in best or PRIORITY[cat] < PRIORITY[best[a][0]]:
            best[a] = (cat, r["nameTag"].strip())

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["address", "category", "name_tag"])
    for a in sorted(best):
        w.writerow([a, best[a][0], best[a][1]])

c = collections.Counter(v[0] for v in best.values())
print(f"{len(best):,} unique mainnet addresses -> {OUT}")
for k in sorted(c, key=PRIORITY.get):
    print(f"  {k:7s} {c[k]:>7,}")
