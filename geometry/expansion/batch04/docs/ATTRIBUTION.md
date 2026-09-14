# Batch 04 source attribution

The three buildings retain mapped OpenStreetMap footprints: **© OpenStreetMap contributors, ODbL 1.0**, [copyright and attribution terms](https://www.openstreetmap.org/copyright). The local source extract remains in `geometry/completion/sources/osm_buildings.json`; original scene assets are preserved.

| Building / source | Credit and licence | Actual use and limits |
| --- | --- | --- |
| Jay Mews, `way-117010293` — [Geograph 5752102](https://www.geograph.org.uk/photo/5752102), captured 2018-04-22 | Robin Webster / Geograph; [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) | Actually inspected street context. Exact target identity and window layout unconfirmed. **Context only**, not evidence of this building’s precise facade. |
| Albert Close context, `way-642055723` — [Albert Hall Mansions, May 2018 (2)](https://commons.wikimedia.org/wiki/File:Albert_Hall_Mansions,_May_2018_(2).jpg), captured 2018-05-25 | No Swan So Fine / Wikimedia Commons; [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | Actually inspected neighbourhood facade vocabulary. Photograph shows Albert Hall Mansions 1–30; the anonymous target rear wing was not identified. **Context only**. |
| Princes Gate Court, `way-27917475` — [Geograph 396643](https://www.geograph.org.uk/photo/396643), captured 2007-04-09 | Philip Halling / Geograph; [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) | Actually inspected target courtyard photograph, adapted into simplified architectural geometry. Oblique view with tree occlusion; no rear coverage or metric calibration. Target reference, **not survey evidence**. |
| Princes Gate Court — [Westminster Council planning report pack, 2017-08-01](https://westminster.moderngov.co.uk/documents/g4385/Public%20reports%20pack%2001st-Aug-2017%2018.30%20Planning%20Applications%20Sub-Committee%202.pdf?T=10) | Westminster Council; indexed factual description, no imagery licence asserted | Search-indexed architectural summary only. Direct PDF returned HTTP 403. No council photographs, drawings or maps acquired or derived. Proposed alterations are not proof of completed work. |

The stored reference photographs retain their source licences. Credit the named photographers and link their licences when redistributing the reference package. Architectural contributions adapted from the CC photographs are identified as adaptations and must retain applicable attribution/share-alike terms. No source photograph is embedded as a texture: exported finishes are procedural/scalar materials.

Per-building source ledgers record download/inspection status, local filenames and SHA-256 hashes:

- [Jay Mews source ledger](../references/jay_mews_117010293/sources.json)
- [Albert Close source ledger](../references/albert_close_642055723/sources.json)
- [Princes Gate Court source ledger](../references/princes_gate_court/sources.json)

No Google Maps/Street View pixels or 3D tiles were acquired or used to derive this batch. Geographic label “Albert Close” is contextual, not a verified postal address for the anonymous OSM feature. See [uncertainty record](UNCERTAINTY.md) for the separation between mapped, photo-informed and artistic geometry.
