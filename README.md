# Roommates Bake Less

Discover University roommates with the Baking interest still like to bake.
They just don't make cake after cake anymore.

## Why they bake so much

The Baking interest gives them an urge to bake that is satisfied by baking a
cake from the fridge:

- It restarts at 1-4 hours from triggering **every time the lot loads**.
- After each cake it comes back in about 9-10 hours.
- On top of that, the interest multiplies how much they want to make desserts by **10**.

## What this changes

| | vanilla | this mod |
|---|---:|---:|
| time between cakes | ~9 h | ~29 h |
| urge on lot load | due in 1-4 h | due in 9-29 h |
| dessert preference | ×10 | ×2 |

The values are constants at the top of `build.py` if you want them tuned
differently.

- Tuning only, no script. Nothing runs during play.
- Two small overrides: `commodity_RoommateNPC_Autonomy_Baking` and
  `buff_RoommateNPC_Interests_Baking`.
- Requires Discover University.

## Build

```
py build.py
```

Reads EA's tuning from the installed game, edits it, and writes
`GhostWorldTourist_RoommatesBakeLess.package`. If a patch changes the values it
edits, the build stops and says so instead of overwriting EA's change.

Author: GhostWorldTourist
