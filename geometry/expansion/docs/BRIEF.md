# Imperial outward geometry expansion

Requested 2026-09-12: use the local region-to-geometry skill and an agent to extend the more detailed Imperial geometry into neighbouring areas.

## Initial scope

Audit the authored geometry boundary, then rank complete neighbouring buildings within an initial 150 m search distance. This distance is a working search scope, not a claim about the existing precision boundary. First modelling batch: one adjacent building with usable evidence. Further rings follow reviewed batches; this is not an indefinite background job.

The existing viewer CAMPUS rectangle is a camera target, not verified quality coverage. Preserve distinctions between authored detail, mapped footprints, source-reported dimensions, visually estimated dimensions, and unverified completion.

## Integration contract

- Preserve `south_kensington_core008_web.glb` and existing working assets.
- Use model coordinates matching EPSG:32630 minus [695238.304719173,5709236.965026026], as established by the supplement registration. Blender uses X east/Y north/Z up; glTF uses X east/Y up/Z south. Independently verify candidate alignment before integration.
- A replacement building must identify all original nodes it replaces by source ID; adding an overlapping detailed shell is not a valid integration.
- Match the existing campus material palette and ground levels. Preserve holes and full intersecting buildings; document shared walls and entrances.
- Keep source modules, source/uncertainty records, versioned uncompressed `.blend`/`.glb`, numerical reports and reviewed renders.
- Existing physics fields describe the original geometry and are not recomputed by this modelling batch.

## Evidence and acceptance

Use inspected sources with permissions for geometry derivation. Footprint extrusion and guessed repeated windows are baselines, not completed precise reconstruction. A source-poor candidate remains pending evidence rather than receiving an invented accurate facade.

User clarification: the original source project is unavailable. The user authorizes automatic Internet reference discovery and imaginative completion. Source-poor buildings may therefore advance as explicitly labelled artistic refinements using the current GLB as the baseline; they must not be presented as geographically verified facade reconstruction. The first pilot now follows this clarified scope.

Check overview, facade, entrance, roof and rear; verify source identities, bounds, materials, neighbouring interfaces, native-file reopening and independent GLB reimport. Only integrate a reviewed result into the default viewer.

## Ownership

Coordinator: scope, coordinate frame, shared interfaces, assembly and acceptance.
`expansion_audit` agent: read-only source/model discovery; writes `docs/AUDIT.md` and `candidate.json` only. After the audit, a bounded per-building assignment may reuse this agent with an explicit module contract.
