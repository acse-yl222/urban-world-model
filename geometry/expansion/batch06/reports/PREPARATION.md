# Batch 06 preparation

Three selected full footprints only. No source asset or earlier batch input changed. No completion state is advanced.

## Source semantics

- `way-1154608372`: OSM `building=yes`, one level; source has only masonry/roof, no windows, door or support. Complete five-point footprint, eaves 3.699724 m. `entry=null`.
- `way-788306098`: OSM `building=service`, one level; source has only masonry/roof, no windows, door or support. Complete four-point footprint, eaves 3.699384 m. `entry=null`.
- `way-640976478`: OSM university, no level tag; full four-point footprint, inherited eaves 16.299368 m. Five floors are an inference from the original procedural 3.15 m pitch + .55 m allowance, not an observation or source-reported tag. Existing west entry edge 1 is projected to wall plane; original recessed leaf location preserved separately.

A small service asset cannot be turned into a multi-storey facade based on missing information. Any new door on either currently doorless asset requires a separately labelled artistic decision and explicit ground support; preparation does not invent one.

## GIS overlap requiring review

The five-point outbuilding overlaps Huxley `relation-37787` by 0.055710 m² (0.233% of its mapped area). This is an unresolved narrow mapped sliver, with no parent relation membership or asset part alias. Full footprints retained. `huxley_overlap.json` contains exact intersection polygon and review instructions. Do not report zero overlap or silently trim the geometry.

Other two footprints have no positive-area overlap. All target polygons valid CCW, no holes; no parent relation memberships or source-part aliases.

## Shared wall and context

University east edge 3 shares approx. 30.56 m with Amaryllis Fleming Concert Hall `way-479275674`. Current available common wall interval is z `[0.05045760072619743,16.349041389633907]`; this is an original source-model estimate. Preserve the wall and default common-height apertures opaque unless observed otherwise. Source whole-geometry bounds are also recorded separately in each neighbour audit.

Initial reused context was rejected because William Penney Laboratory and two RCM structures were missing. Node decoded a new bounded context covering all 12 required buildings, 164 meshes. There are no batch02/03 replacement assets in this local neighbourhood; all relevant current geometry is the inherited source, which is accurate provenance rather than an unjustified reuse claim. Batch04/05 are not counted delivered or complete. Source materials retained as scalar PBR diagnostic values; imagery textures omitted only in context.

Reusable preparation script now handles no-door assets and infers missing level counts from retained baseline height instead of assuming four storeys. Features, manifest and reports are ready; the Huxley sliver remains an integration review item.
