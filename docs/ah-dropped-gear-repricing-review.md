# Dropped-Gear Repricing Review

- Reviewed: `2026-08-08`
- Items reviewed: `347`
- Low-confidence direct-sale bands: `2`
- Reviewed low-pop starter estimates: `345`
- Starter estimates numerically changed: `309`
- Target changes greater than 50%: `9`
- Items present in the one local supply snapshot: `33`
- Realized-sales cohort model deployed: `no` — zero items passed the medium sales gate.
- External gold values copied into bands: `no`
- Gold-normalized cross-server relative rank used: `yes`
- Cross-server normalized coverage: `347` items on at least two realms
- Normalized external diagnostic: `243` below / `80` aligned / `24` above / `0` insufficient
- Comparison requests: `2082` initial / `0` failed after the 2-, 5-, and 10-second retry rule
- Publication status: `local only — not published`

## Decision

No item passed the medium realized-sales gate, so no realized-sales cohort model was deployed. The user explicitly requested practical starter prices for a low-pop market. The reviewed fallback model maps gold-normalized cross-server relative rank onto fixed Hellscream anchors; it never copies external gold and cannot promote confidence above fallback.

The purpose is a useful opening market, not a claim that every item already has a proven sale value. Fixed Hellscream anchors establish the gold scale. Gold-normalized external listings establish relative order only within comparable item groups. Coverage-sensitive ranks are pulled toward the group midpoint, clean price rounding avoids false precision, and wide Quick / Target / High bands leave room for the local market to decide. All 345 modeled rows remain `fallback` confidence until Hellscream completed sales replace them.

## Hellscream starter anchors

| Comparable group | Midpoint target | Ranked range before rounding |
|---|---:|---:|
| level-80/200-205 | 250g 0s 0c | 150g 0s 0c–350g 0s 0c |
| level-80/206-212 | 350g 0s 0c | 210g 0s 0c–490g 0s 0c |
| level-80/213-218 | 450g 0s 0c | 270g 0s 0c–630g 0s 0c |
| level-80/219-225 | 650g 0s 0c | 390g 0s 0c–910g 0s 0c |
| level-80/226-239 | 900g 0s 0c | 540g 0s 0c–1,260g 0s 0c |
| level-80/245-258 | 1,300g 0s 0c | 780g 0s 0c–1,820g 0s 0c |
| level-80/264+ | 2,000g 0s 0c | 1,200g 0s 0c–2,800g 0s 0c |
| classic/rare | 30g 0s 0c | 18g 0s 0c–42g 0s 0c |
| classic/epic | 75g 0s 0c | 45g 0s 0c–105g 0s 0c |
| outland/rare | 15g 0s 0c | 9g 0s 0c–21g 0s 0c |
| outland/epic | 100g 0s 0c | 60g 0s 0c–140g 0s 0c |
| northrend/rare/71-73 | 25g 0s 0c | 15g 0s 0c–35g 0s 0c |
| northrend/rare/74-76 | 35g 0s 0c | 21g 0s 0c–49g 0s 0c |
| northrend/rare/77-79 | 50g 0s 0c | 30g 0s 0c–70g 0s 0c |

## Direct-sale overrides

| Item | Sales / buyers / days | Old Q / T / H | New Q / T / H | Target change | Review |
|---|---:|---:|---:|---:|---|
| Sandals of Broken Dreams | 2 / 1 / 1 | 8g 60s 88c / 9g 56s 53c / 11g 95s 66c | 8g 60s 88c / 9g 56s 53c / 11g 95s 66c | +0.0% | Accepted |
| Zom's Crackling Bulwark | 1 / 1 / 1 | 297g 50s 0c / 350g 0s 0c / 455g 0s 0c | 297g 50s 0c / 350g 0s 0c / 455g 0s 0c | +0.0% | Accepted |

## Buyer and source cohorts

The numerical anchors remain item-level/era cohorts. The separate buyer/source audit prevents containers, world bosses, raid trash, level-70 legacy gear, brackets, and ordinary leveling drops from being described as one market.

| Buyer/source cohort | Items |
|---|---:|
| classic-bracket | 37 |
| classic-iconic | 45 |
| container-drop | 25 |
| level-80-drop | 21 |
| northrend-leveling | 87 |
| outland-level-70 | 35 |
| outland-leveling | 12 |
| raid-trash-drop | 62 |
| special-summon-drop | 3 |
| world-boss-drop | 20 |

## Manual review of Target changes over 50%

Every large change below was rechecked against the pinned slot, stat/socket/effect record, intended buyer, acquisition cohort, and the refreshed three-realm relative rank.

| Item | Buyer/source cohort | Old Target | New Target | Change | Coverage | Review |
|---|---|---:|---:|---:|---|---|
| Bracers of Sizzling Heat | northrend-leveling | 21g 0s 0c | 35g 0s 0c | +66.7% | 3 realms / 6 factions | accept |
| Furen's Boots | classic-bracket | 25g 0s 0c | 40g 0s 0c | +60.0% | 3 realms / 6 factions | accept |
| Helm of Narv | classic-iconic | 45g 0s 0c | 70g 0s 0c | +55.6% | 3 realms / 6 factions | accept |
| Leggings of Aqueous Dissolution | northrend-leveling | 15g 0s 0c | 35g 0s 0c | +133.3% | 3 realms / 6 factions | accept |
| Redbeard Crest | classic-bracket | 21g 0s 0c | 35g 0s 0c | +66.7% | 3 realms / 6 factions | accept |
| Snowmelt Silken Cinch | northrend-leveling | 25g 0s 0c | 45g 0s 0c | +80.0% | 3 realms / 6 factions | accept |
| Storming Vortex Bracers | northrend-leveling | 35g 0s 0c | 55g 0s 0c | +57.1% | 3 realms / 6 factions | accept |
| Surge Needle Ring | level-80-drop | 370g 0s 0c | 575g 0s 0c | +55.4% | 3 realms / 6 factions | accept |
| Will of Edward the Odd | outland-level-70 | 60g 0s 0c | 95g 0s 0c | +58.3% | 3 realms / 6 factions | accept |

## Evidence limits

- BeanCounter had three valid completed buyouts for catalog items: two for Sandals of Broken Dreams and one for Zom's Crackling Bulwark.
- Both histories are sparse and buyer/day-concentrated, so neither reaches `medium`.
- One current local snapshot is insufficient to classify stable supply or turnover.
- Known account characters were excluded where identifiable; friend/guild identities were unavailable and are recorded as such.
- No qualifying measured acquisition routes were supplied.
- Six current Warmane faction item-page comparisons were normalized by the saved commodity economy indexes. The source reports listings, not verified completed sales.
- External listing values set relative rank only. Fixed Hellscream anchors set the gold scale; no external nominal or normalized gold value was copied.
- No external completed-sale dataset or seven-day multi-snapshot series was available. That limitation is why every modeled estimate remains fallback-confidence.

## All item decisions

Prices are exact copper rendered as Quick / Target / High. `Present` is independent auction rows after known-account exclusion, not a valuation input.

