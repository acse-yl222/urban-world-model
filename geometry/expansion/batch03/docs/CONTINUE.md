# Continuing the frontier

Read `geometry/expansion/progress.json`, `remaining_frontier.json`, and `continuation_queue.json` before starting. Refresh the queue from the delivered IDs using:

```sh
python3 geometry/expansion/scripts/plan_next_expansion.py
```

The planner ranks candidates using full polygon boundary distance; it does not search, model, spend money, launch background agents, or mark work as completed. Work continues in bounded agent-operated batches during an active session. No unattended service or schedule has been installed.

Select at most three new building IDs per batch, inspect the source asset identity and evidence, establish shared-wall and entrance contracts, then assign one building per agent. Keep CRS/origin fixed and retain full source polygons. Use a new batch/run directory and retain old artifacts.

Batch03 provides assembly, native reload, independent GLB import, door/roof/shared-wall checks and all-side render examples. Adapt their paths, IDs and previous context assets to the next manifest; do not reuse hardcoded building assumptions blindly. A previous report must never certify newer artifacts. Only update completed IDs after the local integration, numerical checks and actual visual review pass.

Revisions must replace the previous overlay for that ID as well as the original city exterior. Batch03 extracts the two unchanged batch02 buildings into retained_batch02.glb and replaces 29 in its four-building export, avoiding duplicate overlays. Record source hashes and verify the viewer's ID set, visibility toggle, triangle preservation and preserved entrance supports.

References may narrow or correct earlier building assignments. Keep source-reported, visually inferred, and artistically completed parts distinct. Roof-only and service features in the queue are review candidates, not automatically buildings needing full facade reconstruction.
