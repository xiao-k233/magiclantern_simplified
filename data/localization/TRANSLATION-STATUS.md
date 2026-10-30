# Simplified Chinese catalog status

This branch carries the Simplified Chinese localization only. English is the
built-in original and the fallback; the Language menu can switch between
English and Simplified Chinese at runtime.

- Catalog: `data/localization/zh_cn.json` (2264 messages, all with a translation).
- Compiled resource: `data/lang/zh_cn.lng` (MLLG v2, loaded from `ML/LANG/`).
- Font resource: `data/fonts/zh_cn.bfn` (972 glyphs, loaded from `ML/FONTS/`).
- The 73 unrecovered hash-only entries remain in `zh_cn-pending.json`; their
  source strings could not be recovered, so the corresponding UI text stays
  English rather than guessing a key.
- Translation provenance: ported from ryulin456/magiclantern-zh r4
  (`review/localization-v2`, GPL-2.0). Wording still benefits from native
  review; technical units, identifiers, credits and URLs are intentionally
  left unchanged.

No online translation service received firmware source or strings. Printf
argument types, order and widths are validated when compiling the catalog.
Literal percent prose can be marked `format:false`; the runtime compatibility
guard remains active at formatting call sites.
