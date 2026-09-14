# Current expansion status

**59 refined assets integrated locally.** Batch21 is delivered. Curated queue:64 assets,5 pending (3 adjacent candidates and2 evidence-deferred objects). Defaultviewer6,487 building-related IDs, not a physical-building census. Stopped at the user’s request. All three agents stopped; batch22 retained as an unaccepted three-asset draft. Resume only on a new user instruction.

- [Latest delivered batch21](../batch21/docs/STATUS.md)
- [Batch20](../batch20/docs/STATUS.md)
- [Batch19](../batch19/docs/STATUS.md)
- [Batch18](../batch18/docs/STATUS.md)
- [Batch17](../batch17/docs/STATUS.md)
- [Batch16](../batch16/docs/STATUS.md)
- [Batch15](../batch15/docs/STATUS.md)
- [Batch13](../batch13/docs/STATUS.md)
- [27 Princes Gate correction, no count increment](../revision27/docs/STATUS.md)
- [Batch14](../batch14/docs/STATUS.md)
- [Batch 12](../batch12/docs/STATUS.md)
- [Batch 11](../batch11/docs/STATUS.md)
- [Batch 10](../batch10/docs/STATUS.md)
- [Batch 09](../batch09/docs/STATUS.md)
- [Batch 08](../batch08/docs/STATUS.md)
- [Batch 07](../batch07/docs/STATUS.md)
- [Batch 06](../batch06/docs/STATUS.md)
- [Batch 05](../batch05/docs/STATUS.md)
- [Batch 04](../batch04/docs/STATUS.md)
- [Source attribution index](ATTRIBUTION.md)
- [Machine progress](../progress.json) and [continuation queue](../continuation_queue.json)

Refresh http://localhost:8787/viewer/3d/ and use **Building refinements** to compare. Unknown facade/roof dimensions remain labelled artistic estimates. Original assets remain available. Native renders, GLB and Three.js checks passed per delivered batch; no live browser/full-city visual signoff or updated physics is claimed.

---

Historical pilot record follows; its counts and next steps describe the original pilot only.

# Expansion pilot — 23 Kensington Gore

**Update 2026-09-13:** three additional buildings are complete and integrated locally. The comparison control is now **Building refinements · 4**, covering the pilot plus 25 Kensington Gore, 41–45 Jay Mews and 29 Exhibition Road. See [batch 02 status and renders](../batch02/docs/STATUS.md). The remainder of this document records the original pilot run.

One building authored and integrated into the local viewer as an **artistic refinement**, following the user's permission to search online and imagine missing details. The existing source GLB is preserved. This is not a completed expansion of the whole surrounding area or a source-matched precise reconstruction.

The agent ran eight searches and inspected two openly licensed neighbourhood photographs. Neither photograph was confirmed to depict 23 Kensington Gore. The complete OSM plan and four-level tag are retained; facade composition, floor pitch, roof details and unseen elevations are estimates/artistic completion. The original model supplies material colours and entry alignment. See `KENSINGTON_GORE_23.md` and `../references/kensington_gore_23/sources.json`.

Google Maps was considered for location/discovery only. A direct map lookup could not be opened by the web tool; no Google imagery, screenshots or 3D tiles were used to derive or texture the model. Current consumer terms were viewed at https://www.google.com/help/terms_maps/ on 2026-09-12. Internet references and their individual source records were used instead.

## Artifacts

- `../output/kensington_gore_23_v1/master.blend`: editable replacement and 28-building neighbourhood review context. Context preserves scalar PBR colours but omits source texture maps; an estimated flat support plane and review lighting are explicitly labelled.
- `../output/kensington_gore_23_v1/replacement.glb`: uncompressed 816,988-byte replacement, 19 mesh objects and 14,887 triangles; no neighbours or review ground exported.
- `../modules/kensington_gore_23.py`: per-building source module.
- `../output/kensington_gore_23_v1/{front,entrance,roof,rear,context}.png`: actual Blender renders from the reopened native file.
- `../output/kensington_gore_23_v1/verification.json`, `interface_check.json` and `../reports/viewer_check.json`: export, geometry/interface and Three.js integration checks.

## Verification and limitations

Independent GLB import retains every semantic object, triangle count and material assignment, with zero observed bounds discrepancy. No degenerate triangles detected. Roof triangulation matches the complete mapped concave footprint within 0.001 m². Twenty-five entry rays including near-threshold heights found no obstruction before the intentionally closed door assembly. Existing entry support remains in place; its surface is 6 mm below the threshold. Checked entry span is 1 m; nominal leaf width 1.05 m, actual jamb clearance 1.02 m (the module's nominal interface width is not an accessibility certification).

Current isolated front, entry, roof and rear images plus the existing neighbourhood context were inspected. Open coping corners found during review were replaced with continuous mitred bands. Native file reopening and independent export reimport pass. This visual review validates a coherent artistic preview, not correspondence with the unseen real building.

Three.js decoded the actual source GLB and verified exact exterior-root identification, replacement bounds, retained entry support, no triangle loss through batching and reversible comparison. The native browser tool stalled for almost an hour; no live browser visual signoff or full-city rendered signoff is claimed. Full delivery flags remain false for that reason. Existing physics fields have not been recomputed; remote deployment was not performed.

## Viewing and resuming

Refresh the local viewer. **23 Kensington Gore · imagined detail** toggles the replacement and original exterior; the replacement is on by default. `?expansion=0` starts with the original. A close camera is `?cam=560,30,-145,512,7,-105&replay=0`. A missing/invalid replacement leaves the original available.

Reproduce: run `node --experimental-loader ./geometry/completion/scripts/three-loader.mjs geometry/expansion/scripts/extract_context.mjs`; then Blender `--background --factory-startup --disable-autoexec --python-exit-code 1 --python geometry/expansion/scripts/build_review.py`; then the same Blender command with `geometry/expansion/scripts/check_interfaces.py`; finally run the Node extraction command with `--verify-expansion`. Use a new version directory and update the viewer URL for future geometry revisions to avoid cached GLBs.

First pilot: 1/1 selected building modelled, 0/1 facade-verified against same-building photographs. Further outward batches have not started.
