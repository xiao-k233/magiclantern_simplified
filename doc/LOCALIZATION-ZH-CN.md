# Simplified Chinese localization (zh-cn branch)

This branch ports the file-backed localization design from
`ryulin456/magiclantern_simplified` branch `review/localization-v2`
(tip `6f1bb16`, GPL-2.0) onto upstream `142472e95`, trimmed to **Simplified
Chinese only**.

## Behaviour

- English remains the built-in original, the fallback for missing strings and
  the base language of `entry->name` / config / Lua keys.
- A fresh config defaults to Simplified Chinese
  (`menu.language` default = FNV-1a("zh_cn") & 0x7fffffff = 432070101).
- `Prefs -> Language` switches English <-> Simplified Chinese immediately with
  SET; a failed load keeps the active language and reports an `E<n>` code.
- Menu labels, help lines, choices, warnings (including printf format strings),
  submenu titles and module metadata are translated at display time; module
  binaries and the module ABI are unchanged.

## Resources on the card

- `ML/LANG/INDEX.TXT` - language list, one line per language:
  `id<TAB>display name<TAB>font id`.
- `ML/LANG/zh_cn.lng` - compiled MLLG v2 catalog (FNV-1a keyed).
- `ML/FONTS/zh_cn.bfn` - BFNT-format CJK font (972 glyphs, Noto Sans CJK).
- `ML/doc/OFL-NotoSansCJK.txt`, `ML/doc/OFL-NotoSansSC.txt` - font licenses.

`platform/Makefile` copies `data/lang/*` and `data/fonts/*.bfn` into the zip.
Missing or invalid resources fall back to English; the Language item shows the
error code and failing path.

## Build

Use the same prerequisites as upstream ML (GNU make, ARM none-eabi GCC, Python 3;
Pillow only when regenerating the font). Because `src/reboot.c` embeds
`magiclantern.bin` with `.incbin`, the assembler include path must point at the
selected build directory:

```sh
cd platform/5D3.123
ARM_BINPATH=/path/to/arm-none-eabi/bin \
make -j8 BUILD_DIR=build-zh ZIP_DIR=build-zh/zip \
     INCLUDE_ARGS='-I. -Iinclude -Ibuild-zh -I../../src -Wa,-Ibuild-zh'
```

The resulting `build-zh/magiclantern.zip` contains `autoexec.bin`, the ML tree,
`ML/LANG/INDEX.TXT`, `ML/LANG/zh_cn.lng`, `ML/FONTS/zh_cn.bfn` and the font
licenses.

## Regenerating the catalog / font

```sh
python3 tools/localization/catalog.py data/localization/zh_cn.json --output data/lang/zh_cn.lng
python3 tools/localization/extend_chinese_font.py
```

`extend_chinese_font.py` extends the preserved base BFNT with glyphs from
`data/fonts/source/NotoSansCJKsc-Regular.otf`; the OFL license texts are in
`doc/`.

## Provenance and scope

- Upstream design: ryulin456/magiclantern-zh r4 (`review/localization-v2`,
  GPL-2.0), itself built on Magic Lantern (GPL-2.0).
- German and Polish catalogs, the shared Latin extension font and their tests
  were removed for this branch; the loader/compiler remain language-neutral.
- The maintainer's real-camera test claim applies to the upstream r4 package,
  not to this rebased branch; verify on hardware before relying on it.

## QEMU menu capture

QEMU's 5D3 display model scans the active BMP buffer.  ML draws its menu into
the idle buffer and Canon clears the active one shortly afterwards, so a plain
screendump is blank.  Use the `ml-menu-screendump` branch of `qemu-eos`
commit `cfdfd0f548`: when the active 8-bit BMP frame is blank it scans the
alternate buffer (`^ 0x80000`), which lets screendump show the Chinese ML menu.
Canon GUI frames are unchanged; 100D/1100D use a different idle address and are
excluded.
