"""Roommates Bake Less - build script.

Discover University roommates with the Baking interest bake cake after cake.
They still like baking after this; they just stop doing it all the time.

Why they bake so much
---------------------
`trait_RoommateNPC_Interest_Baking` gives `buff_RoommateNPC_Interests_Baking`,
which does two things:

1. It adds `commodity_RoommateNPC_Autonomy_Baking`, an urge that
   `fridge_BakeCake_Autonomously` advertises to satisfy. The urge starts at a
   random 60-240 every time the buff is applied (the commodity is not
   persisted, so that means every lot load), decays 1 per Sim minute, and
   starts pulling once it is below 60. Baking resets it to its max of 600. So: a
   cake within 1-4 hours of every load, then another about every 9-10 hours.
2. It multiplies the autonomy score of `commodity_Motive_MakeOneDessert` by
   10, on top of that.

What this changes
-----------------
- Urge max 600 -> 1800: about 29 hours between cakes instead of 9.
- Starting urge 60-240 -> 600-1800: loading the lot no longer queues up a cake.
- Dessert score multiplier 10 -> 2: they still lean towards desserts, just not
  ten times over.

Two small tuning overrides. No script, so nothing runs during play. The XML is
read from the installed game at build time and edited, so a rebuild after a
patch picks up whatever EA changed.

Author: GhostWorldTourist
"""
import os, sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.environ['LOCALAPPDATA'], 'sulskill', 'ts4-knowledge', 'lib'))
sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'repos', 'sulskill', 'sulskill-modbuild', 'scripts'))
import mergedtuning, dbpf

SOURCE = r'C:\Games\The Sims 4\Delta\EP08\SimulationDeltaBuild0.package'
T_BUFF, T_STATISTIC = 0x6017E896, 0x339BC5BD
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'GhostWorldTourist_RoommatesBakeLess.package')

URGE, BUFF = 211771, 211755
MAKE_ONE_DESSERT = '34124'

URGE_MAX = 1800
URGE_START = (600, 1800)
DESSERT_MULTIPLIER = 2


def one(elem, path, expect):
    node = elem.find(path)
    if node is None or node.text != expect:
        raise SystemExit('%s: %s is %r, expected %r - EA changed it, review '
                         'before rebuilding' % (elem.get('n'), path,
                                                None if node is None else node.text, expect))
    return node


def edit_urge(e):
    one(e, "T[@n='max_value_tuning']", '600').text = str(URGE_MAX)
    rng = "U[@n='initial_tuning']/V[@n='_value_range']/U[@n='enabled']/"
    one(e, rng + "T[@n='lower_bound']", '60').text = str(URGE_START[0])
    one(e, rng + "T[@n='upper_bound']", '240').text = str(URGE_START[1])


def edit_buff(e):
    mults = e.findall(".//U[@n='autonomy_modifier']/L[@n='score_multipliers']/U")
    hits = [u for u in mults if u.findtext("T[@n='key']") == MAKE_ONE_DESSERT]
    if len(hits) != 1:
        raise SystemExit('%s: expected one MakeOneDessert multiplier, found %d'
                         % (e.get('n'), len(hits)))
    one(hits[0], "T[@n='value']", '10').text = str(DESSERT_MULTIPLIER)


TARGETS = {
    URGE: (T_STATISTIC, 'commodity_RoommateNPC_Autonomy_Baking', edit_urge),
    BUFF: (T_BUFF, 'buff_RoommateNPC_Interests_Baking', edit_buff),
}


def main():
    found = {}
    for _, _, ct in mergedtuning.iter_resources(SOURCE):
        for inst in ct.instances():
            iid = int(inst.attrs.get('s', 0))
            if iid in TARGETS and inst.attrs.get('n') == TARGETS[iid][1]:
                found[iid] = ct.expand(inst)
    missing = set(TARGETS) - set(found)
    if missing:
        print('NOT FOUND: %s' % sorted(missing), file=sys.stderr)
        return 2
    resources = []
    for iid, (rtype, name, edit) in sorted(TARGETS.items()):
        edit(found[iid])
        xml = b'<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(found[iid], encoding='utf-8')
        resources.append((rtype, 0, iid, xml))
        print('  %s' % name)
    n, size = dbpf.write(OUT, resources)
    print('\nwrote %s\n  %d resources, %d bytes' % (OUT, n, size))
    return 0


if __name__ == '__main__':
    sys.exit(main())
