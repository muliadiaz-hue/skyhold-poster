# SKYHOLD — a travel poster for a place that isn't there

Entry for the make.fun bounty
[the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539).

SKYHOLD is a city built on a ring-shaped cliff above a sea of clouds.
Its rivers pour off the rim as waterfalls that fall into the sky, and
the whole town turns gold at sunset. It does not exist. The poster
wishes it did.

## How the entry works

- `asset.jpg` — the finished poster: 1024×1024 JPEG, 352,671 bytes.
- `main.py` — a standard-library Python 3 program. It validates the
  asset against the bounty gate (whole JPEG, at most 1,048,576 bytes,
  at most 1024×1024), clears stale files from the output directory
  (never the directory itself), and writes the poster to
  `entry.png` in `$MAKEFUN_OUTPUT_DIR` (falling back to `/output`,
  then `./output`). Every run writes exactly the same bytes.

## License

MIT — see `LICENSE`.