| ID | Item | Cohort | Sales | Buyers / days | Present | Relative-rank input | Old Q / T / H | Proposed Q / T / H | Decision | Confidence |
|---:|---|---|---:|---:|---:|---|---:|---:|---|---|
| 647 | Destiny | classic/epic/weapons/req-52 | 0 | 0 / 0 | 1 | classic/epic; rank 52.1%; 3 realms | 70g 0s 0c / 95g 0s 0c / 150g 0s 0c | 55g 0s 0c / 75g 0s 0c / 120g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 809 | Bloodrazor | classic/epic/weapons/req-45 | 0 | 0 / 0 | 0 | classic/epic; rank 78.0%; 3 realms | 50g 0s 0c / 75g 0s 0c / 130g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 810 | Hammer of the Northern Wind | classic/epic/weapons/req-49 | 0 | 0 / 0 | 0 | classic/epic; rank 9.9%; 3 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 811 | Axe of the Deep Woods | classic/epic/weapons/req-52 | 0 | 0 / 0 | 0 | classic/epic; rank 40.0%; 3 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 50g 0s 0c / 70g 0s 0c / 120g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 812 | Glowing Brightwood Staff | classic/epic/weapons/req-49 | 0 | 0 / 0 | 0 | classic/epic; rank 67.4%; 3 realms | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 833 | Lifestone | classic/epic/accessories/req-51 | 0 | 0 / 0 | 0 | classic/epic; rank 54.9%; 3 realms | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | 60g 0s 0c / 80g 0s 0c / 130g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 867 | Gloves of Holy Might | classic/epic/armor/req-37 | 0 | 0 / 0 | 1 | classic/epic; rank 16.9%; 3 realms | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 868 | Ardent Custodian | classic/epic/weapons/req-38 | 0 | 0 / 0 | 1 | classic/epic; rank 39.4%; 3 realms | 60g 0s 0c / 85g 0s 0c / 140g 0s 0c | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 869 | Dazzling Longsword | classic/epic/weapons/req-36 | 0 | 0 / 0 | 0 | classic/epic; rank 29.6%; 3 realms | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 870 | Fiery War Axe | classic/epic/weapons/req-35 | 0 | 0 / 0 | 0 | classic/epic; rank 0.0%; 3 realms | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 871 | Flurry Axe | classic/epic/weapons/req-42 | 0 | 0 / 0 | 0 | classic/epic; rank 71.7%; 3 realms | 60g 0s 0c / 80g 0s 0c / 130g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 873 | Staff of Jordan | classic/epic/weapons/req-35 | 0 | 0 / 0 | 0 | classic/epic; rank 64.8%; 3 realms | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | 60g 0s 0c / 85g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 890 | Twisted Chanter's Staff | classic/rare/weapons/req-19 | 0 | 0 / 0 | 0 | classic/rare; rank 64.2%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 24g 0s 0c / 35g 0s 0c / 60g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 940 | Robes of Insight | classic/epic/armor/req-42 | 0 | 0 / 0 | 0 | classic/epic; rank 49.3%; 3 realms | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | 55g 0s 0c / 75g 0s 0c / 120g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 942 | Freezing Band | classic/epic/accessories/req-47 | 0 | 0 / 0 | 0 | classic/epic; rank 27.5%; 3 realms | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 943 | Warden Staff | classic/epic/weapons/req-43 | 0 | 0 / 0 | 1 | classic/epic; rank 22.5%; 3 realms | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 944 | Elemental Mage Staff | classic/epic/weapons/req-56 | 0 | 0 / 0 | 1 | classic/epic; rank 8.5%; 3 realms | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1121 | Feet of the Lynx | classic/rare/armor/req-19 | 0 | 0 / 0 | 0 | classic/rare; rank 93.1%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1168 | Skullflame Shield | classic/epic/accessories/req-54 | 0 | 0 / 0 | 0 | classic/epic; rank 84.3%; 3 realms | 70g 0s 0c / 100g 0s 0c / 160g 0s 0c | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1169 | Blackskull Shield | classic/epic/accessories/req-41 | 0 | 0 / 0 | 0 | classic/epic; rank 74.6%; 3 realms | 65g 0s 0c / 90g 0s 0c / 140g 0s 0c | 65g 0s 0c / 90g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1203 | Aegis of Stormwind | classic/rare/accessories/req-49 | 0 | 0 / 0 | 1 | classic/rare; rank 51.3%; 3 realms | 17g 0s 0c / 23g 0s 0c / 35g 0s 0c | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1204 | The Green Tower | classic/epic/accessories/req-36 | 0 | 0 / 0 | 1 | classic/epic; rank 60.6%; 3 realms | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | 60g 0s 0c / 80g 0s 0c / 130g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1263 | Brain Hacker | classic/epic/weapons/req-55 | 0 | 0 / 0 | 0 | classic/epic; rank 35.2%; 3 realms | 55g 0s 0c / 75g 0s 0c / 120g 0s 0c | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1315 | Lei of Lilies | classic/epic/accessories/req-46 | 0 | 0 / 0 | 0 | classic/epic; rank 36.8%; 2 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 45g 0s 0c / 65g 0s 0c / 110g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1443 | Jeweled Amulet of Cainwyn | classic/epic/accessories/req-55 | 0 | 0 / 0 | 0 | classic/epic; rank 4.2%; 3 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1447 | Ring of Saviors | classic/epic/accessories/req-41 | 0 | 0 / 0 | 1 | classic/epic; rank 2.8%; 3 realms | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1482 | Shadowfang | classic/rare/weapons/req-19 | 0 | 0 / 0 | 0 | classic/rare; rank 84.9%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 25g 0s 0c / 40g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1486 | Tree Bark Jacket | classic/rare/armor/req-19 | 0 | 0 / 0 | 0 | classic/rare; rank 37.9%; 3 realms | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1607 | Soulkeeper | classic/rare/weapons/req-49 | 0 | 0 / 0 | 0 | classic/rare; rank 55.2%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1715 | Polished Jazeraint Armor | classic/rare/armor/req-39 | 0 | 0 / 0 | 0 | classic/rare; rank 72.4%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1721 | Viking Warhammer | classic/rare/weapons/req-49 | 0 | 0 / 0 | 1 | classic/rare; rank 6.9%; 3 realms | 17g 0s 0c / 24g 0s 0c / 40g 0s 0c | 14g 0s 0c / 20g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1728 | Teebu's Blazing Longsword | classic/epic/weapons/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 100.0%; 3 realms | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | 80g 0s 0c / 110g 0s 0c / 180g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1935 | Assassin's Blade | classic/rare/weapons/req-19 | 0 | 0 / 0 | 0 | classic/rare; rank 89.7%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1979 | Wall of the Dead | classic/epic/accessories/req-45 | 0 | 0 / 0 | 0 | classic/epic; rank 75.9%; 3 realms | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1980 | Underworld Band | classic/epic/accessories/req-38 | 0 | 0 / 0 | 0 | classic/epic; rank 66.2%; 3 realms | 70g 0s 0c / 95g 0s 0c / 150g 0s 0c | 60g 0s 0c / 85g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1981 | Icemail Jerkin | classic/epic/armor/req-39 | 0 | 0 / 0 | 0 | classic/epic; rank 11.3%; 3 realms | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 1982 | Nightblade | classic/epic/weapons/req-39 | 0 | 0 / 0 | 0 | classic/epic; rank 27.5%; 3 realms | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2059 | Sentry Cloak | classic/rare/armor/req-19 | 0 | 0 / 0 | 0 | classic/rare; rank 56.5%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2099 | Dwarven Hand Cannon | classic/epic/weapons/req-53 | 0 | 0 / 0 | 0 | classic/epic; rank 12.7%; 3 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2100 | Precisely Calibrated Boomstick | classic/epic/weapons/req-43 | 0 | 0 / 0 | 0 | classic/epic; rank 5.6%; 3 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2163 | Shadowblade | classic/epic/weapons/req-48 | 0 | 0 / 0 | 0 | classic/epic; rank 15.5%; 3 realms | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2164 | Gut Ripper | classic/epic/weapons/req-40 | 0 | 0 / 0 | 0 | classic/epic; rank 83.3%; 3 realms | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2243 | Hand of Edward the Odd | classic/epic/weapons/req-57 | 0 | 0 / 0 | 0 | classic/epic; rank 43.7%; 3 realms | 50g 0s 0c / 75g 0s 0c / 130g 0s 0c | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2244 | Krol Blade | classic/epic/weapons/req-51 | 0 | 0 / 0 | 0 | classic/epic; rank 52.6%; 3 realms | 45g 0s 0c / 65g 0s 0c / 110g 0s 0c | 50g 0s 0c / 75g 0s 0c / 130g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2245 | Helm of Narv | classic/epic/armor/req-54 | 0 | 0 / 0 | 0 | classic/epic; rank 44.2%; 3 realms | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | 50g 0s 0c / 70g 0s 0c / 120g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2246 | Myrmidon's Signet | classic/epic/accessories/req-53 | 0 | 0 / 0 | 0 | classic/epic; rank 43.1%; 3 realms | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | 50g 0s 0c / 70g 0s 0c / 120g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2256 | Skeletal Club | classic/rare/weapons/req-19 | 0 | 0 / 0 | 0 | classic/rare; rank 3.4%; 3 realms | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | 14g 0s 0c / 19g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2291 | Kang the Decapitator | classic/epic/weapons/req-44 | 0 | 0 / 0 | 1 | classic/epic; rank 38.0%; 3 realms | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2801 | Blade of Hanna | classic/epic/weapons/req-59 | 0 | 0 / 0 | 0 | classic/epic; rank 85.4%; 3 realms | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2824 | Hurricane | classic/epic/weapons/req-48 | 0 | 0 / 0 | 0 | classic/epic; rank 57.7%; 3 realms | 55g 0s 0c / 80g 0s 0c / 140g 0s 0c | 60g 0s 0c / 80g 0s 0c / 130g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2825 | Bow of Searing Arrows | classic/epic/weapons/req-37 | 0 | 0 / 0 | 1 | classic/epic; rank 31.0%; 3 realms | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 2915 | Taran Icebreaker | classic/epic/weapons/req-47 | 0 | 0 / 0 | 0 | classic/epic; rank 45.8%; 3 realms | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 3075 | Eye of Flame | classic/epic/armor/req-49 | 0 | 0 / 0 | 0 | classic/epic; rank 67.6%; 3 realms | 60g 0s 0c / 80g 0s 0c / 130g 0s 0c | 60g 0s 0c / 85g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 3415 | Staff of the Friar | classic/rare/weapons/req-19 | 0 | 0 / 0 | 0 | classic/rare; rank 24.1%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 17g 0s 0c / 24g 0s 0c / 40g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 3475 | Cloak of Flames | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 76.9%; 3 realms | 50g 0s 0c / 80g 0s 0c / 160g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 7728 | Beguiler Robes | classic/rare/armor/req-29 | 0 | 0 / 0 | 0 | classic/rare; rank 41.4%; 3 realms | 17g 0s 0c / 23g 0s 0c / 35g 0s 0c | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 7730 | Cobalt Crusher | classic/rare/weapons/req-29 | 0 | 0 / 0 | 0 | classic/rare; rank 13.8%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 15g 0s 0c / 21g 0s 0c / 35g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 9395 | Gloves of Old | classic/rare/armor/req-29 | 0 | 0 / 0 | 1 | classic/rare; rank 48.3%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 9425 | Pendulum of Doom | classic/rare/weapons/req-39 | 0 | 0 / 0 | 0 | classic/rare; rank 72.0%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 24g 0s 0c / 35g 0s 0c / 60g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 9429 | Miner's Hat of the Deep | classic/rare/armor/req-39 | 0 | 0 / 0 | 0 | classic/rare; rank 100.0%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 12535 | Doomforged Straightedge | classic/rare/weapons/req-49 | 0 | 0 / 0 | 0 | classic/rare; rank 33.2%; 3 realms | 14g 0s 0c / 20g 0s 0c / 30g 0s 0c | 17g 0s 0c / 25g 0s 0c / 45g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 12546 | Aristocratic Cuffs | classic/rare/armor/req-49 | 0 | 0 / 0 | 0 | classic/rare; rank 35.8%; 3 realms | 14g 0s 0c / 20g 0s 0c / 30g 0s 0c | 17g 0s 0c / 25g 0s 0c / 45g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 12997 | Redbeard Crest | classic/rare/accessories/req-19 | 0 | 0 / 0 | 0 | classic/rare; rank 62.1%; 3 realms | 15g 0s 0c / 21g 0s 0c / 35g 0s 0c | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 13033 | Zealot Blade | classic/rare/weapons/req-29 | 0 | 0 / 0 | 0 | classic/rare; rank 34.5%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 13051 | Witchfury | classic/rare/weapons/req-39 | 0 | 0 / 0 | 1 | classic/rare; rank 10.3%; 3 realms | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | 14g 0s 0c / 20g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 13058 | Khoo's Point | classic/rare/weapons/req-39 | 0 | 0 / 0 | 0 | classic/rare; rank 17.2%; 3 realms | 13g 0s 0c / 18g 0s 0c / 30g 0s 0c | 16g 0s 0c / 22g 0s 0c / 35g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 13063 | Starfaller | classic/rare/weapons/req-29 | 0 | 0 / 0 | 0 | classic/rare; rank 46.1%; 3 realms | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 13067 | Hydralick Armor | classic/rare/armor/req-49 | 0 | 0 / 0 | 1 | classic/rare; rank 61.6%; 3 realms | 24g 0s 0c / 35g 0s 0c / 60g 0s 0c | 24g 0s 0c / 35g 0s 0c / 60g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 13095 | Assault Band | classic/rare/accessories/req-39 | 0 | 0 / 0 | 0 | classic/rare; rank 86.2%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 13100 | Furen's Boots | classic/rare/armor/req-39 | 0 | 0 / 0 | 0 | classic/rare; rank 82.8%; 3 realms | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 13108 | Tigerstrike Mantle | classic/rare/armor/req-29 | 0 | 0 / 0 | 1 | classic/rare; rank 69.4%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 24g 0s 0c / 35g 0s 0c / 60g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 13111 | Sandals of the Insurgent | classic/rare/armor/req-49 | 0 | 0 / 0 | 0 | classic/rare; rank 0.0%; 3 realms | 14g 0s 0c / 19g 0s 0c / 30g 0s 0c | 13g 0s 0c / 18g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 13137 | Ironweaver | classic/rare/weapons/req-29 | 0 | 0 / 0 | 0 | classic/rare; rank 20.7%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 17g 0s 0c / 23g 0s 0c / 35g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 14549 | Boots of Avoidance | classic/epic/armor/req-40 | 0 | 0 / 0 | 0 | classic/epic; rank 90.1%; 3 realms | 65g 0s 0c / 90g 0s 0c / 140g 0s 0c | 70g 0s 0c / 100g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 14551 | Edgemaster's Handguards | classic/epic/armor/req-44 | 0 | 0 / 0 | 1 | classic/epic; rank 50.7%; 3 realms | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | 55g 0s 0c / 75g 0s 0c / 120g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 14552 | Stockade Pauldrons | classic/epic/armor/req-50 | 0 | 0 / 0 | 1 | classic/epic; rank 25.4%; 3 realms | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 14553 | Sash of Mercy | classic/epic/armor/req-56 | 0 | 0 / 0 | 0 | classic/epic; rank 21.1%; 3 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 14554 | Cloudkeeper Legplates | classic/epic/armor/req-57 | 0 | 0 / 0 | 0 | classic/epic; rank 91.5%; 3 realms | 55g 0s 0c / 75g 0s 0c / 120g 0s 0c | 70g 0s 0c / 100g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 14555 | Alcor's Sunrazor | classic/epic/weapons/req-58 | 0 | 0 / 0 | 0 | classic/epic; rank 23.9%; 3 realms | 45g 0s 0c / 75g 0s 0c / 150g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 14557 | The Lion Horn of Stormwind | classic/epic/accessories/req-58 | 0 | 0 / 0 | 0 | classic/epic; rank 45.8%; 3 realms | 45g 0s 0c / 65g 0s 0c / 110g 0s 0c | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 14558 | Lady Maye's Pendant | classic/epic/accessories/req-59 | 0 | 0 / 0 | 0 | classic/epic; rank 77.5%; 3 realms | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | 65g 0s 0c / 90g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16799 | Arcanist Bindings | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 79.0%; 3 realms | 50g 0s 0c / 75g 0s 0c / 130g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16802 | Arcanist Belt | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 56.3%; 3 realms | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | 60g 0s 0c / 80g 0s 0c / 130g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16804 | Felheart Bracers | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 19.7%; 3 realms | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16806 | Felheart Belt | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 18.3%; 3 realms | 50g 0s 0c / 70g 0s 0c / 120g 0s 0c | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16817 | Girdle of Prophecy | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 62.0%; 3 realms | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | 60g 0s 0c / 80g 0s 0c / 130g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16819 | Vambraces of Prophecy | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 72.7%; 3 realms | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16825 | Nightslayer Bracelets | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 47.9%; 3 realms | 70g 0s 0c / 95g 0s 0c / 150g 0s 0c | 55g 0s 0c / 75g 0s 0c / 120g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16827 | Nightslayer Belt | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 69.5%; 3 realms | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16828 | Cenarion Belt | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 7.0%; 3 realms | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16830 | Cenarion Bracers | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 93.0%; 3 realms | 55g 0s 0c / 80g 0s 0c / 140g 0s 0c | 70g 0s 0c / 100g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16838 | Earthfury Belt | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 71.8%; 3 realms | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | 65g 0s 0c / 90g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16840 | Earthfury Bracers | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 69.0%; 3 realms | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | 60g 0s 0c / 85g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16850 | Giantstalker's Bracers | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 59.2%; 3 realms | 55g 0s 0c / 80g 0s 0c / 140g 0s 0c | 60g 0s 0c / 80g 0s 0c / 130g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16851 | Giantstalker's Belt | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 33.8%; 3 realms | 45g 0s 0c / 65g 0s 0c / 110g 0s 0c | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16857 | Lawbringer Bracers | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 63.4%; 3 realms | 40g 0s 0c / 60g 0s 0c / 110g 0s 0c | 60g 0s 0c / 85g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16858 | Lawbringer Belt | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 65.3%; 3 realms | 60g 0s 0c / 80g 0s 0c / 130g 0s 0c | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16861 | Bracers of Might | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 14.1%; 3 realms | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 16864 | Belt of Might | classic/epic/armor/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 73.8%; 3 realms | 60g 0s 0c / 85g 0s 0c / 140g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 17007 | Stonerender Gauntlets | classic/epic/armor/req-46 | 0 | 0 / 0 | 0 | classic/epic; rank 1.4%; 3 realms | 50g 0s 0c / 75g 0s 0c / 130g 0s 0c | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 18665 | The Eye of Shadow | classic/epic/accessories/req-60 | 0 | 0 / 0 | 0 | classic/epic; rank 74.8%; 3 realms | 55g 0s 0c / 80g 0s 0c / 140g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 20698 | Elemental Attuned Blade | classic/epic/weapons/req-58 | 0 | 0 / 0 | 0 | classic/epic; rank 98.6%; 3 realms | 55g 0s 0c / 90g 0s 0c / 180g 0s 0c | 70g 0s 0c / 100g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30722 | Ethereum Nexus-Reaver | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 100.0%; 3 realms | 100g 0s 0c / 140g 0s 0c / 220g 0s 0c | 100g 0s 0c / 140g 0s 0c / 220g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30723 | Talon of the Tempest | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 88.6%; 3 realms | 80g 0s 0c / 120g 0s 0c / 210g 0s 0c | 95g 0s 0c / 130g 0s 0c / 210g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30724 | Barrel-Blade Longrifle | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 97.7%; 3 realms | 75g 0s 0c / 120g 0s 0c / 240g 0s 0c | 100g 0s 0c / 140g 0s 0c / 220g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30725 | Anger-Spark Gloves | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 58.5%; 3 realms | 60g 0s 0c / 100g 0s 0c / 200g 0s 0c | 75g 0s 0c / 110g 0s 0c / 190g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30726 | Archaic Charm of Presence | outland/epic/accessories/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 43.2%; 3 realms | 60g 0s 0c / 100g 0s 0c / 200g 0s 0c | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30727 | Gilded Trousers of Benediction | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 79.5%; 3 realms | 70g 0s 0c / 110g 0s 0c / 220g 0s 0c | 85g 0s 0c / 120g 0s 0c / 190g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30728 | Fathom-Helm of the Deeps | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 55.1%; 3 realms | 70g 0s 0c / 110g 0s 0c / 220g 0s 0c | 70g 0s 0c / 100g 0s 0c / 180g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30729 | Black-Iron Battlecloak | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 53.4%; 3 realms | 60g 0s 0c / 95g 0s 0c / 190g 0s 0c | 70g 0s 0c / 100g 0s 0c / 180g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30730 | Terrorweave Tunic | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 86.4%; 3 realms | 80g 0s 0c / 120g 0s 0c / 210g 0s 0c | 95g 0s 0c / 130g 0s 0c / 210g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30731 | Faceguard of the Endless Watch | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 81.8%; 3 realms | 75g 0s 0c / 120g 0s 0c / 240g 0s 0c | 95g 0s 0c / 130g 0s 0c / 210g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30732 | Exodar Life-Staff | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 93.2%; 3 realms | 80g 0s 0c / 120g 0s 0c / 210g 0s 0c | 95g 0s 0c / 130g 0s 0c / 210g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30733 | Hope Ender | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 90.9%; 3 realms | 75g 0s 0c / 120g 0s 0c / 240g 0s 0c | 95g 0s 0c / 130g 0s 0c / 210g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30734 | Leggings of the Seventh Circle | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 68.2%; 3 realms | 70g 0s 0c / 110g 0s 0c / 220g 0s 0c | 80g 0s 0c / 110g 0s 0c / 180g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30735 | Ancient Spellcloak of the Highborne | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 60.2%; 3 realms | 60g 0s 0c / 100g 0s 0c / 200g 0s 0c | 75g 0s 0c / 110g 0s 0c / 190g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30736 | Ring of Flowing Light | outland/epic/accessories/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 22.7%; 3 realms | 70g 0s 0c / 100g 0s 0c / 180g 0s 0c | 55g 0s 0c / 80g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30737 | Gold-Leaf Wildboots | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 31.2%; 3 realms | 60g 0s 0c / 100g 0s 0c / 200g 0s 0c | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30738 | Ring of Reciprocity | outland/epic/accessories/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 33.0%; 3 realms | 60g 0s 0c / 100g 0s 0c / 200g 0s 0c | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30739 | Scaled Greaves of the Marksman | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 77.3%; 3 realms | 70g 0s 0c / 110g 0s 0c / 220g 0s 0c | 85g 0s 0c / 120g 0s 0c / 190g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30740 | Ripfiend Shoulderplates | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 95.5%; 3 realms | 70g 0s 0c / 110g 0s 0c / 220g 0s 0c | 100g 0s 0c / 140g 0s 0c / 220g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 30741 | Topaz-Studded Battlegrips | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 67.0%; 3 realms | 75g 0s 0c / 120g 0s 0c / 240g 0s 0c | 75g 0s 0c / 110g 0s 0c / 190g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31290 | Band of Dominion | outland/rare/accessories/req-70 | 0 | 0 / 0 | 0 | outland/rare; rank 76.4%; 3 realms | 12g 0s 0c / 18g 0s 0c / 30g 0s 0c | 12g 0s 0c / 18g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31291 | Crystalforged War Axe | outland/rare/weapons/req-69 | 0 | 0 / 0 | 0 | outland/rare; rank 87.5%; 3 realms | 14g 0s 0c / 20g 0s 0c / 30g 0s 0c | 14g 0s 0c / 20g 0s 0c / 35g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31292 | Crystal Pulse Shield | outland/rare/accessories/req-69 | 0 | 0 / 0 | 1 | outland/rare; rank 96.3%; 3 realms | 15g 0s 0c / 21g 0s 0c / 35g 0s 0c | 15g 0s 0c / 21g 0s 0c / 35g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31293 | Girdle of Gale Force | outland/rare/armor/req-69 | 0 | 0 / 0 | 0 | outland/rare; rank 43.1%; 3 realms | 12g 0s 0c / 17g 0s 0c / 30g 0s 0c | 9g 50s 0c / 14g 0s 0c / 25g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31294 | Pauldrons of Surging Mana | outland/rare/armor/req-69 | 0 | 0 / 0 | 0 | outland/rare; rank 55.6%; 3 realms | 12g 0s 0c / 16g 0s 0c / 25g 0s 0c | 12g 0s 0c / 16g 0s 0c / 25g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31295 | Chestguard of the Dark Stalker | outland/rare/armor/req-69 | 0 | 0 / 0 | 0 | outland/rare; rank 29.6%; 3 realms | 8g 0s 0c / 11g 0s 0c / 18g 0s 0c | 9g 50s 0c / 13g 0s 0c / 21g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31297 | Robe of the Crimson Order | outland/rare/armor/req-69 | 0 | 0 / 0 | 1 | outland/rare; rank 65.3%; 3 realms | 9g 50s 0c / 14g 0s 0c / 25g 0s 0c | 12g 0s 0c / 17g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31298 | Legguards of the Shattered Hand | outland/rare/armor/req-70 | 0 | 0 / 0 | 0 | outland/rare; rank 70.8%; 3 realms | 12g 0s 0c / 17g 0s 0c / 25g 0s 0c | 12g 0s 0c / 18g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31303 | Valanos' Longbow | outland/rare/weapons/req-70 | 0 | 0 / 0 | 0 | outland/rare; rank 37.5%; 3 realms | 7g 0s 0c / 10g 0s 0c / 16g 0s 0c | 9g 50s 0c / 14g 0s 0c / 25g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31304 | The Essence Focuser | outland/rare/weapons/req-70 | 0 | 0 / 0 | 1 | outland/rare; rank 51.4%; 3 realms | 8g 0s 0c / 11g 0s 0c / 18g 0s 0c | 10g 0s 0c / 15g 0s 0c / 25g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31305 | Ced's Carver | outland/rare/weapons/req-70 | 0 | 0 / 0 | 0 | outland/rare; rank 44.4%; 3 realms | 13g 0s 0c / 18g 0s 0c / 30g 0s 0c | 10g 0s 0c / 14g 0s 0c / 22g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31306 | Leggings of the Sacred Crest | outland/rare/armor/req-70 | 0 | 0 / 0 | 0 | outland/rare; rank 22.2%; 3 realms | 9g 50s 0c / 13g 0s 0c / 21g 0s 0c | 8g 50s 0c / 12g 0s 0c / 19g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31308 | The Bringer of Death | outland/rare/weapons/req-70 | 0 | 0 / 0 | 1 | outland/rare; rank 59.7%; 3 realms | 10g 0s 0c / 14g 0s 0c / 22g 0s 0c | 11g 0s 0c / 16g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31318 | Singing Crystal Axe | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 45.5%; 3 realms | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | 70g 0s 0c / 95g 0s 0c / 150g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31319 | Band of Impenetrable Defenses | outland/epic/accessories/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 9.1%; 3 realms | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31320 | Chestguard of Exile | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 24.4%; 3 realms | 75g 0s 0c / 110g 0s 0c / 190g 0s 0c | 55g 0s 0c / 80g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31321 | Choker of Repentance | outland/epic/accessories/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 27.8%; 3 realms | 50g 0s 0c / 75g 0s 0c / 130g 0s 0c | 55g 0s 0c / 80g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31322 | The Hammer of Destiny | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 26.1%; 3 realms | 60g 0s 0c / 80g 0s 0c / 130g 0s 0c | 55g 0s 0c / 80g 0s 0c / 140g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31323 | Don Santos' Famous Hunting Rifle | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 34.7%; 3 realms | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31326 | Truestrike Ring | outland/epic/accessories/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 29.5%; 3 realms | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31328 | Leggings of Beast Mastery | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 11.4%; 3 realms | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31329 | Lifegiving Cloak | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 12.5%; 3 realms | 60g 0s 0c / 95g 0s 0c / 190g 0s 0c | 50g 0s 0c / 70g 0s 0c / 120g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31330 | Lightning Crown | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 38.1%; 3 realms | 60g 0s 0c / 85g 0s 0c / 140g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31331 | The Night Blade | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 50.0%; 3 realms | 70g 0s 0c / 95g 0s 0c / 150g 0s 0c | 70g 0s 0c / 100g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31332 | Blinkstrike | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 47.7%; 3 realms | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | 70g 0s 0c / 100g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31333 | The Night Watchman | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 56.8%; 3 realms | 60g 0s 0c / 85g 0s 0c / 150g 0s 0c | 75g 0s 0c / 110g 0s 0c / 190g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31334 | Staff of Natural Fury | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 39.8%; 3 realms | 55g 0s 0c / 80g 0s 0c / 140g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31335 | Pants of Living Growth | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 4.5%; 3 realms | 50g 0s 0c / 80g 0s 0c / 160g 0s 0c | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31336 | Blade of Wizardry | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 75.0%; 3 realms | 80g 0s 0c / 110g 0s 0c / 180g 0s 0c | 85g 0s 0c / 120g 0s 0c / 190g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31338 | Charlotte's Ivy | outland/epic/accessories/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 41.5%; 3 realms | 55g 0s 0c / 85g 0s 0c / 170g 0s 0c | 65g 0s 0c / 95g 0s 0c / 170g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31339 | Lola's Eve | outland/epic/accessories/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 36.4%; 3 realms | 55g 0s 0c / 85g 0s 0c / 170g 0s 0c | 60g 0s 0c / 90g 0s 0c / 160g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31340 | Will of Edward the Odd | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 43.2%; 3 realms | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | 70g 0s 0c / 95g 0s 0c / 150g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31342 | The Ancient Scepter of Sue-Min | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 70.5%; 3 realms | 65g 0s 0c / 90g 0s 0c / 140g 0s 0c | 85g 0s 0c / 120g 0s 0c / 190g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 31343 | Kamaei's Cerulean Skirt | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 2.3%; 3 realms | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 32535 | Gift of the Talonpriests | outland/rare/accessories/req-70 | 0 | 0 / 0 | 0 | outland/rare; rank 23.6%; 3 realms | 11g 0s 0c / 17g 0s 0c / 35g 0s 0c | 8g 0s 0c / 12g 0s 0c / 21g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 32540 | Terokk's Might | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 65.9%; 3 realms | 60g 0s 0c / 100g 0s 0c / 200g 0s 0c | 80g 0s 0c / 110g 0s 0c / 180g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 32541 | Terokk's Wisdom | outland/epic/armor/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 6.8%; 3 realms | 60g 0s 0c / 100g 0s 0c / 200g 0s 0c | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 34622 | Spinesever | outland/epic/weapons/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 84.1%; 3 realms | 80g 0s 0c / 120g 0s 0c / 210g 0s 0c | 95g 0s 0c / 130g 0s 0c / 210g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 34837 | The 2 Ring | outland/epic/accessories/req-70 | 0 | 0 / 0 | 0 | outland/epic; rank 51.7%; 3 realms | 60g 0s 0c / 100g 0s 0c / 200g 0s 0c | 70g 0s 0c / 100g 0s 0c / 180g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35579 | Vrykul Shackles | outland/rare/armor/req-70 | 0 | 0 / 0 | 0 | outland/rare; rank 3.7%; 3 realms | 6g 50s 0c / 9g 0s 0c / 14g 0s 0c | 7g 0s 0c / 9g 50s 0c / 15g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35580 | Skein Woven Mantle | outland/rare/armor/req-70 | 0 | 0 / 0 | 0 | outland/rare; rank 0.0%; 3 realms | 7g 0s 0c / 9g 50s 0c / 15g 0s 0c | 6g 50s 0c / 9g 0s 0c / 14g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35593 | Steel Bear Trap Bracers | northrend/rare/armor/req-76 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 4.0%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 16g 0s 0c / 22g 0s 0c / 35g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35594 | Snowmelt Silken Cinch | northrend/rare/armor/req-76 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 81.5%; 3 realms | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | 30g 0s 0c / 45g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35615 | Glowworm Cavern Bindings | northrend/rare/armor/req-73 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 18.2%; 3 realms | 11g 0s 0c / 15g 0s 0c / 24g 0s 0c | 14g 0s 0c / 19g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35616 | Spored Tendrils Spaulders | northrend/rare/armor/req-73 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 22.7%; 3 realms | 12g 0s 0c / 17g 0s 0c / 25g 0s 0c | 14g 0s 0c / 20g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35639 | Brighthelm of Guarding | northrend/rare/armor/req-74 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 78.5%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 30g 0s 0c / 45g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35640 | Darkweb Bindings | northrend/rare/armor/req-74 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 40.0%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35641 | Scytheclaw Boots | northrend/rare/armor/req-74 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 20.0%; 3 realms | 17g 0s 0c / 23g 0s 0c / 35g 0s 0c | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35652 | Incessant Torch | northrend/rare/weapons/req-75 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 32.0%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35653 | Girdle of the Mystical Prison | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 47.3%; 3 realms | 35g 0s 0c / 50g 0s 0c / 90g 0s 0c | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35654 | Bindings of the Bastille | northrend/rare/armor/req-75 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 16.0%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35664 | Unknown Archaeologist's Hammer | northrend/rare/weapons/req-72 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 36.4%; 3 realms | 16g 0s 0c / 25g 0s 0c / 50g 0s 0c | 16g 0s 0c / 22g 0s 0c / 35g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35665 | Soothing Lichen Wraps | northrend/rare/armor/req-72 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 0.0%; 3 realms | 16g 0s 0c / 25g 0s 0c / 50g 0s 0c | 11g 0s 0c / 15g 0s 0c / 24g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35666 | Mark of the Spider | northrend/rare/accessories/req-72 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 13.6%; 3 realms | 14g 0s 0c / 23g 0s 0c / 45g 0s 0c | 13g 0s 0c / 18g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35681 | Unrelenting Blade | northrend/rare/weapons/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 47.3%; 3 realms | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35682 | Rune Giant Bindings | northrend/rare/armor/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 40.5%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 35683 | Palladium Ring | northrend/rare/accessories/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 54.1%; 3 realms | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 36976 | Ring-Lord's Leggings | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 78.4%; 3 realms | 45g 0s 0c / 65g 0s 0c / 110g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 36977 | Bindings of the Construct | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 18.9%; 3 realms | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 36978 | Ley-Whelphide Belt | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 89.2%; 3 realms | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 36997 | Sash of the Hardened Watcher | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 35.1%; 3 realms | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 36999 | Boots of the Terrestrial Guardian | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 75.7%; 3 realms | 35g 0s 0c / 55g 0s 0c / 95g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37000 | Storming Vortex Bracers | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 61.1%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 35g 0s 0c / 55g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37068 | Berserker's Sabatons | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 83.4%; 3 realms | 45g 0s 0c / 65g 0s 0c / 110g 0s 0c | 45g 0s 0c / 65g 0s 0c / 110g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37069 | Dragonflayer Seer's Bindings | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 2.7%; 3 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37070 | Tundra Wolf Boots | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 83.8%; 3 realms | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37115 | Crusader's Square Pauldrons | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 5.4%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37116 | Epaulets of Market Row | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 32.4%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37117 | King's Square Bracers | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 27.0%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37743 | Legguards of Brutalization | outland/rare/armor/req-69 | 0 | 0 / 0 | 1 | outland/rare; rank 88.9%; 3 realms | 12g 0s 0c / 17g 0s 0c / 25g 0s 0c | 14g 0s 0c / 20g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37744 | Horrorblood Treads | outland/rare/armor/req-69 | 0 | 0 / 0 | 1 | outland/rare; rank 56.9%; 3 realms | 8g 50s 0c / 12g 0s 0c / 19g 0s 0c | 11g 0s 0c / 16g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37745 | Greenhealer's Garb | outland/rare/armor/req-69 | 0 | 0 / 0 | 0 | outland/rare; rank 7.4%; 3 realms | 8g 50s 0c / 12g 0s 0c / 19g 0s 0c | 7g 0s 0c / 10g 0s 0c / 16g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37746 | Helm of the Burning Soul | outland/rare/armor/req-69 | 0 | 0 / 0 | 1 | outland/rare; rank 62.5%; 3 realms | 10g 0s 0c / 15g 0s 0c / 25g 0s 0c | 12g 0s 0c / 17g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37747 | Beneficent Bulwark | outland/rare/accessories/req-69 | 0 | 0 / 0 | 0 | outland/rare; rank 92.6%; 3 realms | 10g 0s 0c / 14g 0s 0c / 22g 0s 0c | 14g 0s 0c / 20g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37748 | Winterfall's Frozen Necklace | outland/rare/accessories/req-69 | 0 | 0 / 0 | 0 | outland/rare; rank 25.9%; 3 realms | 9g 50s 0c / 13g 0s 0c / 21g 0s 0c | 8g 50s 0c / 12g 0s 0c / 19g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37749 | Shocking Claws | outland/rare/weapons/req-70 | 0 | 0 / 0 | 0 | outland/rare; rank 40.3%; 3 realms | 7g 0s 0c / 10g 0s 0c / 16g 0s 0c | 9g 50s 0c / 14g 0s 0c / 25g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37751 | Tooga's Lost Toenail | outland/rare/accessories/req-70 | 0 | 0 / 0 | 0 | outland/rare; rank 73.6%; 3 realms | 14g 0s 0c / 20g 0s 0c / 30g 0s 0c | 12g 0s 0c / 18g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37752 | Sandals of Broken Dreams | outland/rare/armor/req-70 | 2 | 1 / 1 | 0 | direct local sale; 3 external realms observed | 8g 60s 88c / 9g 56s 53c / 11g 95s 66c | 8g 60s 88c / 9g 56s 53c / 11g 95s 66c | accept-sparse-direct-sale | low |
| 37753 | Mendicant's Robe of Mendacity | northrend/rare/armor/req-71 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 43.2%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 16g 0s 0c / 24g 0s 0c / 40g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37754 | Shimmersteel Hood | northrend/rare/armor/req-72 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 27.3%; 3 realms | 17g 0s 0c / 24g 0s 0c / 40g 0s 0c | 14g 0s 0c / 20g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37755 | Leggings of the Icy Heart | northrend/rare/armor/req-73 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 50.0%; 3 realms | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | 17g 0s 0c / 25g 0s 0c / 45g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37756 | Zoe's Comforting Cape | northrend/rare/armor/req-74 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 72.5%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 25g 0s 0c / 40g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37757 | Charlotte's Chastizing Pauldrons | northrend/rare/armor/req-75 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 48.5%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 24g 0s 0c / 35g 0s 0c / 60g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37758 | Raine's Choker of Combustion | northrend/rare/accessories/req-76 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 24.0%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37759 | Rhie-ay's Clutching Gauntlets | northrend/rare/armor/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 51.0%; 3 realms | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | 35g 0s 0c / 50g 0s 0c / 90g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37760 | Cracklefire Wristguards | northrend/rare/armor/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 21.6%; 3 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37761 | Shimmerthread Girdle | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 16.2%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37762 | Many-Pocketed Belt | outland/rare/armor/req-70 | 0 | 0 / 0 | 1 | outland/rare; rank 68.1%; 3 realms | 12g 0s 0c / 17g 0s 0c / 25g 0s 0c | 12g 0s 0c / 17g 0s 0c / 30g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37763 | Treads of the Purifier | northrend/rare/armor/req-71 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 53.4%; 3 realms | 15g 0s 0c / 21g 0s 0c / 35g 0s 0c | 17g 0s 0c / 25g 0s 0c / 45g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37764 | Corehound Fang Shoulderpads | northrend/rare/armor/req-72 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 60.2%; 3 realms | 17g 0s 0c / 24g 0s 0c / 40g 0s 0c | 17g 0s 0c / 25g 0s 0c / 45g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37765 | Leggings of the Water Moccasin | northrend/rare/armor/req-74 | 0 | 0 / 0 | 1 | northrend/rare/74-76; rank 12.0%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 17g 0s 0c / 24g 0s 0c / 40g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37766 | Bracers of Unmitigated Larceny | northrend/rare/armor/req-75 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 0.0%; 3 realms | 17g 0s 0c / 23g 0s 0c / 35g 0s 0c | 15g 0s 0c / 21g 0s 0c / 35g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37767 | Ryft's Deathgaze | northrend/rare/armor/req-76 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 60.5%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 25g 0s 0c / 40g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37768 | Leggings of Violent Exsanguination | northrend/rare/armor/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 58.1%; 3 realms | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37769 | Gnarled Shovelhorn Spaulders | northrend/rare/armor/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 58.1%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37770 | Bulge-Concealing Breastplate | northrend/rare/armor/req-77 | 0 | 0 / 0 | 1 | northrend/rare/77-79; rank 13.5%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37771 | Wristguards of Verdant Recovery | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 0.0%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37772 | Wub's Electrospike Spaulders | outland/rare/armor/req-70 | 0 | 0 / 0 | 1 | outland/rare; rank 18.5%; 3 realms | 11g 0s 0c / 15g 0s 0c / 24g 0s 0c | 8g 0s 0c / 11g 0s 0c / 18g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37773 | Shock-Inducing Girdle | northrend/rare/armor/req-71 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 4.5%; 3 realms | 13g 0s 0c / 18g 0s 0c / 30g 0s 0c | 12g 0s 0c / 16g 0s 0c / 25g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37774 | Leggings of Aqueous Dissolution | northrend/rare/armor/req-72 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 87.5%; 3 realms | 11g 0s 0c / 15g 0s 0c / 24g 0s 0c | 24g 0s 0c / 35g 0s 0c / 60g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37775 | Helm of the Broken Ram | northrend/rare/armor/req-73 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 46.6%; 3 realms | 17g 0s 0c / 23g 0s 0c / 35g 0s 0c | 16g 0s 0c / 24g 0s 0c / 40g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37776 | Bracers of Accurate Fire | northrend/rare/armor/req-74 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 28.0%; 3 realms | 17g 0s 0c / 23g 0s 0c / 35g 0s 0c | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37777 | Bracers of Sizzling Heat | northrend/rare/armor/req-75 | 0 | 0 / 0 | 2 | northrend/rare/74-76; rank 51.5%; 3 realms | 15g 0s 0c / 21g 0s 0c / 35g 0s 0c | 24g 0s 0c / 35g 0s 0c / 60g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37778 | Girdle of Unerring Flight | northrend/rare/armor/req-76 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 39.5%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37779 | Nixod's Chain-Threshed Spaulders | northrend/rare/armor/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 73.0%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37780 | Condor-Bone Chestguard | northrend/rare/armor/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 29.7%; 3 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37781 | Grips of the Warming Heart | northrend/rare/armor/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 10.8%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37782 | Gauntlets of the Cheerful Hearth | outland/rare/armor/req-70 | 0 | 0 / 0 | 1 | outland/rare; rank 11.1%; 3 realms | 12g 0s 0c / 16g 0s 0c / 25g 0s 0c | 7g 0s 0c / 10g 0s 0c / 16g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37783 | Blood-Tempered Spaulders | northrend/rare/armor/req-71 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 36.4%; 3 realms | 14g 0s 0c / 19g 0s 0c / 30g 0s 0c | 15g 0s 0c / 22g 0s 0c / 40g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37785 | Girdle of the Howling Berserker | northrend/rare/armor/req-73 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 77.3%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37786 | Legguards of the Forlorn Seas | northrend/rare/armor/req-74 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 60.0%; 3 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37787 | Greathelm of the Unyielding Bull | northrend/rare/armor/req-75 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 72.0%; 3 realms | 30g 0s 0c / 45g 0s 0c / 80g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37789 | Gauntlets of Disembowelment | northrend/rare/armor/req-76 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 8.0%; 3 realms | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | 17g 0s 0c / 23g 0s 0c / 35g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37790 | Belt of Crystalline Tears | northrend/rare/armor/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 24.3%; 3 realms | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37792 | Agin's Crushing Carapace | northrend/rare/armor/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 91.9%; 3 realms | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37793 | Skullcage of Eternal Terror | northrend/rare/armor/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 70.3%; 3 realms | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37794 | Torta's Oversized Choker | northrend/rare/accessories/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 8.1%; 3 realms | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37795 | Grips of the Valiant Champion | northrend/rare/armor/req-72 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 67.0%; 3 realms | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37796 | Earthbound Cape | northrend/rare/armor/req-72 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 95.5%; 3 realms | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37797 | Cloak of the Agile Mind | northrend/rare/armor/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 86.5%; 3 realms | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37802 | Elanor's Edge | northrend/rare/weapons/req-73 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 9.1%; 3 realms | 15g 0s 0c / 22g 0s 0c / 40g 0s 0c | 12g 0s 0c / 17g 0s 0c / 25g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37803 | Lola's Lifegiving Branch | northrend/rare/weapons/req-71 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 56.8%; 3 realms | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | 17g 0s 0c / 25g 0s 0c / 45g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37804 | Bloodwood Greatstaff | northrend/rare/weapons/req-76 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 56.0%; 3 realms | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37805 | Melia's Magnificent Scepter | northrend/rare/weapons/req-75 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 84.5%; 3 realms | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | 30g 0s 0c / 45g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37806 | Zabra's Misplaced Staff | northrend/rare/weapons/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 97.3%; 3 realms | 45g 0s 0c / 65g 0s 0c / 100g 0s 0c | 50g 0s 0c / 70g 0s 0c / 110g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37807 | Lydia's Sharpened Swordbreaker | northrend/rare/weapons/req-74 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 87.5%; 3 realms | 35g 0s 0c / 50g 0s 0c / 80g 0s 0c | 30g 0s 0c / 45g 0s 0c / 80g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37808 | Dragonjaw Mauler | northrend/rare/weapons/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 62.2%; 3 realms | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37809 | Roc-Feather Longbow | northrend/rare/weapons/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 44.9%; 2 realms | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | 35g 0s 0c / 50g 0s 0c / 90g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37810 | Blade-Binding Bulwark | northrend/rare/accessories/req-76 | 0 | 0 / 0 | 1 | northrend/rare/74-76; rank 44.0%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37811 | Captain Carver's Persuader | northrend/rare/weapons/req-73 | 0 | 0 / 0 | 1 | northrend/rare/71-73; rank 70.5%; 3 realms | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37812 | Petrified Ironwood Smasher | northrend/rare/weapons/req-76 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 84.0%; 3 realms | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37813 | Banner Slicer | northrend/rare/weapons/req-75 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 69.5%; 3 realms | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | 25g 0s 0c / 40g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37817 | Branch of Sinful Reprieve | northrend/rare/accessories/req-73 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 73.9%; 3 realms | 22g 0s 0c / 30g 0s 0c / 50g 0s 0c | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37819 | Milan's Mastercraft Band | northrend/rare/accessories/req-71 | 0 | 0 / 0 | 1 | northrend/rare/71-73; rank 90.9%; 3 realms | 18g 0s 0c / 25g 0s 0c / 40g 0s 0c | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37820 | Worgen's Ring of Revitalization | northrend/rare/accessories/req-72 | 0 | 0 / 0 | 0 | northrend/rare/71-73; rank 63.6%; 3 realms | 17g 0s 0c / 25g 0s 0c / 45g 0s 0c | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37821 | Raine's Signet of Blasting | northrend/rare/accessories/req-74 | 0 | 0 / 0 | 0 | northrend/rare/74-76; rank 68.0%; 3 realms | 20g 0s 0c / 30g 0s 0c / 55g 0s 0c | 30g 0s 0c / 40g 0s 0c / 65g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37822 | Twisted Puzzle-Ring | northrend/rare/accessories/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 63.2%; 3 realms | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | 35g 0s 0c / 55g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37823 | Draconic Choker of Ferocity | northrend/rare/accessories/req-77 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 81.1%; 3 realms | 40g 0s 0c / 55g 0s 0c / 90g 0s 0c | 45g 0s 0c / 60g 0s 0c / 95g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37824 | Gwyneth's Runed Dragonwand | northrend/rare/weapons/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 37.8%; 3 realms | 25g 0s 0c / 35g 0s 0c / 55g 0s 0c | 30g 0s 0c / 45g 0s 0c / 70g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 37835 | Je'Tze's Bell | level-80/200-212/trinkets | 0 | 0 / 0 | 0 | level-80/200-205; rank 54.7%; 3 realms | 180g 0s 0c / 260g 0s 0c / 460g 0s 0c | 180g 0s 0c / 260g 0s 0c / 460g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 39194 | Rusted-Link Spiked Gauntlets | level-80/200-212/mail | 0 | 0 / 0 | 0 | level-80/200-205; rank 81.2%; 3 realms | 200g 0s 0c / 290g 0s 0c / 500g 0s 0c | 220g 0s 0c / 310g 0s 0c / 500g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 39235 | Bone-Framed Bracers | level-80/200-212/plate | 0 | 0 / 0 | 0 | level-80/200-205; rank 6.2%; 3 realms | 170g 0s 0c / 230g 0s 0c / 370g 0s 0c | 120g 0s 0c / 160g 0s 0c / 260g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 39283 | Putrescent Bands | level-80/200-212/leather | 0 | 0 / 0 | 0 | level-80/200-205; rank 50.0%; 3 realms | 180g 0s 0c / 270g 0s 0c / 470g 0s 0c | 170g 0s 0c / 250g 0s 0c / 440g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 39310 | Mantle of the Extensive Mind | level-80/200-212/cloth | 0 | 0 / 0 | 0 | level-80/200-205; rank 40.6%; 3 realms | 120g 0s 0c / 200g 0s 0c / 400g 0s 0c | 160g 0s 0c / 230g 0s 0c / 400g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 39472 | Chain of Latent Energies | level-80/200-212/neck | 0 | 0 / 0 | 0 | level-80/200-205; rank 68.8%; 3 realms | 210g 0s 0c / 290g 0s 0c / 460g 0s 0c | 210g 0s 0c / 290g 0s 0c / 460g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 39717 | Inexorable Sabatons | level-80/213-225/plate | 0 | 0 / 0 | 0 | level-80/213-218; rank 71.4%; 3 realms | 280g 0s 0c / 410g 0s 0c / 725g 0s 0c | 360g 0s 0c / 525g 0s 0c / 925g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 39733 | Gloves of Token Respect | level-80/213-225/cloth | 0 | 0 / 0 | 0 | level-80/213-218; rank 14.3%; 3 realms | 240g 0s 0c / 350g 0s 0c / 625g 0s 0c | 230g 0s 0c / 320g 0s 0c / 500g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 39762 | Torn Web Wrapping | level-80/213-225/mail | 0 | 0 / 0 | 0 | level-80/213-218; rank 28.6%; 3 realms | 290g 0s 0c / 430g 0s 0c / 750g 0s 0c | 250g 0s 0c / 370g 0s 0c / 650g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40187 | Poignant Sabatons | level-80/213-225/plate | 0 | 0 / 0 | 0 | level-80/213-218; rank 35.7%; 3 realms | 270g 0s 0c / 390g 0s 0c / 675g 0s 0c | 290g 0s 0c / 400g 0s 0c / 650g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40206 | Iron-Spring Jumpers | level-80/213-225/plate | 0 | 0 / 0 | 0 | level-80/213-218; rank 42.9%; 3 realms | 320g 0s 0c / 470g 0s 0c / 825g 0s 0c | 300g 0s 0c / 420g 0s 0c / 675g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40246 | Boots of Impetuous Ideals | level-80/213-225/cloth | 0 | 0 / 0 | 0 | level-80/213-218; rank 57.1%; 3 realms | 340g 0s 0c / 500g 0s 0c / 875g 0s 0c | 350g 0s 0c / 480g 0s 0c / 775g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40270 | Boots of Septic Wounds | level-80/213-225/leather | 0 | 0 / 0 | 0 | level-80/213-218; rank 33.9%; 3 realms | 330g 0s 0c / 490g 0s 0c / 850g 0s 0c | 270g 0s 0c / 390g 0s 0c / 675g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40282 | Slime Stream Bands | level-80/213-225/mail | 0 | 0 / 0 | 0 | level-80/213-218; rank 17.9%; 3 realms | 220g 0s 0c / 330g 0s 0c / 575g 0s 0c | 220g 0s 0c / 330g 0s 0c / 575g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40302 | Benefactor's Gauntlets | level-80/213-225/mail | 0 | 0 / 0 | 0 | level-80/213-218; rank 60.7%; 3 realms | 330g 0s 0c / 525g 0s 0c / 1,050g 0s 0c | 330g 0s 0c / 490g 0s 0c / 850g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40305 | Spaulders of Egotism | level-80/213-225/leather | 0 | 0 / 0 | 0 | level-80/213-218; rank 76.8%; 3 realms | 360g 0s 0c / 525g 0s 0c / 925g 0s 0c | 370g 0s 0c / 550g 0s 0c / 975g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40338 | Bindings of Yearning | level-80/213-225/cloth | 0 | 0 / 0 | 0 | level-80/213-218; rank 12.5%; 3 realms | 220g 0s 0c / 360g 0s 0c / 725g 0s 0c | 220g 0s 0c / 320g 0s 0c / 550g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40347 | Zeliek's Gauntlets | level-80/213-225/plate | 0 | 0 / 0 | 0 | level-80/213-218; rank 66.1%; 3 realms | 330g 0s 0c / 525g 0s 0c / 1,050g 0s 0c | 340g 0s 0c / 500g 0s 0c / 875g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40362 | Gloves of Fast Reactions | level-80/213-225/leather | 0 | 0 / 0 | 0 | level-80/213-218; rank 82.1%; 3 realms | 340g 0s 0c / 550g 0s 0c / 1,100g 0s 0c | 390g 0s 0c / 575g 0s 0c / 1,000g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40426 | Signet of the Accord | level-80/200-212/rings | 0 | 0 / 0 | 0 | level-80/200-205; rank 59.4%; 3 realms | 170g 0s 0c / 250g 0s 0c / 440g 0s 0c | 180g 0s 0c / 270g 0s 0c / 470g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40439 | Mantle of the Eternal Sentinel | level-80/213-225/leather | 0 | 0 / 0 | 0 | level-80/213-218; rank 50.0%; 3 realms | 280g 0s 0c / 450g 0s 0c / 900g 0s 0c | 320g 0s 0c / 450g 0s 0c / 725g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40474 | Surge Needle Ring | level-80/213-225/rings | 0 | 0 / 0 | 0 | level-80/213-218; rank 87.5%; 3 realms | 250g 0s 0c / 370g 0s 0c / 650g 0s 0c | 390g 0s 0c / 575g 0s 0c / 1,000g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 40558 | Arcanic Tramplers | level-80/226-239/cloth | 0 | 0 / 0 | 0 | level-80/226-239; rank 38.5%; 3 realms | 625g 0s 0c / 1,000g 0s 0c / 2,000g 0s 0c | 600g 0s 0c / 825g 0s 0c / 1,300g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 43573 | Tears of Bitter Anguish | level-80/200-212/trinkets | 0 | 0 / 0 | 0 | level-80/200-205; rank 93.8%; 3 realms | 210g 0s 0c / 310g 0s 0c / 550g 0s 0c | 240g 0s 0c / 340g 0s 0c / 550g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 43611 | Krol Cleaver | level-80/200-212/hand | 0 | 0 / 0 | 0 | level-80/200-205; rank 78.1%; 3 realms | 180g 0s 0c / 290g 0s 0c / 575g 0s 0c | 210g 0s 0c / 310g 0s 0c / 550g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 43612 | Spineslicer | level-80/200-212/ranged | 0 | 0 / 0 | 0 | level-80/200-205; rank 75.0%; 3 realms | 170g 0s 0c / 280g 0s 0c / 550g 0s 0c | 220g 0s 0c / 300g 0s 0c / 480g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 43613 | The Dusk Blade | level-80/200-212/hand | 0 | 0 / 0 | 0 | level-80/200-205; rank 100.0%; 3 realms | 220g 0s 0c / 330g 0s 0c / 575g 0s 0c | 250g 0s 0c / 350g 0s 0c / 550g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 44308 | Signet of Edward the Odd | level-80/200-212/rings | 0 | 0 / 0 | 0 | level-80/200-205; rank 25.0%; 3 realms | 130g 0s 0c / 180g 0s 0c / 290g 0s 0c | 140g 0s 0c / 200g 0s 0c / 320g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 44309 | Sash of Jordan | level-80/200-212/cloth | 0 | 0 / 0 | 0 | level-80/200-205; rank 18.8%; 3 realms | 140g 0s 0c / 200g 0s 0c / 320g 0s 0c | 140g 0s 0c / 190g 0s 0c / 300g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 44310 | Namlak's Supernumerary Sticker | level-80/200-212/hand | 0 | 0 / 0 | 0 | level-80/200-205; rank 0.0%; 3 realms | 170g 0s 0c / 240g 0s 0c / 380g 0s 0c | 110g 0s 0c / 150g 0s 0c / 240g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 44311 | Avool's Sword of Jin | level-80/200-212/hand | 0 | 0 / 0 | 0 | level-80/200-205; rank 43.8%; 3 realms | 120g 0s 0c / 160g 0s 0c / 260g 0s 0c | 170g 0s 0c / 240g 0s 0c / 380g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 44312 | Wapach's Spaulders of Solidarity | level-80/200-212/plate | 0 | 0 / 0 | 0 | level-80/200-205; rank 12.5%; 3 realms | 140g 0s 0c / 190g 0s 0c / 300g 0s 0c | 130g 0s 0c / 180g 0s 0c / 290g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 44313 | Zom's Crackling Bulwark | level-80/200-212/offhands | 1 | 1 / 1 | 0 | direct local sale; 3 external realms observed | 297g 50s 0c / 350g 0s 0c / 455g 0s 0c | 297g 50s 0c / 350g 0s 0c / 455g 0s 0c | accept-sparse-direct-sale | low |
| 44505 | Dustbringer | northrend/rare/weapons/req-78 | 0 | 0 / 0 | 0 | northrend/rare/77-79; rank 87.5%; 2 realms | 35g 0s 0c / 60g 0s 0c / 120g 0s 0c | 45g 0s 0c / 65g 0s 0c / 110g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45107 | Iron Riveted War Helm | level-80/226-239/plate | 0 | 0 / 0 | 0 | level-80/226-239; rank 47.1%; 3 realms | 625g 0s 0c / 925g 0s 0c / 1,600g 0s 0c | 600g 0s 0c / 875g 0s 0c / 1,550g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45141 | Proto-hide Leggings | level-80/226-239/leather | 0 | 0 / 0 | 0 | level-80/226-239; rank 35.6%; 3 realms | 470g 0s 0c / 650g 0s 0c / 1,050g 0s 0c | 550g 0s 0c / 800g 0s 0c / 1,400g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45167 | Lifeforge Breastplate | level-80/226-239/plate | 0 | 0 / 0 | 0 | level-80/226-239; rank 15.4%; 3 realms | 550g 0s 0c / 750g 0s 0c / 1,200g 0s 0c | 470g 0s 0c / 650g 0s 0c / 1,050g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45237 | Phaelia's Vestments of the Sprouting Seed | level-80/226-239/leather | 0 | 0 / 0 | 0 | level-80/226-239; rank 23.1%; 3 realms | 500g 0s 0c / 750g 0s 0c / 1,300g 0s 0c | 500g 0s 0c / 700g 0s 0c / 1,100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45247 | Signet of the Earthshaker | level-80/226-239/rings | 0 | 0 / 0 | 0 | level-80/226-239; rank 76.0%; 3 realms | 650g 0s 0c / 950g 0s 0c / 1,650g 0s 0c | 750g 0s 0c / 1,100g 0s 0c / 1,950g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45274 | Leggings of the Stoneweaver | level-80/226-239/mail | 0 | 0 / 0 | 0 | level-80/226-239; rank 18.3%; 3 realms | 430g 0s 0c / 600g 0s 0c / 950g 0s 0c | 460g 0s 0c / 675g 0s 0c / 1,200g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45291 | Combustion Bracers | level-80/213-225/cloth | 0 | 0 / 0 | 0 | level-80/219-225; rank 0.0%; 3 realms | 280g 0s 0c / 390g 0s 0c / 625g 0s 0c | 280g 0s 0c / 390g 0s 0c / 625g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45301 | Bracers of the Smothering Inferno | level-80/213-225/mail | 0 | 0 / 0 | 0 | level-80/219-225; rank 30.0%; 3 realms | 360g 0s 0c / 575g 0s 0c / 1,150g 0s 0c | 400g 0s 0c / 550g 0s 0c / 875g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45316 | Armbraces of the Vibrant Flame | level-80/213-225/mail | 0 | 0 / 0 | 0 | level-80/219-225; rank 20.0%; 3 realms | 440g 0s 0c / 650g 0s 0c / 1,150g 0s 0c | 350g 0s 0c / 490g 0s 0c / 775g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45322 | Cloak of the Iron Council | level-80/213-225/cloaks | 0 | 0 / 0 | 0 | level-80/219-225; rank 80.0%; 3 realms | 575g 0s 0c / 850g 0s 0c / 1,500g 0s 0c | 550g 0s 0c / 800g 0s 0c / 1,400g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45435 | Cowl of the Absolute | level-80/226-239/cloth | 0 | 0 / 0 | 0 | level-80/226-239; rank 92.3%; 3 realms | 825g 0s 0c / 1,150g 0s 0c / 1,850g 0s 0c | 875g 0s 0c / 1,200g 0s 0c / 1,900g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45450 | Northern Barrier | level-80/226-239/offhands | 0 | 0 / 0 | 0 | level-80/226-239; rank 87.5%; 3 realms | 775g 0s 0c / 1,150g 0s 0c / 2,000g 0s 0c | 775g 0s 0c / 1,150g 0s 0c / 2,000g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45468 | Leggings of Lost Love | level-80/226-239/cloth | 0 | 0 / 0 | 0 | level-80/226-239; rank 70.2%; 3 realms | 775g 0s 0c / 1,150g 0s 0c / 2,000g 0s 0c | 725g 0s 0c / 1,050g 0s 0c / 1,850g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45480 | Nymph Heart Charm | level-80/226-239/neck | 0 | 0 / 0 | 0 | level-80/226-239; rank 58.7%; 3 realms | 625g 0s 0c / 875g 0s 0c / 1,400g 0s 0c | 650g 0s 0c / 950g 0s 0c / 1,650g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45493 | Asimov's Drape | level-80/226-239/cloaks | 0 | 0 / 0 | 0 | level-80/226-239; rank 64.4%; 3 realms | 750g 0s 0c / 1,050g 0s 0c / 1,700g 0s 0c | 675g 0s 0c / 1,000g 0s 0c / 1,750g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45504 | Darkcore Leggings | level-80/226-239/mail | 0 | 0 / 0 | 0 | level-80/226-239; rank 52.9%; 3 realms | 600g 0s 0c / 825g 0s 0c / 1,300g 0s 0c | 625g 0s 0c / 925g 0s 0c / 1,600g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45680 | Armbands of the Construct | level-80/213-225/plate | 0 | 0 / 0 | 0 | level-80/219-225; rank 10.0%; 3 realms | 320g 0s 0c / 440g 0s 0c / 700g 0s 0c | 320g 0s 0c / 440g 0s 0c / 700g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45704 | Shawl of the Shattered Giant | level-80/213-225/cloaks | 0 | 0 / 0 | 0 | level-80/219-225; rank 87.5%; 3 realms | 575g 0s 0c / 800g 0s 0c / 1,300g 0s 0c | 575g 0s 0c / 850g 0s 0c / 1,500g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45709 | Nimble Climber's Belt | level-80/213-225/leather | 0 | 0 / 0 | 0 | level-80/219-225; rank 50.0%; 3 realms | 410g 0s 0c / 600g 0s 0c / 1,050g 0s 0c | 470g 0s 0c / 650g 0s 0c / 1,050g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45859 | The 5 Ring | level-80/200-212/rings | 0 | 0 / 0 | 0 | level-80/206-212; rank 50.0%; 3 realms | 220g 0s 0c / 350g 0s 0c / 700g 0s 0c | 240g 0s 0c / 350g 0s 0c / 625g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45874 | Signet of Winter | level-80/213-225/rings | 0 | 0 / 0 | 0 | level-80/219-225; rank 40.0%; 3 realms | 390g 0s 0c / 575g 0s 0c / 1,000g 0s 0c | 430g 0s 0c / 600g 0s 0c / 950g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45927 | Handwraps of Resonance | level-80/213-225/cloth | 0 | 0 / 0 | 0 | level-80/219-225; rank 57.5%; 3 realms | 550g 0s 0c / 800g 0s 0c / 1,400g 0s 0c | 480g 0s 0c / 700g 0s 0c / 1,250g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 45975 | Cable of the Metrognome | level-80/213-225/plate | 0 | 0 / 0 | 0 | level-80/219-225; rank 75.0%; 3 realms | 480g 0s 0c / 700g 0s 0c / 1,250g 0s 0c | 550g 0s 0c / 775g 0s 0c / 1,250g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 46009 | Bindings of the Depths | level-80/213-225/leather | 0 | 0 / 0 | 0 | level-80/219-225; rank 68.8%; 3 realms | 430g 0s 0c / 700g 0s 0c / 1,400g 0s 0c | 500g 0s 0c / 750g 0s 0c / 1,300g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 46970 | Drape of the Untamed Predator | level-80/245-258/cloaks | 0 | 0 / 0 | 0 | level-80/245-258; rank 88.9%; 3 realms | 1,200g 0s 0c / 1,700g 0s 0c / 2,700g 0s 0c | 1,200g 0s 0c / 1,700g 0s 0c / 2,700g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 47089 | Cloak of Displacement | level-80/245-258/cloaks | 0 | 0 / 0 | 0 | level-80/245-258; rank 100.0%; 3 realms | 1,300g 0s 0c / 1,800g 0s 0c / 2,900g 0s 0c | 1,300g 0s 0c / 1,800g 0s 0c / 2,900g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 47105 | The Executioner's Malice | level-80/245-258/neck | 0 | 0 / 0 | 0 | level-80/245-258; rank 33.3%; 3 realms | 975g 0s 0c / 1,450g 0s 0c / 2,550g 0s 0c | 825g 0s 0c / 1,150g 0s 0c / 1,850g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 47149 | Signet of the Traitor King | level-80/245-258/rings | 0 | 0 / 0 | 0 | level-80/245-258; rank 0.0%; 3 realms | 850g 0s 0c / 1,250g 0s 0c / 2,200g 0s 0c | 550g 0s 0c / 775g 0s 0c / 1,250g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 47223 | Ring of the Darkmender | level-80/245-258/rings | 0 | 0 / 0 | 0 | level-80/245-258; rank 54.2%; 3 realms | 775g 0s 0c / 1,150g 0s 0c / 2,000g 0s 0c | 925g 0s 0c / 1,350g 0s 0c / 2,350g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 47257 | Cloak of the Untamed Predator | level-80/245-258/cloaks | 0 | 0 / 0 | 0 | level-80/245-258; rank 70.8%; 3 realms | 925g 0s 0c / 1,350g 0s 0c / 2,350g 0s 0c | 1,000g 0s 0c / 1,500g 0s 0c / 2,650g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 47278 | Circle of the Darkmender | level-80/245-258/rings | 0 | 0 / 0 | 0 | level-80/245-258; rank 45.8%; 3 realms | 725g 0s 0c / 1,000g 0s 0c / 1,600g 0s 0c | 850g 0s 0c / 1,250g 0s 0c / 2,200g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 47291 | Shroud of Displacement | level-80/245-258/cloaks | 0 | 0 / 0 | 0 | level-80/245-258; rank 62.5%; 3 realms | 1,000g 0s 0c / 1,500g 0s 0c / 2,650g 0s 0c | 975g 0s 0c / 1,450g 0s 0c / 2,550g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 47297 | The Executioner's Vice | level-80/245-258/neck | 0 | 0 / 0 | 0 | level-80/245-258; rank 22.2%; 3 realms | 650g 0s 0c / 900g 0s 0c / 1,450g 0s 0c | 725g 0s 0c / 1,000g 0s 0c / 1,600g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 47315 | Band of the Traitor King | level-80/245-258/rings | 0 | 0 / 0 | 0 | level-80/245-258; rank 20.8%; 3 realms | 550g 0s 0c / 775g 0s 0c / 1,250g 0s 0c | 675g 0s 0c / 1,000g 0s 0c / 1,750g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 48663 | Tankard O' Terror | level-80/226-239/hand | 0 | 0 / 0 | 0 | level-80/226-239; rank 12.5%; 2 realms | 430g 0s 0c / 625g 0s 0c / 1,100g 0s 0c | 430g 0s 0c / 625g 0s 0c / 1,100g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 49967 | Marrowgar's Frigid Eye | level-80/264+/rings | 0 | 0 / 0 | 0 | level-80/264+; rank 82.8%; 2 realms | 1,750g 0s 0c / 2,550g 0s 0c / 4,450g 0s 0c | 1,750g 0s 0c / 2,550g 0s 0c / 4,450g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 49994 | The Lady's Brittle Bracers | level-80/264+/cloth | 0 | 0 / 0 | 0 | level-80/264+; rank 64.1%; 2 realms | 1,550g 0s 0c / 2,300g 0s 0c / 4,050g 0s 0c | 1,550g 0s 0c / 2,250g 0s 0c / 3,950g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50001 | Ikfirus's Sack of Wonder | level-80/264+/leather | 0 | 0 / 0 | 0 | level-80/264+; rank 78.1%; 2 realms | 1,550g 0s 0c / 2,250g 0s 0c / 3,950g 0s 0c | 1,650g 0s 0c / 2,450g 0s 0c / 4,300g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50015 | Belt of the Blood Nova | level-80/264+/mail | 0 | 0 / 0 | 0 | level-80/264+; rank 45.3%; 2 realms | 1,350g 0s 0c / 2,000g 0s 0c / 3,500g 0s 0c | 1,350g 0s 0c / 1,950g 0s 0c / 3,400g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50020 | Raging Behemoth's Shoulderplates | level-80/264+/plate | 0 | 0 / 0 | 0 | level-80/264+; rank 68.8%; 2 realms | 1,650g 0s 0c / 2,400g 0s 0c / 4,200g 0s 0c | 1,550g 0s 0c / 2,300g 0s 0c / 4,050g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50038 | Carapace of Forgotten Kings | level-80/264+/mail | 0 | 0 / 0 | 0 | level-80/264+; rank 59.4%; 2 realms | 1,450g 0s 0c / 2,100g 0s 0c / 3,700g 0s 0c | 1,450g 0s 0c / 2,150g 0s 0c / 3,750g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50069 | Professor's Bloodied Smock | level-80/264+/leather | 0 | 0 / 0 | 0 | level-80/264+; rank 40.6%; 2 realms | 1,100g 0s 0c / 1,650g 0s 0c / 2,900g 0s 0c | 1,250g 0s 0c / 1,850g 0s 0c / 3,250g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50175 | Crypt Keeper's Bracers | level-80/264+/plate | 0 | 0 / 0 | 0 | level-80/264+; rank 50.0%; 2 realms | 1,450g 0s 0c / 2,100g 0s 0c / 3,700g 0s 0c | 1,350g 0s 0c / 2,000g 0s 0c / 3,500g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50182 | Blood Queen's Crimson Choker | level-80/264+/neck | 0 | 0 / 0 | 0 | level-80/264+; rank 87.5%; 2 realms | 1,750g 0s 0c / 2,600g 0s 0c / 4,550g 0s 0c | 1,750g 0s 0c / 2,600g 0s 0c / 4,550g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50444 | Rowan's Rifle of Silver Bullets | level-80/264+/ranged | 0 | 0 / 0 | 0 | level-80/264+; rank 12.5%; 2 realms | 950g 0s 0c / 1,400g 0s 0c / 2,450g 0s 0c | 950g 0s 0c / 1,400g 0s 0c / 2,450g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50447 | Harbinger's Bone Band | level-80/264+/rings | 0 | 0 / 0 | 0 | level-80/264+; rank 21.9%; 2 realms | 1,050g 0s 0c / 1,550g 0s 0c / 2,700g 0s 0c | 1,050g 0s 0c / 1,550g 0s 0c / 2,700g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50449 | Stiffened Corpse Shoulderpads | level-80/264+/cloth | 0 | 0 / 0 | 0 | level-80/264+; rank 17.2%; 2 realms | 1,000g 0s 0c / 1,500g 0s 0c / 2,650g 0s 0c | 1,000g 0s 0c / 1,500g 0s 0c / 2,650g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50450 | Leggings of Dubious Charms | level-80/264+/mail | 0 | 0 / 0 | 0 | level-80/264+; rank 54.7%; 2 realms | 1,200g 0s 0c / 1,800g 0s 0c / 3,150g 0s 0c | 1,450g 0s 0c / 2,100g 0s 0c / 3,700g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50451 | Belt of the Lonely Noble | level-80/264+/plate | 0 | 0 / 0 | 0 | level-80/264+; rank 26.6%; 2 realms | 1,200g 0s 0c / 1,800g 0s 0c / 3,150g 0s 0c | 1,100g 0s 0c / 1,650g 0s 0c / 2,900g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50452 | Wodin's Lucky Necklace | level-80/264+/neck | 0 | 0 / 0 | 0 | level-80/264+; rank 35.9%; 2 realms | 1,350g 0s 0c / 1,950g 0s 0c / 3,400g 0s 0c | 1,200g 0s 0c / 1,800g 0s 0c / 3,150g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50453 | Ring of Rotting Sinew | level-80/264+/rings | 0 | 0 / 0 | 0 | level-80/264+; rank 31.2%; 2 realms | 1,200g 0s 0c / 1,800g 0s 0c / 3,150g 0s 0c | 1,150g 0s 0c / 1,700g 0s 0c / 3,000g 0s 0c | accept-reviewed-starter-estimate | fallback |
| 50472 | Nightmare Ender | level-80/264+/ranged | 0 | 0 / 0 | 0 | level-80/264+; rank 73.4%; 2 realms | 1,650g 0s 0c / 2,450g 0s 0c / 4,300g 0s 0c | 1,650g 0s 0c / 2,400g 0s 0c / 4,200g 0s 0c | accept-reviewed-starter-estimate | fallback |

## Reproduction

```powershell
python scripts/estimate-ah-dropped-gear-prices.py --check
```

Publishing is a separate step and is not part of this review.
