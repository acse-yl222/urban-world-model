# 41–45 Jay Mews — batch 02 authored module

Stage: module built and Python syntax checked. Coordinator must run Blender assembly, numeric checks, export/reimport and visual QA before delivery.

Mapped way-117010286: retain all 8 ring vertices (335.141154 m²), two levels, existing estimated wall height 6.8507755567 m, local base 0.049463634 m. No global objects deleted. All wall segments, including unverified shared boundaries, remain present. Roof membrane follows inset mapped polygon with concavity preserved and continuous mitred coping.

The module creates a distinct low mews composition: wider ground studio windows, narrow upper windows, inset glazing, true masonry apertures, projecting sills, simple lintels/eaves, rainwater downpipes and low parapet. No ornamental Victorian balconies or copied Kensington Gore facade. All openings, roof style and architectural dimensions are explicitly artistic completion, not measured. No invented plant or basement.

## Evidence

Actually inspected `references/jay_mews_41_45/street.jpg`: [Jay Mews, SW7, Robin Webster, 22 April 2018](https://www.geograph.org.uk/photo/5752102), [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/). Two-storey pale/brick mews, upper small windows and ground wide garage/workshop openings provide neighbourhood context only. Exact 41–45 is not positively identified. Contribution is artistically interpreted; attribution and share-alike should accompany adapted geometry. No image texture used.

Also inspected `frayling.jpg`, [Shadowssettle 2020](https://commons.wikimedia.org/wiki/File:Frayling_Building,_Royal_College_of_Art,_Jay_Mews.jpg), CC BY-SA 4.0: a separate four-storey institutional building. Excluded from modelling.

[RCM official Jay Mews map](https://www.rcm.ac.uk/media/RCM%20Jay%20Mews%20map.pdf) lists 41–43 with offices on Ground and 1. The inherited OSM Royal College of Art operator is therefore potentially stale or conflates addresses; no institution signage is created. OSM mapping retained with © OpenStreetMap contributors / ODbL attribution.

Sources and observations saved beside images with hashes, dates and rights review. Google imagery not acquired or used. Two search queries, two stored and actually inspected photos.

## Entry and material handoff

Entry uses nearest mapped edge 1, projects the existing XY [546.608103270071,25.125275576742] to that wall. Outward normal [-0.9902440793,-0.1393436881,0], threshold z 0.049463634, clear width 1.0487730234 m; door leaf 0.30 m recessed. Threshold extends -0.006 m below local base, matching existing support z 0.044 within 0.54 mm. No new external ramp or steps. Returned interfaces contain actual authored threshold, normal, clear width and leaf centre.

Recommend masonry as pale warm painted brick, base RGBA [0.68,0.65,0.55,1], roughness .88; trim [0.85,0.84,0.78,1], roughness .75. Coordinator-owned `materials` retained without mutation. Blue-grey glass and dark painted door/metal are appropriate.

## Limits

Bay numbers and spacing, back windows, flat membrane roof/parapet and drain placement unconfirmed. Entry inherited from previous estimated asset. Shared walls are not deleted pending actual adjacency evidence. This is richer authored geometry with explicit uncertainty, not survey-accurate reconstruction.


Coordinator update 2026-09-13: integrated locally; native reopening, independent GLB import, material/entry/roof checks and current rendered views passed. See STATUS.md for final scope and limitations.
