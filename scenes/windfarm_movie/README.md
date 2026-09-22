# Windfarm display data

Completed 2 m independent MAC experiment: 12,206 adaptive steps, 300 simulated
seconds, 151 saved frames. This is not an equivalent implementation of AI4Urban.
The display samples axial velocity at 8 m spacing on the terrain + 80 m surface;
frames are interpolated for playback. Binary chunks are little-endian float16,
shape [time,256,512], in consecutive 40-frame chunks. Terrain is float32 [256,512].
The GLB uses local elevation, original elevation minus 480 m.

Rotor motion is display-only. Each rotor uses its time-varying actuator-disk mean
velocity from rotor-speeds.json and assumed tip-speed ratio 7: omega=7 U/R.
The display integrates angular phase at 1/12.5 of simulated time for readable
motion during 12.5x playback. Native CAD rotor planes are preserved; the simulation
assumes all actuator disks face +x, so visual yaw is not a resolved solver input.
No blade-resolved dynamics, generator/controller model, cut-in or rated-speed
control, rotation-induced torque, or power prediction is claimed.

All 23 assemblies contain three blades plus hub/spinner. Other geometry stays
fixed. The checkbox disables the visual rotation. The linked MP4 is the earlier
static-blade export; live interaction includes the new rotor animation.
