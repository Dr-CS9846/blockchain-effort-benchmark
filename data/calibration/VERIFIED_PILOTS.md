# Verified Pilot Set — cleanly-reported blockchain development effort (matched triples)

Hand-curated, **independently verified** projects for the Curated Matched-Triple calibration.
Each entry = {human-REPORTED effort, the ONE repo that produced it, a verifiable on-chain proposal}.
Every figure below was read directly from the on-chain proposal / repo (not auto-parsed).
Person-month unit = Boehm's **152 person-hours/PM** (hours-reported cases); FTE×duration where the
proposal reports developer-weeks. Conversion is shown per project for full transparency.

## ⭐ EFFORT GROUND TRUTH & GROWTH RULE (governance, re-locked 2026-06-16)
**Decision (PI, 2026-06-16): the effort ground truth is the FTE/effort the grantee committed on-record in the
W3F (and equivalent) grant — believed as written.** Self-reconstructed effort (git-history mining) is REJECTED
and will not be revisited; grantee surveys are not relied upon. Rationale: an on-record figure the builder
themselves signed up to is more trustworthy than any number we reconstruct.

- **Sources (ecosystem diversity):** W3F/Polkadot (#1–90, #97–101) + **Crust Grants Program (#91–92, decentralized
  storage)** + **Polkadot Open Source Dev Grants / POSG (#93–96, treasury-funded, distinct curators)** — non-W3F
  sources admitted 2026-06-17; same believe-stated-FTE matched-triple rule, distinct programs/teams; adds Lua,
  Java, Haskell-shop & TS-tooling stacks.
- **Calibration set = the full matched-triple corpus, n = 100 (and growing):** every row is {grantee-stated
  effort (FTE×duration → PM, or hours where given) · the ONE repo that produced it · on-chain/milestone delivery
  proof}. The headline constant A is fit on this set. The earlier GOLD/EXTENDED wall is REMOVED — all delivery-
  proven triples sit on one footing.
- **Best-grounded subset (sensitivity only, NOT segregated):** the 6 rows reporting *actual logged hours*
  (#1 Subsquare, #4 dotreasury, #10 Remarker, #11 Kheopswap, #12 ink! analyzer, #13 Dot Code School) are kept
  flagged so we can report a robustness check that A is stable between "actual-hours" and "stated-FTE" rows.
  This is a sensitivity analysis, not a separate headline.

**Growth rule going forward:** grow the W3F-stated-effort matched-triple corpus toward and past Boehm (n=161),
admitting only rows that pass all three gates — (1) delivered (on-chain executed OR W3F milestones delivered),
(2) a single matched repo that produced the funded work, (3) scope sanity (ks_per_pm within band). Effort is
taken as the grantee-stated FTE×duration. No proxy reconstruction, no survey dependence.

| # | Project | Chain / yr | Type | Codebase | Reported effort | ≈ PM | Repo | On-chain |
|---|---|---|---|---|---|---|---|---|
| 1 | **Subsquare** (gov app) | Polkadot 2024 | Retroactive | Brownfield | 3,760 dev-hrs (itemised) | **24.7** | opensquare-network/subsquare | Executed, 469,845 USDT |
| 2 | **Ask! v0.1** (ink!/AS language) | Kusama 2020–21 | Forward grant | Greenfield | 30 dev-weeks (3 dev × 10 wk) | **6.9** | patractlabs/ask | Awarded, 1,661 KSM |
| 3 | **Bagpipes** (no-code XCM dApp) | Polkadot 2023–24 | Forward | dApp | 1,515 dev-hrs (4 milestones) | **9.97** | BagpipesOrg/app | Awarded, 25,910.72 DOT |
| 4 | **dotreasury** (treasury explorer) | Kusama 2021 | Retroactive | Brownfield slice | ≈20 dev-days (10 maint + 2-wk feature) | **0.95** | opensquare-network/dotreasury | Awarded, 38.66 KSM |
| 5 | **Megaclite v0.1** (ZKP crypto lib) | Polkadot 2020 | Forward grant | Greenfield | 15 dev-weeks (3 dev × 5 wk) | **3.45** | patractlabs/megaclite (→ zkmega) | Awarded, 5,431 DOT |
| 6 | **Subsquare new-features** (gov app) | Polkadot 2022–23 | Forward + retro | Brownfield slice | 1,736 dev-hrs (subsquare share of 2,104) | **11.4** | opensquare-network/subsquare | Awarded, 36,969 DOT |
| 7 | **Fennel Protocol** (Whiteflag msg chain) | W3F grant 2022 | Forward grant | Greenfield (ported PoC) | 3 FTE × 3 mo (3 milestones, all delivered) | **9.0** | fennelLabs/Fennel-Protocol | W3F: 3/3 milestones delivered |
| 8 | **Elara v0.1** (RPC access layer) | Polkadot 2020 | Forward grant | Greenfield | 20 dev-wk + 1 designer-wk (4 dev × 5 wk) | **4.6** | patractlabs/elara | Awarded, 8,600 DOT |
| 9 | **ParaSpell** (XCM dev tool/UI) | W3F grant 2022 | Forward grant | Greenfield | 1 FTE × 2 mo (base grant, 1 milestone) | **2.0** | dudo50/ParaSpell | W3F: base grant delivered |
| 10 | **Remarker** (NFT marketplace) | Polkadot 2024 | **Retroactive (actual)** | dApp | 1,100 work-hrs (completed) | **7.24** | Remarkers/Remarkers-market | Executed, 946.91 DOT |
| 11 | **Kheopswap** (Asset Hub DEX UI) | Polkadot 2024 | **Retroactive (actual)** | dApp | 480 dev-hrs (completed) | **3.16** | kheopswap/kheopswap | Executed, 14,092 DOT |
| 12 | **ink! analyzer** (LSP/semantic analyzer) | Polkadot 2024 | **Retroactive (actual)** | Brownfield slice | 424 dev-hrs (itemised, v5-support) | **2.79** | ink-analyzer/ink-analyzer | Executed, 2,812.27 DOT |
| 13 | **Dot Code School** (interactive coding edu) | Polkadot 2023 | **Retroactive (actual)** | dApp/web | 144 dev-hrs (PoC; FTE 1 @ $125/h) | **0.95** | iammasterbrucewayne/dotcodeschool | Executed, 2,500 DOT |
| 14 | **Pontem (Move VM pallet)** | W3F 2020–21 | Forward grant | Greenfield (forked Libra Move VM) | M1+M2 = 252 person-days (28×4 + 28×5) | **13.3** | pontem-network/sp-move | W3F: M1 (PR#72) + M2 (PR#113) delivered |
| 15 | **SkyeKiwi Protocol** (secret-sharing crypto) | W3F 2021 | Forward grant | Greenfield (privacy lib) | 2 FTE × 4 mo | **8.0** | skyekiwi/skyekiwi-protocol | W3F grant delivered |
| 16 | **Stable Asset** (DeFi synth-asset) | W3F 2021 (Wave 9) | Forward grant | Greenfield (Substrate modules) | 2 FTE × 1 mo | **2.0** | nutsfinance/stable-asset | W3F grant delivered |
| 17 | **Subcoin** (Bitcoin-on-Substrate full node) | W3F | Forward grant | Greenfield node | FTE×mo PRIMARY-confirmed (v2) | **3.0** | subcoin-project/subcoin | W3F: 3 milestones delivered |
| 18 | **Myriad Social** (social parachain) | W3F | Forward grant | Greenfield parachain | FTE×mo PRIMARY-confirmed (v2) | **9.0** | myriadsocial/myriad-node-parachain | W3F: 3 milestones delivered |
| 19 | **Melodot** (data-availability layer) | W3F | Forward grant | Greenfield DA node | FTE×mo PRIMARY-confirmed (v2) | **6.75** | ZeroDAO/melodot | W3F: 4 milestones delivered |
| 20 | **Gafi** (GameFi infra parachain) | W3F | Forward grant | Greenfield parachain | FTE×mo PRIMARY-confirmed (v2) | **13.8** | cryptoviet/gafi | W3F: 3 milestones delivered |
| 21 | **Fair Squares** (real-estate/housing DAO) | W3F | Forward grant | Greenfield pallets | FTE×mo PRIMARY-confirmed (v2) | **12.0** | Fair-Squares/fair-squares | W3F: 5 milestones delivered |
| 22 | **NewOmega** (on-chain turn-based game) | W3F | Forward grant | Greenfield game (ink!) | FTE×mo PRIMARY-confirmed (v2) | **4.0** | WiktorStarczewski/newomega.polkadot | W3F: 4 milestones delivered |
| 23 | **Delmonicos** (EV-charging payments) | W3F | Forward grant | Greenfield pallet | FTE×mo PRIMARY-confirmed (v2) | **3.0** | Delmonicos/charger-node | W3F: 3 milestones delivered |
| 24 | **DelightfulDOT/Dedot** (TS Substrate client SDK) | W3F | Forward grant | Greenfield library | FTE×mo PRIMARY-confirmed (v2) | **9.0** | CoongCrafts/delightfuldot | W3F: 2 milestones delivered |
| 25 | **Bit.Country** (metaverse parachain) | W3F | Forward grant | Greenfield parachain | FTE×mo PRIMARY-confirmed (v2) | **5.0** | bit-country/Bit-Country-Blockchain | W3F: 2 milestones delivered |
| 26 | **EightFish** (substrate dApp framework) | W3F | Forward grant | Greenfield framework | FTE×mo PRIMARY-confirmed (v2) | **4.0** | eightfish-org/eightfish | W3F: 2 milestones delivered |
| 27 | **Candle Auction (ink!)** (auction contract) | W3F | Forward grant | Greenfield ink! contract | FTE×mo PRIMARY-confirmed (v2) | **1.0** | agryaznov/candle-auction-ink | W3F: 3 milestones delivered |
| 28 | **inkscope Fuzzer** (ink! security fuzzer) | W3F | Forward grant | Greenfield tool | 1.5 FTE × 3 mo (primary) | **4.5** | inkscopexyz/inkscope-fuzzer | W3F: 2 milestones delivered |
| 29 | **Decentralized Threshold Signing** (crypto) | W3F | Forward grant | Greenfield lib | 1 FTE × 3 mo (primary) | **3.0** | Fiono11/decentralized_threshold_signing_service | W3F: 3 milestones delivered |
| 30 | **Aisland DocSig** (document signing) | W3F | Forward grant | Greenfield pallet/dApp | 1.5 FTE × 2 mo (primary) | **3.0** | aisland-dao/docsig | W3F: 2 milestones delivered |
| 31 | **Roloi** (payment streaming) | W3F | Forward grant | Greenfield pallet | 2 FTE × 1 mo (primary) | **2.0** | RoloiMoney/roloi-polkadot-w3f-grant | W3F: 2 milestones delivered |
| 32 | **KZero** (zk-login identity) | W3F | Forward grant | Greenfield | 4 FTE × 2 mo | **8.0** | kzero-xyz/kzero | W3F delivered |
| 33 | **Libra** (escrow payments) | W3F | Forward grant | Greenfield | 1.5 FTE × 4 mo | **6.0** | atscaletech/libra | W3F delivered |
| 34 | **CESS** (decentralized storage) | W3F | Forward grant | Greenfield | 2 FTE × 4 mo | **8.0** | Cumulus2021/cess | W3F delivered |
| 35 | **Cyclops** (validator dashboard) | W3F | Forward grant | Greenfield | 1 FTE × 3 mo | **3.0** | ArthurHoeke/cyclops | W3F delivered |
| 36 | **DAOsign** (e-signing contracts) | W3F | Forward grant | Greenfield | 2 FTE × 2 mo | **4.0** | DAOsign/polkadot-smart-contracts | W3F delivered |
| 37 | **Fractapp** (wallet) | W3F | Forward grant | Greenfield | 3.5 FTE × 3 mo | **10.5** | fractapp/fractapp | W3F delivered |
| 38 | **GenesisDAO** (DAO node) | W3F | Forward grant | Greenfield | 3 FTE × 3 mo | **9.0** | deep-ink-ventures/genesis-dao-node | W3F delivered |
| 39 | **PoCS** (proof-of-contract-stake) | W3F | Forward grant | Greenfield | 3 FTE × 3.45 mo | **10.35** | auguth/pocs | W3F delivered |
| 40 | **SubIdentity** (identity) | W3F | Forward grant | Greenfield | 3 FTE × 3 mo | **9.0** | TDSoftware/subidentity-webapp | W3F delivered · scope-recheck (low ks/PM) |
| 41 | **Substats** (chain stats) | W3F | Forward grant | Greenfield | 2 FTE × 5 mo | **10.0** | CESSProject/substats | W3F delivered |
| 42 | **ArtZero / InkWhale** (NFT marketplace) | W3F | Forward grant | Greenfield (ink!) | 5 FTE × 4 mo | **20.0** | ArtZero-io/Contracts | W3F delivered |
| 43 | **Curve AMM** (DeFi AMM) | W3F | Forward grant | Greenfield | 3 FTE × 1.38 mo | **4.14** | equilibrium-eosdt/equilibrium-curve-amm | W3F delivered |
| 44 | **DotPay** (payments) | W3F | Forward grant | Greenfield | 5 FTE × 1.84 mo | **9.2** | bytepayment/bytepay | W3F delivered |
| 45 | **Evanesco** (privacy network) | W3F | Forward grant | Greenfield | 3 FTE × 3 mo | **9.0** | Evanesco-Labs/WhiteNoise.rs | W3F delivered |
| 46 | **IPFS Utilities** (IPFS pallet) | W3F | Forward grant | Greenfield | 2 FTE × 2 mo | **4.0** | TDSoftware/substrate-ipfs | W3F delivered · scope-recheck (high ks/PM) |
| 47 | **PolkaJ** (Java client) | W3F | Forward grant | Greenfield (Java) | 0.8 FTE × 3 mo | **2.4** | emeraldpay/polkaj | W3F delivered |
| 48 | **Liisa Portfolio Tracker** (NFT) | W3F | Forward grant | Greenfield | 2.25 FTE × 5 mo | **11.25** | LiisaNFT/PolkadotNFTPortfolioTracker | W3F delivered · scope-recheck |
| 49 | **MangoSale** (token sale) | W3F | Forward grant | Greenfield | 4 FTE × 2 mo | **8.0** | Mangoboxlabs/MangoSale | W3F delivered · scope-recheck |
| 50 | **NuLink** (privacy KMS) | W3F | Forward grant | Greenfield | 2 FTE × 6 mo | **12.0** | NuLink-network/nulink-chain | W3F delivered · scope-recheck (low ks/PM) |
| 51 | **Parallel** (DeFi lending parachain) | W3F | Forward grant | Greenfield | 4 FTE × 4 mo | **16.0** | parallel-finance/parallel | W3F delivered |
| 52 | **php-scale-codec** (PHP SDK) | W3F | Forward grant | Greenfield (PHP) | 1 FTE × 2 mo | **2.0** | gmajor-encrypt/php-scale-codec | W3F delivered |
| 53 | **RainbowDAO** (DAO protocol) | W3F | Forward grant | Greenfield (ink!) | 8 FTE × 1.84 mo | **14.72** | RainbowcityFoundation/RainbowDAO-Protocol-Ink | W3F delivered |
| 54 | **Tempora** (XCM payment automation) | W3F | Forward grant | Greenfield | 3 FTE × 2.5 mo | **7.5** | NeoPower-Digital/tempora | W3F delivered |
| 55 | **SubGame** (gaming chain) | W3F | Forward grant | Greenfield | 3 FTE × 2.76 mo | **8.28** | SubGame-Network/subgame-network | W3F delivered |
| 56 | **AlgoCash** (algorithmic stablecoin) | W3F | Forward grant | Greenfield | 1.5 FTE × 1.38 mo | **2.07** | ReserveLabs/AlgoCash | W3F delivered |
| 57 | **Anchor** (naming service) | W3F | Forward grant | Greenfield | 1 FTE × 1 mo | **1.0** | ff13dfly/Anchor | W3F delivered · scope-recheck |
| 58 | **C++ Light Client** | W3F | Forward grant | Greenfield (C++) | 1 FTE × 1.15 mo | **1.15** | eqlabs/polkadot-light-client | W3F delivered |
| 59 | **create-substrate-app** (CLI scaffolder) | W3F | Forward grant | Greenfield | 1 FTE × 1 mo | **1.0** | philoniare/create-substrate-app | W3F delivered |
| 60 | **Shivarthu** (decentralized court) | W3F | Forward grant | Greenfield | 2 FTE × 8 mo | **16.0** | amiyatulu/shivarthu | W3F delivered |
| 61 | **SubQuery** (indexer) | W3F | Forward grant | Greenfield | 2 FTE × 1.5 mo | **3.0** | OnFinality-io/subql | W3F delivered |
| 62 | **GreenLemon** (stealth-address payments) | W3F | Forward grant | Greenfield | 2 FTE × 2.76 mo | **5.52** | GreenLemonProtocol/dksap-polkadot | W3F delivered · scope-recheck |
| 63 | **Epirus Explorer** (contract explorer) | W3F | Forward grant | Greenfield | 2 FTE × 3 mo | **6.0** | web3labs/epirus-substrate | W3F delivered |
| 64 | **Halva** (testing framework) | W3F | Forward grant | Greenfield | 1.5 FTE × 1.15 mo | **1.72** | halva-suite/halva | W3F delivered |
| 65 | **Idavoll** (DAO) | W3F | Forward grant | Greenfield | 3 FTE × 0.92 mo | **2.76** | idavollnetwork/idavoll | W3F delivered |
| 66 | **Konomi** (money market) | W3F | Forward grant | Greenfield | 2 FTE × 1.5 mo | **3.0** | konomi-network/cumulus | W3F delivered · scope-recheck |
| 67 | **Lunie** (governance UI) | W3F | Forward grant | Greenfield | 5.5 FTE × 1.15 mo | **6.32** | luniehq/lunie | W3F delivered |
| 68 | **MangoBOX** (launchpad, ink!) | W3F | Forward grant | Greenfield | 4 FTE × 2 mo | **8.0** | Mangoboxlabs/Mangoboxink | W3F delivered · scope-recheck |
| 69 | **NFTMart** (NFT market node) | W3F | Forward grant | Greenfield | 2 FTE × 2 mo | **4.0** | NFTT-studio/NFTMart-Node | W3F delivered |
| 70 | **Ocelloids** (monitoring SDK) | W3F | Forward grant | Greenfield | 2 FTE × 2 mo | **4.0** | sodazone/ocelloids | W3F delivered |
| 71 | **Offline Election Tool** (staking) | W3F | Forward grant | Greenfield | 1 FTE × 0.92 mo | **0.92** | antiers-solutions/polkadot-staking-miner | W3F delivered |
| 72 | **Polkadot Analytics** (analytics) | W3F | Forward grant | Greenfield | 0.85 FTE × 1 mo | **0.85** | mobr-ai/PolkadotAnalytics | W3F delivered |
| 73 | **PRIMIS** (identity client) | W3F | Forward grant | Greenfield | 3 FTE × 1.38 mo | **4.14** | Primis-Labs/client | W3F delivered |
| 74 | **Sandox** (no-code dApp builder) | W3F | Forward grant | Greenfield | 4 FTE × 4 mo | **16.0** | sandoxio/sandox | W3F delivered |
| 75 | **Signet** (sign-in with Substrate) | W3F | Forward grant | Greenfield | 1 FTE × 1 mo | **1.0** | TalismanSociety/siws | W3F delivered |
| 76 | **Slonigiraf** (education) | W3F | Forward grant | Greenfield | 1 FTE × 1 mo | **1.0** | slonigiraf/recommendation-letter | W3F delivered |
| 77 | **sol2ink** (Solidity→ink! transpiler) | W3F | Forward grant | Greenfield | 1 FTE × 4.6 mo | **4.6** | 727-Ventures/sol2ink | W3F delivered |
| 78 | **Standard Protocol** (stablecoin) | W3F | Forward grant | Greenfield | 1 FTE × 2 mo | **2.0** | digitalnativeinc/standard-substrate | W3F delivered · scope-recheck |
| 79 | **Starry Network** (NFT) | W3F | Forward grant | Greenfield | 1 FTE × 2.5 mo | **2.5** | Starry-Network/starry_node | W3F delivered |
| 80 | **Stone Index** (index fund) | W3F | Forward grant | Greenfield | 3 FTE × 0.69 mo | **2.07** | stonedefi/stone-index-substrate-ui | W3F delivered |
| 81 | **SubDAO** (DAO node) | W3F | Forward grant | Greenfield | 4 FTE × 2 mo | **8.0** | SubDAO-Network/subdao-node | W3F delivered (multi-repo grant → node only) |
| 82 | **Distributed Key Mgmt** (KMS) | W3F | Forward grant | Greenfield | 4 FTE × 3 mo | **12.0** | KryptikApp/swordExample | W3F delivered |
| 83 | **DecentralML** (decentralized ML) | W3F | Forward grant | Greenfield | 2.5 FTE × 2 mo | **5.0** | livetreetech/DecentralML | W3F delivered |
| 84 | **DAuth Network** (auth/identity) | W3F | Forward grant | Greenfield | 3 FTE × 8 mo | **24.0** | DAuth-Network/instant-proof | W3F delivered · scope-recheck |
| 85 | **Deeper Network** (VPN chain) | W3F | Forward grant | Greenfield | 5 FTE × 1 mo | **5.0** | deeper-chain/deeper-chain | W3F delivered · scope-recheck |
| 86 | **Plus** (polkadot-js-plus wallet) | W3F | Forward grant | Greenfield | 1 FTE × 3 mo | **3.0** | Nick-1979/polkadot-Js-Plus-extension | W3F delivered · scope-recheck |
| 87 | **Faucet** (sybil-resistant faucet) | W3F | Forward grant | Greenfield | 1 FTE × 1 mo | **1.0** | karooolis/sybil-resistant-substrate-faucet | W3F delivered |
| 88 | **hs-web3** (Haskell Web3 client lib) | W3F | Forward grant | Greenfield (Haskell) | 0.4 FTE × 3.68 mo | **1.47** | airalab/hs-web3 | W3F delivered |
| 89 | **GrantMaster** (grant-management dApp) | W3F | Forward grant | Greenfield | 0.6 FTE × 5 mo | **3.0** | Zaniyar/grantmaster | W3F delivered |
| 90 | **RainbowDAO Protocol ink!** (DAO contract suite) | W3F | Forward grant | Greenfield (ink!) | 8 FTE × 1.84 mo | **14.72** | RainbowcityFoundation/RainbowDAO-Protocol-Ink-milestone_1 | W3F delivered (M1) |
| 91 | **CruTransfer** (decentralized file-transfer dApp) | **Crust** 2021 | Forward grant | Greenfield (Angular/Node, IPFS/Crust) | 1 FTE × 2 mo | **2.0** | h2qutc/CruTransfer | Crust: 2 milestones delivered |
| 92 | **crust-explorer** (blockchain explorer + open API) | **Crust** 2021 | Forward grant | Greenfield (front+back+DB) | 3 FTE × 2 mo | **6.0** | HuaZhuangNan/crust-explorer | Crust: 2 milestones delivered |
| 93 | **OpenGov Voting Tool** (DAO voting automation) | **POSG** 2025 | Forward grant | Greenfield (TS/Express) | 2.5 FTE × 2 mo | **5.0** | ZelmaCorp/VotingTool | POSG: delivered (2 ML) |
| 94 | **SubLua** (Substrate SDK for Lua) | **POSG** 2025 | Forward grant | Greenfield (Lua + Rust FFI) | 1.5 FTE × 3 mo | **4.5** | MontaQLabs/sublua | POSG: delivered (2 ML) |
| 95 | **Create Dot App** (dApp scaffolding CLI) | **POSG** 2025 | Forward grant | Greenfield (CLI/TS) | 1 FTE × 2 mo (overview said 2 FTE; solo team → 1) | **2.0** | preschian/create-dot-app | POSG: delivered (2 ML) |
| 96 | **Polkadot Java SDK (Jot)** (JVM Substrate SDK) | **POSG** 2025 | Forward grant | Greenfield (Java) | 2.5 FTE × 3 mo | **7.5** | methodfive/jot | POSG: all milestones delivered |
| 97 | **Nolik** (censorship-resistant messaging protocol) | W3F | Forward grant | Greenfield (Substrate + Rust CLI) | 1 FTE × 2 mo | **2.0** | chainify/nolik | W3F delivered (2 ML) |
| 98 | **Typechain-Polkadot** (ink! TS type generator) | W3F | Forward grant | Greenfield (TS tooling) | 2 FTE × 1.84 mo (M1) | **3.68** | Supercolony-net/typechain-polkadot | W3F delivered (M1) |
| 99 | **Calamar** (multi-chain block explorer) | W3F | Forward grant | Greenfield (TS/React/GraphQL) | 1 FTE × 2.53 mo | **2.53** | topmonks/calamar | W3F delivered |
| 100 | **TuxedoDApp** (UTXO dApp + wallet) | W3F | Forward grant | Greenfield (React/TS + Rust/Axum) | 2 FTE × 3 mo | **6.0** | mlabs-haskell/TuxedoDapp | W3F delivered (2 ML) |
| 101 | **Ventur** (business-process pallets) | W3F | Forward grant | Greenfield (Substrate pallets) | 4 FTE × 2 mo | **8.0** | Popular-Coding/ventur | W3F delivered (2 ML) |

Spread so far: **0.95 → 24.7 PM** (26×), two chains, five project types (governance app / language-compiler /
no-code dApp / treasury-explorer maintenance slice / ZKP crypto library), greenfield + brownfield, forward +
retroactive, full-build + micro-maintenance. Exactly the heterogeneity Boehm-style local calibration needs — and
the wide size dynamic range a power law needs.

**Org concentration (disclosed):** of 9 pilots, **3 OpenSquare** (1 & 6 subsquare, 4 dotreasury), **3 Patract Hub**
(2 Ask!, 5 Megaclite, 8 Elara), Bagpipes (3), Fennel Labs (7, US), ParaSpell (9, Slovakia/EU). Pilots 1 and 6 are
two non-overlapping windows of the same `opensquare-network/subsquare` repo (valid distinct slices, not
independent). Independence is now the majority — **7 of 13 are non-OpenSquare/Patract** (3 Bagpipes, 7 Fennel, 9
ParaSpell, 10 Remarker, 11 Kheopswap, 12 ink! analyzer, 13 Dot Code School). The two big orgs are now a
minority (6 of 13), with independent teams spanning US + EU + India + solo-dev contributors.

**Effort-type balance (disclosed):** "actual" (retroactive, completed-work) effort = Pilots 1, 4, 6 (partial),
**10** (Remarker), **11** (Kheopswap), **12** (ink! analyzer — first independent *itemised* actual). "Proposed"
(forward) effort = 2, 3, 5, 7, 8, 9. The actual subset now has both single-figure (10, 11) and fully-itemised
(12) reports from independent devs. Tag preserved so calibration can stratify actual vs proposed.

**"Roadmap angle" (discovery method, recorded):** Patract and OpenSquare each published *numbered project
roadmaps* (e.g. Patract roadmap [polkassembly post/100]; Elara is their "4th project") where **every roadmap item
is a separate treasury proposal with its own itemised FTE×week effort table.** This is a high-yield vein of
gold-standard *clean-effort* triples — but all from the same 1–2 orgs, so it grows the clean subset WITHOUT
improving independence. Use it to bulk the on-chain-itemised tier; keep the W3F/independent route for diversity.

**Proof classes (disclosed):** Pilots 1–6 are **on-chain treasury awards** (Polkadot/Kusama). Pilot 7 is a
**W3F grant delivery** — completion proven by merged milestone-delivery PRs + commit-pinned repo (durable,
peer-reviewed), not an on-chain award. Tag each pilot's proof class so calibration can stratify if needed.

---

## Pilot 1 — Subsquare (Polkadot OpenGov Referendum #1225)
- **Proposal (open it):** https://polkadot.subsquare.io/referenda/1225
- **What:** open-source Polkadot/Kusama governance app (~175K monthly users — the platform whose API we mine).
- **Type:** **[Retroactive]** 12-month maintenance + common-features development → reports *completed* work.
- **Window (stated):** 2023-10-01 → 2024-09-30 (12 months).
- **Reported effort (itemised dev-cost table, 8 workstreams):** **3,760 development hours** → 3760 / 152 = **24.7 PM**.
  (Referendum-detail 1,200 h; Account/profile 640 h; Treasury spends 480 h; New referenda 360 h; Preimages 360 h;
  Track-status 240 h; AssetHub 240 h; Bounty 240 h.) Plus a separate maintenance budget.
- **Repo (the code):** https://github.com/opensquare-network/subsquare — proposal links its [CHANGELOG](https://github.com/opensquare-network/subsquare/blob/main/CHANGELOG.md) + [commits](https://github.com/opensquare-network/subsquare/commits/main).
- **On-chain proof:** state **Executed** (paid) 2024-11-11, block 23,367,224; **469,845 USDT** via AssetHub Treasury Spend #64. Track: medium_spender. Proposer 12sNU8…Srx4.
- **Sizing mode:** windowed slice (brownfield) — measure source LOC delivered in the 12-month window.

## Pilot 2 — Ask! v0.1 (Kusama Treasury Proposal #66)
- **Proposal (open it):** https://kusama.subsquare.io/treasury/proposals/66 · original discussion [Polkassembly #398](https://kusama.polkassembly.io/post/398)
- **What:** a smart-contract **language/compiler** for Substrate — AssemblyScript-based alternative to ink! — by **Patract Hub** (their 8th treasury project).
- **Type:** forward grant; **greenfield** (new codebase, "does not rely on other open source libraries").
- **Window (stated):** 14 Dec 2020 → 22 Feb 2021 (10 weeks).
- **Reported effort (verbatim):** *"Cost of v0.1 (30 developers × weeks)"* — 3 developers across 10 weeks = **30 developer-weeks** → 3 FTE × (10/4.345 mo) = **6.9 PM**. Cost: employee payments $87,000 ($2,900/dev-week) + $6,000 ops = $93,000.
- **Repo (the code, named in proposal):** https://github.com/patractlabs/ask
- **On-chain proof:** state **Awarded** (paid) 2021-01-15, block 5,788,800; **1,661 KSM** (~$111K at the time). Council motion #254 passed **12–0 unanimous**. Proposer HsNn…2WEV; beneficiary Dz8UJCdSfSoixAkZFzeRb9ZthKKBniB3m7ZwxhNu4hLVeJv.
- **Sizing mode:** greenfield — whole repo at the v0.1 delivery ≈ the work (use first-commit→v0.1-tag window to isolate v0.1).

## Pilot 3 — Bagpipes (Polkadot OpenGov Referendum #362)
- **Proposal (open it):** https://polkadot.polkassembly.io/referenda/362 · forum: [Powerful no-code cross-chain XCM dApp builder](https://forum.polkadot.network/t/powerful-no-code-cross-chain-xcm-dapp-builder/4767)
- **What:** no-code cross-chain **XCM dApp / workflow builder** ("Zapier for Web3"), live at alpha.bagpipes.io. By **Ramsey Ajram** (full-stack/product) + **Filip Kalebo** (Substrate/Rust) — Rust Syndicate + Decentration, funding split 50/50. Two hands-on coders, no non-technical members.
- **Type:** forward (proposed effort); post-W3F-grant continuation. Submitted Dec 2023.
- **Window (stated):** 4 milestones, 24–32 weeks (~6–8 months).
- **Reported effort (4-milestone table):** **1,515 developer hours** → 1515 / 152 = **9.97 PM**.
  (M0 Core web tools 245 h; M1 Polkadot primitives/pallets 370 h; M2 OpenGov & staking 295 h; M3 ink!/light-client/mobile 605 h.) Rate ~$100/dev-hr ($151,500 / 1,515).
- **Repo (the code, verified):** https://github.com/BagpipesOrg/app (formerly `XcmSend/app`).
- **On-chain proof:** **Awarded** single lump-sum **25,910.7234 DOT** (= $151,500 at EMA30 $5.847/DOT), funded ~block 19,008,000 (2024). Tracked "In progress – on time" by the Saxemberg OpenGov Watchdog.
- **Honest caveat (team-stated):** 1,515 h is the **proposed** effort in the submission; *actual* delivered hours may differ (single lump-sum award, not milestone-tied). Flag this pilot's reported PM as "proposed", not "actual".
- **Sizing mode:** windowed slice over the funded period (or full repo if BagpipesOrg/app was created for this work — to confirm at measurement).

## Pilot 4 — dotreasury (Kusama Treasury Proposal #103)
- **Proposal (open it):** https://kusama.subsquare.io/treasury/proposals/103 · original discussion [Polkassembly #816](https://kusama.polkassembly.io/post/816)
- **What:** **dotreasury** (dotreasury.com) — an open-source Kusama/Polkadot **treasury explorer / retrospect tool** by **OpenSquare**. This proposal funds one maintenance-quarter slice (server + continuous dev + one new "proposal grading + IPFS signature" feature).
- **Type:** **[Retroactive]** maintenance quarter → reports *completed* work. Brownfield slice of an existing repo.
- **Window (stated):** 05.2021 → 07.2021 (the "last 3 months" maintenance quarter).
- **Reported effort (itemised, verbatim on-chain):**
  - Continuous maintenance development: *"We request 10 days cost for 1 developer, and it's \$500 × 10 = \$5000"* → **10 developer-days**.
  - Grading + IPFS feature (part of M3): table *"Support grading and IPFS storage | 2 weeks | \$1500"* → ~**2 developer-weeks** (1 dev).
  - (Server hosting \$1,350 is infrastructure, **not** dev effort — excluded from PM.)
  - **Total dev effort ≈ 20 developer-days ≈ 4 dev-weeks → 20 / 21.1 working-days-per-month ≈ 0.95 PM.**
- **Repo (the code, named in proposal):** https://github.com/opensquare-network/dotreasury
  - **Exact matched slice handed to us by the developers:** [diff `e8f09bf…release-2.3.1`](https://github.com/opensquare-network/dotreasury/compare/e8f09bf9cfcbf352425555734c022c59c9ba72ea...release-2.3.1) — this is *precisely* the code delivered for this proposal. The most exactly-sizable pilot in the set.
- **On-chain proof:** state **Awarded** (paid) 2021-08-10, award block 8,726,400; **38.66 KSM** (= \$7,992 at MA30 KSM price; requested as \$7,850/203.077). Council approval **motion #339, 12–0 unanimous**. Proposer & beneficiary ESgz…1cEb (OpenSquare). proposalIndex 103.
- **Sizing mode:** windowed slice (brownfield) — measure source LOC in the exact `e8f09bf…release-2.3.1` diff (added + modified, generated-excluded).
- **Disclosed overlap:** same team (OpenSquare) as Pilot 1 (subsquare). Different product, different repo, different scope — a valid distinct calibration point (Boehm's own COCOMO dataset repeated organizations). Flagged here for full transparency; do not treat #1 and #4 as organizationally independent.

## Pilot 5 — Megaclite v0.1 (Polkadot Treasury Proposal #24)
- **Proposal (open it):** https://polkadot.subsquare.io/treasury/proposals/24 · original discussion [Polkassembly #167](https://polkadot.polkassembly.io/post/167)
- **What:** **Megaclite v0.1** — a **zero-knowledge-proof cryptography library** for Substrate (ADD, MUL, Pairing for 4 elliptic curves — alt_bn128, bls12_381, BLS12-377, BW6_761 — in both Native and Runtime-WASM layers, plus groth16 zkSNARK verify). Patract Hub's 5th project. Later renamed **zkMega** (`patractlabs/zkmega`).
- **Type:** forward grant (**proposed** effort); **greenfield** (new library).
- **Window (stated, verbatim):** *"Detailed Design of v0.1: 5 weeks (16 Nov – 21 Dec)"* (2020).
- **Reported effort (verbatim on-chain):** *"Cost of v0.1 (15 developers × weeks)"* — five milestones M1–M5 each *"3 developers × 1 week"* = **15 developer-weeks** (3 devs × 5 wk) → 15 / 4.345 = **3.45 PM**. Cost: $28,500 dev ($1,900/dev-week) + $3,000 ops = **$31,500**.
- **Repo (the code, named in proposal):** https://github.com/patractlabs/megaclite (renamed → https://github.com/patractlabs/zkmega). *GitHub status (user-reported, confirm at measurement): ~57 commits, Apache-2.0.*
- **On-chain proof:** state **Awarded** (paid) 2020-12-05, award block 2,764,800; **5,431 DOT** (= $31,500 at $5.8/DOT; on-chain value 54310000000000 plancks). Council **motion #42** — *final tally 8–0 (zero nays)*. Proposer 13DgX…H9rz (Patract); beneficiary 123ua9…X2iC (identity "RTTI-5220").
- **Sizing mode:** greenfield — whole repo at the v0.1 delivery ≈ the work (use first-commit→v0.1 window, 16 Nov→21 Dec 2020, to isolate v0.1 from later v0.2/v0.3).
- **Honesty notes:**
  - **Effort is proposed, not actual** (planned 15 dev-weeks in the application) — tag as "proposed", like Pilots 2–3.
  - **Motion #42 was 8–0 *final* but not unanimous throughout:** one councillor (1363HWTP…) first voted **Nay** (briefly 5–1) then switched to Aye. Final = 8 ayes, 0 nays. "Unanimous final," not "unanimous throughout."
  - **3rd Patract Hub project** in the set (shares org with Pilot 2, Ask!). Disclosed; not organizationally independent of #2.

## Pilot 6 — Subsquare new-features (Polkadot Treasury #336 / OpenGov Referendum #13)
- **Proposal (open it):** https://polkadot.subsquare.io/referenda/13 · treasury view https://polkadot.subsquare.io/treasury/proposals/336
- **What:** a development cycle of new features for **Subsquare** (governance app) **and** dotreasury (treasury explorer) by **OpenSquare** — governance statistics, user-participation views, v2 redesign, Collectives support; dotreasury dark mode + spend stats.
- **Type:** mixed — **496 h retroactive** (delivered) + **1,608 h forward** (planned new features). Predominantly forward; tag as "mostly proposed."
- **Window (stated):** proposal dated 2022-04-24; on-chain 2023-07. Treat the funded cycle as 2022-04 → 2023-07.
- **Reported effort (itemised on-chain @ $80/h, verbatim tables — total 2,104 h = $168,320):**
  - **Subsquare share = 1,736 h** → Collectives 368 + Subsquare enhancements 80 + Subsquare new-features 1,288. **1,736 / 152 = 11.4 PM.** ← the matched-pair effort for this repo.
  - dotreasury share = 368 h (OpenGov pie 48 + dotreasury new-features 320) → 368 / 152 = **2.42 PM** (separately available as a dotreasury slice; NOT used here).
- **Repo (matched, the code):** https://github.com/opensquare-network/subsquare — measure source LOC delivered in the 2022-04→2023-07 window (windowed slice, brownfield).
- **On-chain proof:** state **Awarded** (paid) 2023-07-27, award block 16,588,800; **36,969 DOT** ($168,320 at submission EMA7 / ~$194k at award). gov2 Referendum **#13**, track medium_spender. Proposer & beneficiary 12sNU8…Srx4 (OpenSquare). No council motion (OpenGov direct referendum).
- **Sizing mode:** windowed slice (brownfield) over 2022-04→2023-07 — **must not reuse Pilot 1's window** (2023-10→2024-09); the two slices measure different commits of the same repo.
- **Honesty notes:**
  - **Scope-matched:** headline effort is the **subsquare-only 1,736 h (11.4 PM)**, not the full 2,104 h, to keep one-effort↔one-artifact. Logging the full table for audit; the 368 h dotreasury portion is a separate (unused) slice.
  - **Mostly forward:** 1,608 of 2,104 h (76%) are planned, not delivered-at-submission. Tag "proposed".
  - **3rd OpenSquare entry; 2nd slice of the same subsquare repo as Pilot 1** (distinct, non-overlapping window). Not independent of #1/#4 — concentration disclosed.

## Pilot 7 — Fennel Protocol (W3F Grant, delivered)
- **Application (open it):** https://github.com/w3f/Grants-Program/blob/master/applications/Fennel_Protocol.md
- **Delivered code (the repo):** https://github.com/fennelLabs/Fennel-Protocol — commit-pinned at delivery `37cc301f03ebd7eef83b589385fe566bfa777aa2` (primary Substrate chain repo; lib/cli/server are components).
- **What:** a Substrate chain implementing the **Whiteflag Protocol** — a neutral, trusted messaging standard for conflict zones / disaster response. Pallets: identity, trust, keystore, signal (AES-256 / RSA-4096). Ported from the Theriak hackathon PoC, then built out.
- **Team:** **Fennel Labs, LLC** (Sheridan, Wyoming, USA) — Sean Batzel et al. **First fully-independent team** in the set (no OpenSquare/Patract/Litentry tie).
- **Type:** forward W3F grant (**proposed** effort, fixed-scope/fixed-price); greenfield-ish (PoC port + new pallets).
- **Reported effort (durable, internally consistent — verbatim from application):** *Total Estimated Duration 3 months · FTE 3 · Total Costs $50,000*, across 3 milestones (M1 3 FTE×1 mo $15k; M2 3 FTE×1 mo $15k; M3 3 FTE×1 mo $20k). **3 FTE × 3 mo = 9.0 PM.** ($5,556/PM — W3F fixed-price, below market.)
- **Completion proof:** W3F **3/3 milestones delivered** (delivery_verified; delivery_count=3) — provable via merged milestone-delivery PRs + the pinned commit. Durable, peer-reviewed acceptance.
- **Sizing mode:** greenfield-ish — repo at the as-delivered commit; equivalent SLOC already reuse-adjusted in census (Theriak port = adapted code).
- **Honesty notes:**
  - **Proof class = W3F grant delivery**, not an on-chain treasury award (W3F pays off-chain). First non-on-chain pilot; tagged accordingly.
  - **Effort is proposed** (the $50k/9 PM fixed-price budget), not logged actuals — tag "proposed" (team delivered all 3 milestones).
  - **Why over AdMeta (rejected for this slot):** AdMeta's application self-contradicts on duration (header "1 month" vs Milestone "6 month"), and its devs are **Litentry/Web3Go-affiliated** (not independent). Fennel's fields are consistent and the team is independent. Recorded so the choice is auditable.
  - **TWO-GRANT DISAMBIGUATION (supervisor caution, 2026-06-14) — resolved.** Fennel Labs has two W3F grants:
    · **Grant 1 `Fennel_Protocol.md` (Q1 2022):** 3 months, **3 FTE**, $50k, **3 milestones** ($15k/$15k/$20k). ← Pilot #7's source; 3 FTE × 3 mo = **9.0 PM** is correct for it.
    · **Grant 2 `Whiteflag-on-Fennel.md` (Q2 2022):** 3 months, **2 FTE** (overview), $90k, **2 milestones** (M1 2 FTE×1mo $25k; M2 3 FTE×2mo $65k). The "2 FTE" a reviewer may see belongs to THIS grant — a different, later scope (web UI + full Whiteflag + IPFS). NOT Pilot #7.
    Our census pinned Grant 1 (application_url = Fennel_Protocol.md, delivery_count = 3 → matches Grant 1's 3 milestones; Grant 2 has only 2). So #7 = Grant 1, not conflated.
  - **Open caveats to tighten before final calibration:** (a) **pin** `Fennel-Protocol` to the Grant-1 delivery (~end Q1 2022 / M3) so size doesn't bleed Grant-2 code; (b) Grant 1 spanned `Fennel-Protocol` + `fennel-lib` + `fennel-cli` — sizing only the chain repo may undercount (matched-pair risk as in #6); (c) if Grant 2 is ever added, its milestone-weighted effort = 2×1 + 3×2 = **8 PM**, not the 6 PM its header implies.

## Pilot 8 — Elara v0.1 (Polkadot Treasury Proposal #16)
- **Proposal (open it):** https://polkadot.subsquare.io/treasury/proposals/16 · discussion [Polkassembly #103](https://polkadot.polkassembly.io/post/103) · Patract roadmap [post/100](https://polkadot.polkassembly.io/post/100)
- **What:** **Elara** — a unified **RPC access layer** for Substrate chains ("Infura for Polkadot"), named after Jupiter's 7th moon. Patract Hub's 4th roadmap project. Three backend services: account, stat, api.
- **Type:** forward grant (**proposed** effort); **greenfield** (new repo built for the work).
- **Window (stated, verbatim):** *"Detailed design of v0.1 (5 weeks, 21 Sept ~ 26 Oct)"* (2020).
- **Reported effort (verbatim on-chain):** *"Cost of v0.1 (1 designer × week + 20 developers × weeks)"* — M1 design (1 designer + 4 dev × 1 wk), M2 dev (4 × 2 wk), M3 integration (4 × 1 wk), M4 testing (4 × 1 wk) = **20 developer-weeks** (+1 designer-week). **20 / 4.345 = 4.6 PM** (dev-weeks, consistent with Pilots 2 & 5); **4.83 PM** if the 1 designer-week is included. Cost: $30k dev ($1,500/dev-wk) + $1k design + $3.4k ops = $34,400.
- **Repo (the code, named in proposal):** https://github.com/patractlabs/elara — GPL-3.0, ~47 commits, last active ~2020–21 (v0.1 delivered then dormant → repo ≈ v0.1 work).
- **On-chain proof:** state **Awarded** (paid) 2020-10-18, award block 2,073,600; **8,600 DOT** ($34,400 at $4/DOT). Council **motion #31, 8–0 unanimous** (all ayes, no transient nay). Proposer 13DgX…H9rz (Patract); beneficiary 1629Shw6…vmAg.
- **Sizing mode:** greenfield — whole repo at v0.1 delivery ≈ the work (first-commit→~Oct-2020 window).
- **Honesty notes:**
  - **Effort is proposed** (planned milestones), not logged actuals — tag "proposed".
  - **Headline 4.6 PM = developer-weeks only**; the 1 designer-week (UX) gives 4.83 PM if design labour is counted. Recorded both so calibration can choose.
  - **3rd Patract Hub project** (with #2 Ask!, #5 Megaclite) — re-concentrates the set; not independent. Entered for its gold-standard clean on-chain effort table, with concentration disclosed.

## Pilot 9 — ParaSpell (W3F Grant, base, delivered)
- **Application (open it):** https://github.com/w3f/Grants-Program/blob/master/applications/ParaSpell.md
- **What:** **ParaSpell** — an XCM & XCMP developer tool: a UI (and later SDK) that simplifies building cross-chain XCM transfers and opening/closing HRMP channels on Substrate. Base grant built the Vue.js UI + first transfer scenarios.
- **Team:** **ParaSpell** — Dušan Morháč (core dev, student at STU Bratislava, **Slovakia**), supervised by Viktor Valaštín (KodaDot co-founder). Independent EU team. *Disclosure: KodaDot tie via the supervisor; core dev is independent.*
- **Type:** forward W3F grant (**proposed** effort, Level-1 / fixed-price); greenfield.
- **Reported effort (durable, verbatim — base grant):** *Total Estimated Duration 2 months · FTE 1 · Total Costs $10,000*, **single milestone** (1 FTE × 2 mo, $10k). **1 FTE × 2 mo = 2.0 PM.**
- **Repo (matched, the code):** https://github.com/dudo50/ParaSpell (base-grant UI repo named in the application). *Project later migrated to the `paraspell` org (`paraspell/ui`, `paraspell/sdk`) under follow-up grants — size `dudo50/ParaSpell` at the base-grant M1 delivery, not the later org repos.*
- **Completion proof:** W3F base grant funded (Grants Wave 15) and **milestone-1 evaluated/accepted** (evaluation `paraspell_1_keeganquigley.md`). Durable GitHub history.
- **Sizing mode:** greenfield — single repo at base-M1 delivery.
- **Honesty notes:**
  - **CENSUS-CSV MISMAPPING (caught 2026-06-14).** Our manifest row "ParaSpell_follow_up" mixed the **base-grant effort** (1 FTE × 2 mo = 2 PM, $10k) with the **follow-up's** repo/commit (`paraspell/sdk` @ tag `ParaSpell-followup-m1`). The 2 PM is correct **for the base grant**, whose repo is `dudo50/ParaSpell` — so this pilot uses the base grant end-to-end. Do **not** pair 2 PM with `paraspell/sdk`.
  - **Three ParaSpell grants exist** — base (`ParaSpell.md`, 1 FTE×2mo, 2 PM), follow-up (`ParaSpell_follow-up.md`, **2 FTE×6mo = 12 PM**, $28.5k, 3 milestones, repos sdk+ui), follow-up-2 (`ParaSpell_follow-up2.md`). The follow-ups are separate, larger, multi-repo data points available later (derive from primary source, not the CSV).
  - **Proof class = W3F grant delivery** (like #7); **effort = proposed**.

## Pilot 10 — Remarker (Polkadot OpenGov Referendum #1170)
- **Proposal (open it):** https://polkadot.subsquare.io/referenda/1170 (title: *"Only Retroactive Funding Proposal: Completed Remarker Development"*) · prior proposal [#1089](https://polkadot.subsquare.io/referenda/1089)
- **What:** **Remarker** (remarkers.io) — an **NFT marketplace for Polkadot** (NFT swaps, stablecoin trading USDC/USDT, auto-teleport relay↔AssetHub, NFT create/list, new UI).
- **Type:** **[Retroactive] — ACTUAL completed effort** (the gold target: reports work already done, not a forward estimate).
- **Window (stated):** 6 months.
- **Reported effort (verbatim on-chain funding table):** *Duration 6 Months · Work Hours **1100** · Rate $4/hr · Amount $4,400.* **1,100 / 152 = 7.24 PM.** Single-figure (not multi-workstream) but an explicit actual-hours total for completed work.
- **Repo (the code, named on-chain):** https://github.com/Remarkers/Remarkers-market — single repo.
- **Team:** **Ashutosh Singh** — solo independent founder/dev (OpenGov-bots author; worked on Kusama AssetHub 2021, Polkadot AssetHub 2022). Not OpenSquare/Patract. First solo-dev pilot.
- **On-chain proof:** state **Executed** (paid) 2024-09-23, ~block 22,652,273; **946.91 DOT** (= $4,400 at submission price). Track **big_tipper**; referendum #1170; treasury-spend index **919**. Proposer/beneficiary 1HzwKk…BZEauF.
- **Sizing mode:** dApp — size `Remarkers-market` at the proposal date (Sep 2024); NFT-marketplace front-ends reuse ecosystem libs/templates, so apply reuse-adjusted equivalent SLOC at measurement.
- **Honesty notes:**
  - **First independent _actual-effort_ pilot** — strengthens the "actual" subset (previously all OpenSquare).
  - **Effort granularity is a single line** (1,100 h total), not an itemised workstream table; it is a solo founder's self-reported completed hours. Lower granularity than #1/#8 but genuinely *actual*.
  - **Reuse caution:** NFT marketplaces lean on existing pallets/UI templates — ensure equivalent-SLOC reuse adjustment so 7.24 PM isn't paired with inflated greenfield size.
  - **Proof class = on-chain treasury (Executed).**

## Pilot 11 — Kheopswap (Polkadot OpenGov Referendum #1102)
- **Proposal (open it):** https://polkadot.subsquare.io/referenda/1102 (title: *"Kheopswap retroactive funding"*)
- **What:** **Kheopswap** (kheopswap.xyz) — a **web front-end for the Polkadot Asset Hub DEX** (AssetConversion pallet): token list/balances, swaps, liquidity provisioning, transfers/teleports, fee-token selection, smoldot/substrate-connect light clients. Among the **first live dApps built on PAPI**.
- **Type:** **[Retroactive] — ACTUAL completed effort** ("entirely retroactive… compensate for work achieved up until today"; live since 24 Apr 2024).
- **Window (stated):** ~3 months of development.
- **Reported effort (verbatim on-chain cost breakdown):** *Estimated Development Hours: 3 months (approx. **480 hours**) · $130/hr · Total $62,400.* **480 / 152 = 3.16 PM.** Actual-hours figure for completed work.
- **Repo (the code, named on-chain):** https://github.com/kheopswap/kheopswap — single repo. (The `polkadot-api/polkadot-api` link is the PAPI library *dependency*, not the deliverable.)
- **Team:** **"Kheops"** — solo independent dev, 20+ yrs experience, French, based in South Korea. *Disclosure: employed at Talisman, but Kheopswap is an explicitly personal side project, separate from Talisman's products.* Not OpenSquare/Patract.
- **On-chain proof:** state **Executed** (paid) 2024-09-10, ~block 22,477,988; **14,092 DOT** (= $62,400 at $4.428 7-day EMA). Track **medium_spender**; referendum #1102; treasury-spend index **916**. Proposer/beneficiary 13ezbf…MTxfm.
- **Sizing mode:** dApp front-end — size `kheopswap/kheopswap` at the proposal date (Aug 2024); reuse-adjusted equivalent SLOC (built on PAPI/smoldot libs, which are excluded dependencies).
- **Honesty notes:**
  - **Second independent actual-effort pilot** (with #10) — diversifies the "actual" subset away from OpenSquare.
  - **Effort = "approx. 480 hours"** — a solo founder's rounded actual; single-figure granularity (like #10), genuinely actual.
  - **Proof class = on-chain treasury (Executed).**

## Pilot 12 — ink! analyzer (Polkadot OpenGov Referendum #619)
- **Proposal (open it):** https://polkadot.subsquare.io/referenda/619 (title: *"ink! Analyzer: Retroactive funding for ink! v5 support"*)
- **What:** **ink! analyzer** (analyze.ink) — a **semantic analyzer + Language Server (LSP)** for ink! smart contracts ("what rust-analyzer is to Rust"): IR/parser, diagnostics, quickfixes, completions, hover, inlay hints; ships a VS Code extension + `ink-lsp-server` binaries. This proposal funds the **ink! v5 support** increment.
- **Type:** **[Retroactive] — ACTUAL completed effort**, with a **fully itemised on-chain effort table** (highest granularity among the independent pilots).
- **Window (stated):** v5-support work, ~late 2023 → ink! v5 release 13 Mar 2024.
- **Reported effort (verbatim on-chain table, 8 workstreams):** foundations ~24h · IR/parser v5 ~80h · diagnostics+quickfixes ~136h · completions/code-actions/hover/inlay/signature ~96h · v5 codegen ~8h · maintenance/perf ~48h · integration tests ~24h · docs ~8h → **Total ~424 h** × $62.5/h = $26,500. **424 / 152 = 2.79 PM.**
- **Repo (matched, the code):** https://github.com/ink-analyzer/ink-analyzer (multi-crate monorepo: `analyzer`, `lsp-server`, IR). The VS Code wrapper `ink-analyzer/ink-vscode` is a thin client (minor).
- **Team:** **David Semakula** (@davidsemakula) — independent solo software engineer/systems architect (10+ yrs); independent contributor to rust-analyzer and ink!. Not OpenSquare/Patract.
- **On-chain proof:** state **Executed** (paid) 2024-04-17, ~block 20,376,803; **2,812.27 DOT** (= $26,500 at EMA30, 27 Mar 2024). Track **small_spender**; referendum #619; treasury-spend index **747**. Proposer/beneficiary 16AExT…eppK.
- **Sizing mode:** **brownfield windowed slice** — size the **v5-support diff only** (~late-2023 → Mar-2024), NOT the whole repo (prior v4 work was two W3F grants: `ink-analyzer.md` $30k + `ink-analyzer-phase-2.md` $59.6k). Same matched-slice discipline as #1/#4/#6.
- **Honesty notes:**
  - **First independent _itemised_ actual-effort pilot** — an 8-line workstream table matching the OpenSquare/Patract gold standard, but from a solo independent dev. Strong calibration point.
  - **Slice, not whole repo:** the 424 h is the v5 increment of a mature codebase; pair it with the v5 diff size, not cumulative LOC.
  - **Proof class = on-chain treasury (Executed).**

## Pilot 13 — Dot Code School (Polkadot OpenGov Referendum #364)
- **Proposal (open it):** https://polkadot.subsquare.io/referenda/364 (title: *"[Retroactive] Funding Development Costs for Dot Code School PoC…"*)
- **What:** **Dot Code School** (dotcodeschool.com) — an **interactive online coding school** for Polkadot/Web3 (CryptoZombies-style in-browser coding interface, step-by-step Rust/Polkadot-SDK tutorials). This proposal retroactively funds the **PoC** development.
- **Type:** **[Retroactive] — ACTUAL completed effort**, with an explicit on-chain cost breakdown.
- **Reported effort (verbatim on-chain):** *Total Cost 2,500 DOT (~$18,000) · **FTE 1** · Hourly Rate $125/h · **Total Time 144 hours**.* **144 / 152 = 0.95 PM.**
- **Repo (the code, named on-chain):** https://github.com/iammasterbrucewayne/dotcodeschool (later renamed `saumyakaran/dotcodeschool`, archived Mar 2024) — single repo; Next.js / TypeScript (99.2%).
- **Team:** **Saumya Karan** (saumyakaran / "iammasterbrucewayne") — solo independent dev (India). Not OpenSquare/Patract. *Note: separately applied to the Decentralized Futures Program for further work — that is a different, later scope; this pilot is the 144 h PoC only.*
- **On-chain proof:** state **Executed** (paid) 2023-12-28, ~block 18,798,459; **2,500 DOT** ($18,000). Track **small_spender**; referendum #364; treasury-spend index **563**. Proposer/beneficiary 16JVrg…HLw8d.
- **Sizing mode:** dApp/web — size `dotcodeschool` at the PoC state (Dec 2023); Next.js framework is an excluded dependency; apply reuse-adjusted equivalent SLOC.
- **Honesty notes:**
  - **Clean low-end actual point** (0.95 PM) — reinforces the bottom of the size/effort range alongside dotreasury (#4, also 0.95 PM); different team/domain so a valid independent point.
  - **Effort = FTE 1 × 144 h** (with explicit rate) — actual, single-task but with a clean FTE+rate+hours statement.
  - **Repo rename** (`iammasterbrucewayne` → `saumyakaran`) — same codebase; pin to the PoC commit.
  - **Proof class = on-chain treasury (Executed).**

## Pilot 14 — Pontem Move VM pallet (W3F Grant, delivered) — *first non-Polkadot-stack / Move-language pilot*
- **Application (open it):** https://github.com/w3f/Grants-Program/blob/master/applications/pontem.md
- **What:** **Pontem** — a Substrate **pallet embedding the Move VM and Move language** (Facebook/Libra's
  resource-oriented smart-contract stack) so Polkadot chains can publish/execute Move modules and scripts.
  By **Dfinance / Wings Stiftung** (Zug, Switzerland). The on-chain analogue of Ask! (#2) but for the **Move**
  language rather than ink!/AssemblyScript → a new language/VM stack in the corpus.
- **Type:** forward W3F grant (**proposed** effort, but unusually precise — per-milestone working-days × people);
  greenfield pallet that **forks the Libra Move VM** (vendored upstream → CEVRP reuse case).
- **Reported effort (verbatim, per-milestone "Working days × ppl"):**
  - M1 Pre-Alpha: 28 days × 4 ppl = **112 person-days**
  - M2 Alpha: 28 days × 5 ppl = **140 person-days**
  - (M3 Beta: 21 × 5 = 105 person-days — **NOT delivered to W3F**, continued under Pontem's own funding → excluded)
  - **W3F-delivered matched scope = M1 + M2 = 252 person-days.** Conversion (Boehm 152 h/PM, 8 h/day):
    252 × 8 / 152 = **13.3 PM** (alt. working-month 21.7 d/PM → 11.6 PM; record both, headline 13.3).
  - Application also states "Total Effort 357 days" (all 3 milestones) — that figure includes the un-delivered M3.
- **Repo (the code, named in proposal):** https://github.com/pontem-network/sp-move — archived by W3F at
  **https://github.com/w3f-grants-archive/sp-move** (durable provenance). Census-pinned commit
  `49d6f1d8598aca86bf7e59f309a078cd573fcc0e` (grant-end, Mar 2021 ≈ M1+M2 state; **confirm = M2-delivery commit
  at dissection**). Rust pallet, has CI + tests + Docker.
- **Completion proof:** W3F **Grant-Milestone-Delivery** — **Milestone #1 = PR #72** and **Milestone #2 = PR
  #113**, both **merged/accepted** (durable, peer-reviewed). Proof class = W3F grant delivery (like #7, #9).
- **Sizing mode:** greenfield-ish pallet at the M2-delivery commit. Census raw ≈ **2.53 KSLOC code**;
  **adapted fraction ≈ 0.44** (the forked Libra Move VM crates) → **CEVRP applies**: C1 (44% flagged), C2 (named
  upstream = Libra Move VM, documented in the M1 delivery), C3 (single vendored fork, not the team's own rename)
  → reuse-correct to equivalent SLOC at dissection.
- **Team / contact:** Boris Povod (R&D lead) — **boris@dfinance.co**; Oleg Gaidukov (CTO); Dfinance / Wings
  Stiftung, Zug CH. Independent of OpenSquare/Patract. Later became Pontem Network (pivoted to Aptos/Move).
- **Honesty notes:**
  - **Effort = proposed** (planned working-days × people), tag "proposed". Precise but not logged actuals.
  - **Matched-scope discipline:** only M1+M2 were W3F-delivered; M3 (Beta) excluded to keep effort↔artifact
    matched (same discipline as #6/#12). The 357-day figure would over-count.
  - **Census row was wrong** (planned_pm=4, cost=$96 — mis-parsed "1.4658 BTC"); the primary application gives
    the correct effort. Caught by hand-verification — exactly why the census `planned_pm` is treated as a
    candidate value only.
  - **Diversity contribution:** first **Move-language / Move-VM** pilot; first **Swiss** team; mid-size (~13 PM).

## Pilot 15 — SkyeKiwi Protocol (W3F Grant, delivered) — *first secret-sharing / privacy-crypto pilot*
- **Application (open it):** https://github.com/w3f/Grants-Program/blob/master/applications/skyekiwi-protocol.md
- **What:** a generic **secret-sharing / encrypted-content protocol** (threshold SSS + x25519 + Crust/IPFS
  storage + an `ink!` contract / `pallet-secrets`) — a privacy-crypto library, distinct from Megaclite's ZKP.
- **Type:** forward W3F grant (**proposed** effort); greenfield library (TS/JS + ink! + Rust).
- **Reported effort (verbatim):** *Total Duration 4 months (16 weeks) · **FTE 2** · $30,000.* M1 (2 mo × 2 FTE,
  $12k) + M2 (2 mo × 2 FTE, $18k). **2 FTE × 4 mo = 8.0 PM.** (Census planned_pm = 8.0 — agrees; primary-verified.)
- **Repo (the code):** https://github.com/skyekiwi/skyekiwi-protocol (the protocol library; `skyekiwi/contract-demo`
  is example contracts — minor, excluded). Single matched artifact.
- **Completion proof:** W3F grant delivery (extracted from the earlier SkyePass grant PR#212 via amendment
  PR#553); census resolved an exact delivery commit. **Confirm delivery PR at dissection.**
- **Reuse:** forks the audited `secret.js` SSS library + uses tweetnacl (dependencies) → assess CEVRP at
  dissection (some adapted crypto; most is integration of dependencies, which are excluded from size).
- **Team / contact:** Song Zhou (@RoyTimes) — **song.zhou@skye.kiwi**. Independent.
- **Honesty notes:** effort = proposed (2 FTE×4 mo budget); tag "proposed". First privacy/secret-sharing type.

## Pilot 16 — Stable Asset / NUTS Finance (W3F Grant, delivered) — *first DeFi-primitive pilot*
- **Application (open it):** https://github.com/w3f/Grants-Program/blob/master/applications/stable-asset.md
- **What:** a **synthetic stable-asset DeFi protocol** (Curve StableSwap-based Substrate modules: Stable Swap,
  Stable Asset, yield) by **NUTS Finance** — first DeFi primitive in the corpus.
- **Type:** forward W3F grant (**proposed** effort, Wave 9); greenfield Substrate modules.
- **Reported effort (verbatim):** *Total Duration 1 month · **FTE 2** · 20,000 DAI.* 3 milestones (1.5 wk +
  1.5 wk + 2 wk). **2 FTE × 1 mo = 2.0 PM** (headline; milestones sum ≈ 5 wk → ≤ 2.3 PM — record 2.0). Census
  planned_pm = 2.0 — agrees.
- **Repo (the code):** https://github.com/nutsfinance/stable-asset — single repo (the 3 Substrate modules).
- **Completion proof:** W3F Wave-9 grant, accepted/funded; census measured a delivery state. **Confirm delivery
  PR + pin exact commit at dissection** (census used a date cutoff, not an exact commit — tighten before final).
- **Reuse:** algorithm **ported from their own Ethereum acBTC Solidity** (`ACoconutSwap.sol`) into Substrate
  Rust — a cross-language *re-implementation* (authoring, not copy) → treat as authored, not CEVRP-adapted.
- **Team / contact:** Terry Lam (co-founder) — **terry@nuts.finance**; Daniel Tang. NUTS Finance (Cayman).
- **Honesty notes:** effort = proposed; tag "proposed". Small clean point (2 PM). First DeFi type. *Caveat:*
  census commit_source = cutoff → pin the exact delivery commit before dissection (matched-scope hygiene).

---

### Provenance / honesty notes
- The auto-harvester had **mislabelled Bagpipes** as classic "treasury #362" (which is actually a Gov1.0 housekeeping item) and guessed the wrong repo (`Koniverse/SubConnect`). The correct record is **OpenGov Referendum #362**, repo **BagpipesOrg/app** — found and verified by hand. This is exactly why every pilot is hand-verified before entry.
- The auto-parser also mis-read effort for Pilots 1 & 2 (Subsquare "72 PM", Ask! "15 PM"); verified figures are 24.7 and 6.9 PM respectively.
- "Reported effort" mixes **actual** (retroactive: Pilots 1, 4) and **proposed** (forward: Pilots 2–3); each is tagged so the calibration can weight or stratify accordingly.
- **Rejected candidate — Ink! Dev Hub Round 1 (OpenGov Ref #624 / Treasury #719, Awarded, 72,000 USDC).**
  Sibling of #137: same Astar + Aleph Zero + Phala joint Swanky/Drink! umbrella. **Excluded** for the same
  reasons — **delivery-based *variable* funding with no person-effort/hours table**, **multi-org**, **multi-repo
  umbrella** (swanky-node + swanky-suite + drink-cli + sandbox/IDE/playground/docs), **~90% partial delivery**.
  Assessed from the supplied writeup + the on-chain-verified #137 precedent (same failure mode).
- **Rejected candidate — ink!Hub / Swanky Suite (OpenGov Ref #137 / Treasury #417, Executed, 58,018 DOT).**
  Famous, real, and delivered (Astar + AlephZero + Phala joint ink! tooling). **Excluded** because: (a) **no
  person-effort on-chain** — the proposal body states only the DOT amount; all cost/effort detail is in an
  external Google Doc (deriving PM from 58,018 DOT would be cost-based, which we rejected as unusable); (b)
  **multi-repo umbrella across 3 orgs** — swanky-cli + swanky-node + drink/drink-cli/drink-pink-runtime + ~26
  `inkdevhub` example repos, so no single artifact to match effort against; (c) **partial, task-based delivery**
  (~90% of tasks, payout adjusted) → fuzzy scope↔payment mapping. Same unmatched-scope failure mode as Talisman.
- **Rejected candidate — Talisman Wallet & Portal (OpenGov Ref #1232, Executed, 690,600 USDT).** Famous and clean on-chain, but **excluded** from the verified set: (a) the proposal states *"see the [external Google Doc] for the cost breakdown"* — **no effort figure is on-chain**, so PM is not verifiable to our standard; (b) it is a **3-repo umbrella** (`talisman` + `talisman-web` + `chaindata`), so there is no single clean matched scope. Recorded here so the exclusion is auditable.
- **Rejected candidate — RegionX Hub (OpenGov Ref #1762, "Retroactive + Key Features + Maintenance").** **Rejected on-chain** (nays > ayes; treasury spend never executed → fails proof gate G3) AND effort/breakdown lives in an **external Google Doc** (no on-chain person-effort → fails G4). Verified live via Subsquare API. Auditable reject.
- **Rejected candidate — Mimir multisig tool (OpenGov Ref #1799, "Retroactive Fund").** **Rejected on-chain** (nays ≫ ayes; 138,385 USDT never executed → G3 fail) AND budget breakdown in an **external Google Sheet** (no on-chain hours table → G4 fail). Verified live via Subsquare API. *Pattern note: recent (2025) retroactive proposals frequently fail both gates — target executed 2024-era proposals with on-chain effort tables instead.*
- **Rejected candidate — Kitdot (OpenGov Ref #1805, "Development Funding (Retroactive)").** **Rejected on-chain** (nays > ayes; 9,999 USDT never executed → G3 fail) AND a **5-repo umbrella** (kitdot CLI + web3auth-examples + create-polkadot-dapp + hackers-survival-guide + personal) → no single matched scope (G1 fail). Effort = "~20 h/week × 3 mo part-time" (no on-chain itemised table). Verified live via Subsquare API.
- **Rejected candidate — Spacewalk / Pendulum (W3F Wave 13, "Stellar bridge").** Application header states **`Status: Terminated`** → grant not delivered (G2/G3 fail). Also **internally inconsistent effort** (overview "FTE 0.5 / 3 mo" vs milestones summing ~5 person-months). The census had listed it as a basic-clean candidate (planned_pm 1.5) — **hand-verification overturned it.** Lesson: census "clean" ≠ delivered; always read the application `Status` header + milestone-delivery record. (Bridge type + this team remain of interest if a *delivered* sibling grant exists.)
- **Empirical pattern (n=3/3 recent retroactive rejected: #1762, #1799, #1805):** late-2025 Polkadot OpenGov retroactive proposals are being rejected at high rate and routinely place effort in off-chain Google Docs/Sheets. **Conclusion:** the clean executed-retroactive vein is **2024-era** (our existing actuals: Remarker #1170, Kheopswap #1102, ink!analyzer #619, dotcodeschool #364). Harvest that range via the `treasury_mine` CI harvester rather than scanning recent referenda.
