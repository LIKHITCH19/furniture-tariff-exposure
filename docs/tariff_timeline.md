# Tariff timeline (furniture, 2025-2026)

The rules changed so often that the trade data doesn't make sense without a
calendar next to it. This is the one I used. Dates are when the change hit
goods entering the US, which is what the Census data records.

`data/reference/policy_phases.csv` turns this into five phases for the
analysis. Phases are set at the month level, so a change that landed mid-month
(Oct 14, Feb 24, Jul 24) splits that month; I put each one in the phase that
covers most of it.

## Before 2025

- Furniture from most countries entered at low MFN rates, often 0%.
- Most Chinese furniture already carried the 2018-19 Section 301 tariffs, which is why
  China's baseline effective rate in the data is about 20% while everyone else
  is near zero.

## 2025

| Date | Change |
|---|---|
| Feb 4 | 10% IEEPA "fentanyl" tariff on China |
| Mar 4 | China fentanyl tariff raised to 20% |
| Apr 5 | 10% reciprocal baseline tariff on most countries |
| Apr 9 | China reciprocal rate raised in steps, reaching 125% |
| May 14 | China reciprocal rate cut back to 10% for 90 days |
| Aug 7 | Country-specific reciprocal rates start: Vietnam 20%; Malaysia, Indonesia, Thailand and Cambodia 19% |
| Oct 14 | Section 232: 25% on certain upholstered wooden furniture and on kitchen cabinets and vanities |
| Nov 10 | China fentanyl tariff cut from 20% to 10% |

## 2026

| Date | Change |
|---|---|
| Jan 1 | Scheduled Section 232 increase pushed back to Jan 1, 2027 (proclamation of Dec 31, 2025) |
| Feb 20 | Supreme Court rules IEEPA does not authorize these tariffs |
| Feb 24 | CBP stops collecting IEEPA tariffs; a flat 10% Section 122 tariff starts the same day |
| Jul 24 | Section 122 expires (150-day limit). New Section 301 tariffs replace it: 12.5% for China, Vietnam and Thailand; 10% for Cambodia, Indonesia, Malaysia, Mexico, Canada, India and others |

The 25% Section 232 duty on upholstered wooden furniture, cabinets and vanities stays
in place through all of 2026.

## Things that affect how to read the data

- **IEEPA refunds.** After the ruling, refunds of IEEPA duties should be
  possible but were not automatic, and how to claim them was still unsettled.
  Census "calculated duty" is recorded at entry, so for Feb 2025 to Feb 2026 it
  shows what importers were charged, not what they end up keeping out of pocket.
- **Section 232 coverage is set at the 10-digit level.** At HS6, a line like
  940161 mixes covered and uncovered goods, so its effective rate sits below 25%
  plus everything else.
- **Stacking.** Not every tariff adds on top of every other one, so effective
  rates in the data are lower than adding the headline rates together. That is
  the reason to measure the rate from duty actually calculated instead of
  rebuilding it from the rules.

## Sources

- [Cozen O'Connor: Supreme Court rules President lacks IEEPA tariff authority; Section 122 tariffs imposed](https://www.cozen.com/news-resources/publications/2026/supreme-court-rules-president-lacks-ieepa-tariff-authority-president-imposes-section-122-tariffs)
- [RVIA: Section 122 tariffs replaced by new Section 301 forced labor tariffs](https://www.rvia.org/news-insights/section-122-tariffs-replaced-new-section-301-forced-labor-tariffs)
- [Z2Data: How the termination of Section 122 tariffs impacts your supply chain](https://www.z2data.com/insights/how-the-termination-of-section-122-tariffs-impacts-your-supply-chain)
- [GHY: US tariffs on lumber, upholstered furniture, cabinets and vanities](https://www.ghy.com/trade-compliance/us-tariffs-lumber-upholstered-furniture-cabinets-vanities/)
- [Mohawk Global: Section 232 tariff increase on furniture and cabinets delayed to 2027](https://mohawkglobal.com/word-from-the-white-house/furniture-and-cabinet-imports-section-232-tariff-increase-delayed-to-2027/)
- [Thompson Hine: President delays Section 232 increase on wood furniture, cabinets and vanities](https://www.thompsonhinesmartrade.com/2026/01/president-trump-delays-section-232-tariff-increase-on-wood-furniture-cabinets-and-vanities/)
- [Thompson Coburn: Reducing the 20% IEEPA fentanyl tariffs on China to 10%](https://www.thompsoncoburn.com/insights/58-november-4-2025-reducing-the-20-ieepa-fentanyl-tariffs-on-china-to-10-reciprocal-tariffs-on-china-remain-at-10-until-november-2026/)
- [Mondaq: US reduces 125% reciprocal tariffs on China to 10%](https://www.mondaq.com/china/international-trade-investment/1624812/may-13-2025-%7c-us-reduces-125-reciprocal-tariffs-against-china-to-10-for-90-days-china-reduces-its-retaliatory-tariffs-to-10-for-90-days)
- [St. Louis Fed: The shifting U.S. import landscape](https://www.stlouisfed.org/on-the-economy/2026/jan/shifting-us-import-landscape-recent-changes-tariffs-trade)
