# Handoff: Castlevania: Curse of Darkness (SLUS-21168) PS2 static recomp — "Noble Archimedes"

## In progress: 2026-09-30 — 59–60 guest update/s performance target

Publication checkpoint (2026-10-01 18:02 UTC): user authorized installing the
tested executable and committing/pushing the fixes. Root `NobleArchimedes.exe`
now equals candidate `9bf3b02bc15d69743947f957876360872fc6f96a9304c6a1ebd4e28b9363e930`.
Previous installed EXE is preserved as
`output/perf60_before_scheduler_state/NobleArchimedes.exe`, hash
`b6f4fcf716180eb2ff714e49b62f0b6338fadf5ab0b7f602361049d4dae57800`.
The installed file passed a fresh 35-second hidden launch smoke probe.
Fresh publication checks: Python host/build/RAM-reader 18/18, optimizer 2/2;
CPU PS2 353/356 with the same three IOP/RPC assertions. Logs under
`output/perf60_publish_ps2_validation.log` and `output/perf60_installed_smoke`.
Actual menu target remains OPEN (main 54.808, cursor name 41.084 updates/s);
audio and cutscene rendering remain unresolved. The earlier checkpoints' claims
that the installed EXE is untouched are historical.

Runtime fixes are published through this repository's existing source-patch
mechanism, preserving the upstream gitlink `75d729ce40d7eed9649fd4bb05628dee520f3d0c`.
The refreshed full-context `patches/ps2recomp-progress.patch` includes authored
runtime source/tests, PGS fetch/CMake integration, retained pinned dependency
patch and license notices. Vendor checkouts, graphify/Python caches, game-derived
generated sources, captures and all compiled binaries remain local. This avoids
creating a new fork or requiring write access to the upstream repository.
The exported patch contains 121 audited source paths (933,551 bytes). Applying
it to a private clean-base index reproduces source tree
`3cf599b2769162c174a72f553dd86946f594d53e`; the real nested index remains untouched.
Independent path audit found no binary, downloaded vendor, cache, captured or
generated game material. The relocated synthetic render-completion fixture
passed all five cases with diagnostics off/on (10 modes), exact guest-state
hashes and cycle counts. CodeGenerator publication suite passed 61/61.
Publication packaging also adds a generic decoder/generator for the two missed
guest entry adapters. It derives operands from local ignored instruction
records, and unity generation refreshes the ignored compatibility header.
Fresh output matches the original header byte-for-byte (SHA256
`e52a74f19bc9d605cf519b1210988cbcd8cc45216c21add1841db02b3ada03b2`);
the existing header timestamp and all executable bytes remain unchanged.
Host/build/generation/RAM-reader Python suite now passes 28/28; optimizer 2/2.
This resolves publishing the manually translated leaves while retaining exact
candidate behavior. Only generic generator logic and synthetic tests are tracked.

Latest checkpoint (2026-10-01 17:48 UTC; supersedes the historical checkpoints below):

- Target remains OPEN. Installed root EXE is unchanged, SHA256
  `b6f4fcf716180eb2ff714e49b62f0b6338fadf5ab0b7f602361049d4dae57800`.
- Latest candidate is `output/perf60_scheduler_state/NobleArchimedes.exe`, SHA256
  `9bf3b02bc15d69743947f957876360872fc6f96a9304c6a1ebd4e28b9363e930`.
  It includes the validated MinGW VU rounding setter, bounded poll folds,
  completion diagnostics (off by default), and restored scheduler execution/
  interrupt state before guest execution. Builds and game link succeeded.
- Fresh CPU PS2 suite: **353/356 passed**. Repaired 96-callback fixture,
  positive-owner IRQ regular StartThread ordering, and priority/FIFO tests pass.
  Remaining three failures are identical to earlier baseline assertions:
  SifInitRpc IOP-cycle initialization, emulated RPC bind, and hybrid RPC bind.
  Log: `output/perf60_scheduler_state_ps2_validation.log`.
- Headless ordinary-input New Game progression passed (both exit codes 0):
  main menu -> name -> no-memory-card confirmation -> loading -> movie at
  81.9 s -> post-movie state at 158.0 s. Log/manifest under
  `output/perf60_scheduler_state_progress`. This overlapped test linking and
  is progression evidence only, NOT a performance measurement.
- Latest clean measured fenv candidate: main **55.390 actual updates/s**;
  cursor name entry **22.993 actual updates/s**, game VBlank **54.871/s**.
  Matched pre-fenv cursor name control was **22.018 actual updates/s**.
  This single pair is a small gain, not achievement of the target.
- Latest sampled story video delivered **22.000 unique pictures/s** against
  native **30000/1001 (~29.97)**, with **47.276 display ticks/s**. PTS remains
  correct; late-caller rebases contribute additional delay. Audio and first
  cutscene rendering remain unresolved.
- Final scheduler-state candidate clean name/cursor and main probes completed
  serially under `output/perf60_scheduler_state_clean`, all four probe/driver
  exit codes 0, no overlapping builds/samplers, original power plan restored.
  Consistent driver-seconds 40–75 windows: name **41.084 actual updates/s**,
  **42.667 game VBlanks/s** (34.125 s window); main **54.808 actual updates/s**,
  **59.312 game VBlanks/s** (32.422 s window). Thus both remain below the actual
  59–60 update/s target. Earlier 23-update name rate was on the pre-restoration
  fenv candidate; restored interrupt state changes behavior, and run-to-run
  variability remains. Do not substitute display-clock FPS for actual updates.
  Read-only agents audit cycle lead and bounded VBlank anchoring; neither
  proposal is implemented. No jobs remain running after the clean probes.
- Independent pacing audit: preserve a processed Start's scheduled host anchor
  only when lateness is less than one existing 16.667 ms period; rebase after
  longer stalls. Before adopting, fix stale idle classification across Start
  wakeups and keep IOP-producing cycle accounting outside the event mutex.
  Required regressions include subperiod drift, period boundary, long-stall
  no-catch-up, Ready wake versus End advancement, already-due End ordering,
  Timer2/IOP event posting, and existing runnable/fold/pacing cases. This is
  a proposal only. Main clock headroom is about 1.1%, below its actual-update
  deficit; name CPU cost also exceeds the 60-update budget. CPU work reduction
  remains necessary, so an anchor change alone cannot fulfill the target.

Historical checkpoints follow; their running-job statements are stale.

Latest checkpoint (2026-10-01 17:15 UTC): the target remains OPEN. Root EXE
is still untouched. `output/perf60_render_wait/NobleArchimedes.exe` links,
hash `58b4cc26d2c84c29c27b358f9e8ae57e65c371a4fde92591af49449293521973`.
It includes frontend elision, restored original completion gate, and bounded
32-cycle polling folds. Gate dispatch 20/20 and wait batching 39/39 pass with
meaningful old-code failures. Rebuilt PS2 350/355 has the SAME five existing
failures; CodeGenerator 61/61 and Python 18/18 pass. Two read-only reviews found
no blocker in the bounded fold. Native VU specialization remains unadopted:
clean folded timings vary and one counterbalanced comparison regressed.

CURRENT status: latest functional candidate is `perf60_deferred_fold` (88c481c
hash below), with clean main58.670 actual updates/s and name26.179/s; display
clock near60 does not prove actual progress. Native ST00 video is29.97 unique
pictures/s but delivers19.279/s in the actual180s New Game probe. Audio and
first-cutscene rendering remain unresolved/deferred. Root EXE still unchanged.
Shared runtime build and new diagnostic game link succeeded at16:34 under
`output/perf60_completion_trace`, hash4c8d1842a941fd2ce326cc672ca8314da5ba28072d1b81fe329afb0e13b1d97f.
All5observercases xflagoff/on pass with exactguesthashes/cycles; independent
reviewclear. Sourcesfrozen, behavior-neutraldiagnostics. RIP80run failedphase
gate (never reachedname beforelimit); discard asnameprofile. RIP180longrun
valid20snamewindow with118889samples: VU24.45%all/33.7%native, scheduler7.55%all,
PGS2.78%,GSfrontend0.99%, DLLwallresidency27.45% (notCPUattribution).
`output/perf60_live_name_rip_long` hasfullnativehistogram/moduleRVAevidence.
CPUIDinsideMinGW__mingw_has_sse is5.74%all at exactpostCPUIDinstruction;
VUrunfesetroundenter/exitcall iteachshortinvocation. VUagentowns PRIVATEfenv
equivalenthelper/accuracy underoutput/perf60_vu_fenv; CPUreleased16:50:55for
accuracyonly. No productionVUedit, fusionadoptionornewbenchmarkyet.
Observer-onlyname80both0 (`perf60_completion_name`):33.765actual/gameAD3F80,
native416D58tracksupdates andnoextra416B58deadlinefailure. BothheavyRIPand
lighterobservereraseearlier26/54mismatch; do notinferinterval2/native30limit.
Actualstory180both0 (`perf60_completion_story`), movie90.4→172.3then3D:
gen2ST01frames300→1200 gives22.000pictures/s,47.276displayticks/s; exactPTS3003,
repeat0,interval2,queued3.134late-callerPTSbasefields=134extrafields. Movie
slowdownincludesdisplayclock47.28 pluscallerrebasing; noMPEGclockfixjustified.
BothassetsST00/ST01native29.97. Audio/renderingremainunfixed.
PGS7hostpreferfallbackwarningseachidentical64MiBrequest/76MiBusage/137MiBBAR
budget,max214MiB; nofailure/growingVRAMleakevidence. Scratchrolloverfallback
and4framecontextrecyclingareimplemented. Menuagentread-onlyauditsTLSowners.

NEW productionfenvpatch frozen inexistinglib/vu/ps2_vu1_core.cpp only: MinGW
GNUx64/GCC>=9/SSE2/!Clang noipa setter replaces exactlytwofesetroundcalls;
stdfegetround retained, same rounding/nonroundflags/callback restoration,
standardfallbackelsewhere. Private1280setter+144tail/callback byteparity,
both669callchainhashes/42,403cycles/667packets,128general/2304bounded/504guard
snapshotcorpora and51/51VU pass. Independentreviewclear; initialinlineversion
rejectedforFPordering, finalout-of-line/noipa avoidsLTOarithmeticmotion.
Sharedruntimebuild0; integratedcandidate `output/perf60_fenv/NobleArchimedes.exe`
linked126.5sec hashad9a7b5324d618437b0b00487a2813a4fca4aad44adc45c09a3c42ffdbc0be7a.
Disassembly confirmshelperdirectCW/MXCSR instructions withnoCPUID.
FreshcorrectCWD CPU PS2suite350/355same5baselinefailures, noVUfailures.
Cleanmatchedreference4c8d cursor-name80both0 (`perf60_fenv_control`):22.018actual
vs53.240gameVBlank over40–75driversecwindow. Candidatecursorname80thenmenu80
NOW RUNNING `output/perf60_fenv_candidate`, rootsession29582; exclusiveCPU,
noobservers/samplers. Do notclaimspeeduporinstall beforeactualresults.
RootEXEstillunchanged, verifiedSHA
b6f4fcf716180eb2ff714e49b62f0b6338fadf5ab0b7f602361049d4dae57800.
Newexplorer /root/scheduler_failures read-only audits twoexisting scheduler
failures (callbackreusable stack andabsolutepriorityFIFO) foractualgameimpact;
noedits/builds/tests duringFPSprobes. Audio/renderingstillunfixed.

Ordinary-input clean Power saver probes (`perf60_render_wait_default`) reach
steady main-menu 59.78–59.8 VBlanks/s, but actual phase increments are lower
(about52/s in a late window). Name entry is still variable21–41 VBlanks/s;
Balanced name (`perf60_render_wait_balanced_name`) also falls below target.
The earlier no-clear-only Balanced build (`perf60_restore_gate_name_rate`)
reports54.6–56.3 VBlanks/s, but its phase increments are only~24/s, so that is
NOT evidence of54–56 actual name updates/s. Detailed new-candidate name trace
(`perf60_render_wait_name_profile`) shows40–45 VBlanks/s, VIF2.7s/5s, GPU raw
GIF~0.28s/2s, GPU scanout~0.55s/2s and several million checkpoints/5s. Detailed
profiling changes timing and is diagnostic evidence, not the final FPS run.

Do NOT infer a native30fps menu limit from A3DD31/A3DD32 alone: mode2 uses
lastSwap+interval, but A3DD71==0 overrides effective mode0; FP/A3DD18 can force
mode1. Mode4 uses lastSwap+1. Current observations include A3DD70=0x101 and
A3DD18=0. Probe now reads these too. MPEG's native29.97 unique picture rate
remains separately established. Both phase updates and VBlank must be tracked.

Next work: menu agent owns EeScheduler.cpp plus a no-extra-cycle host pacing
fixture. At top-level exact417270 spin, reject ALL other Ready threads/events/
callbacks/timer IRQs/native scopes; when only a cycle-due, host-future deadline
remains, wait on the event CV to the existing deadline and charge ZERO extra
cycles. Existing waitForEvent must not be reused because it charges wall time.
The isolated `perf60_full_frontend` control linked successfully after replacing
only gs_frontend.cpp.obj with the old full parser. Its clean Balanced name probe
reaches 50.6–53.1 VBlanks/s, but only 21.66 actual phase increments/s in the late
window. Thus its higher VBlank clock does not establish a graphics speedup;
the current frontend shortcut remains enabled. Use gcc-ar x for binary extraction
on Windows: capturing gcc-ar p stdout corrupted the object through text mode.

Integrated host pacing candidate `output/perf60_paced/NobleArchimedes.exe`
linked successfully, hash82f2e7ce67cf1b17e635863fbb041f09217fec219dce09137c36695487d9501e.
All11 pacing and39 folding cases pass. Saved old Stop and unguarded timer/alarm
controls fail as intended; independent VU review found no remaining blocker.
The new guards veto finite EE timer IRQs and future-cycle events with a host
deadline <= the selected due event. Root build/link both succeeded.

Clean ordinary-input Power saver probes `perf60_paced_default` exit0/0 twice.
Uniform driver-seconds40–75 windows: main55.516 actual updates/59.174 game VBlank
per second; name36.174 actual/gameVBlank, but last rate windows vary15.08–42.55.
Previous bounded-fold default on the same analysis window: main54.618/59.264,
name28.435/28.435. These are single variable comparisons, NOT target completion.
Use private `output/analyze_perf60.py` for consistent windows. Native menu
interval is1: A3DD30=0x01020100 => parity0, interval1, mode2, enabled1.
Only4172D8 caller4158E0 sets1; apparent2 is MODE via417310. Mode2 permits one
update per VBlank. Read-only traces show overdue completion gates in slow runs,
and no mandatory two-VBlank delay in416B58 or its worker/DMA retry paths.

Clean actualNewGame `perf60_paced_story`180sec exits0/0. State4,10,7,1 movie
fromt74.8 to167.8, then4,10,3,1. Movieclock mostly49–50, briefly57.6, below
target; post-movie3D4.2–4.4. MPEGgen2 at least1200 deliveredframes, but playback
wall-rate cannot be precisely inferred from untimestamped logs. No movie60 or
3D60 claim. All original/test/restored power plans are Power saver.

Detailed `perf60_paced_name_profile` completed: VIF~2.7s/5s, GIF~1.17s nested
inside VIF, no host pacing waits. VU core private replay~4.5–5.4ms per669call
chain excludes code/data/state restore and oracle checks; it includes packet-copy
callback, but no live GS cost. Do not call inclusive VIF pureVU or sum scopes.

Integrated diagnostic candidate `output/perf60_diagnostic/NobleArchimedes.exe`
built successfully from opt-in scheduler guard reports plus MPEG timestamp fields.
Both changes are behavior-neutral with diagnostics off. All11+39 cases pass
with diagnostics off AND on. Full runtime rebuilt: proper PS2 CPU suite350/355
with same five existing failures (`perf60_diagnostic_ps2_validation_cpu.log`).
The first root unfiltered/defaultGPU/wrong-cwd run produced452/422/30; that is
configuration-invalid for comparison, not30 new runtime regressions. Use
MINITEST_SUITE=PS2, PS2_GS_BACKEND=cpu, PS2_GS_THREADS=0 and PS2Recomp cwd.

`perf60_wait_reasons`80sec completed. Timer2 MODE0x382/COMPARE0; futureTimer
rejects99.99% of3.125M exact poll attempts, zero parks. At least99.62% passed
every other reported guard; those episodes had cycle-due/host-future VBlank.
The finite timer guard remains necessary (real regression catches delay).
Root approved menu-agent charged-fold extension for this special state: keep
checkpointPending, prove every cycle-due event is host-future under event mutex,
reject queued producers/callbacks/IRQs/native/Ready/etc; cap by timer/slice/IOP
and next still-future virtual event. Agent owns EeScheduler.cpp and batching
fixture. Final old control fails32expected1952; final candidate passes74cases
with diagnostics0 and1 (148total): original39fold+11pacing,18direct and6actual
dispatcher cases. Actual Timer2 cause11 callback at512cycles, queued callbacks,
mixed same-cycle host deadlines and hidden future Alarm160 caps pass. Movie
independent exact source audit clear. Post-proof host crossing is bounded to one
charged batch by unchanged flags/dispatcher, not an injected-delay measurement.
Shared runtime rebuilt successfully and integrated game linked114.9sec:
`output/perf60_deferred_fold/NobleArchimedes.exe`. Host anchor proposal deferred.

VU agent owns PRIVATE `output/perf60_vu_copy/` five-pair copy-loop fusion
experiment (27.5% issued pairs). First1338call private-metadata name audits pass
twice. Independent review found codeSize==1a8 finalPC wrap bug, now rejected
with <=1a8 guard; code/data alias and canonical decoded-cache guards also added.
Final tightened candidate compiles, but final full-counter/write-sequence-wrap
and other added accuracy cases remain UNVALIDATED. No VU timing/adoption yet.

Root clean serial run DONE: `perf60_deferred_fold_default` session40692exit0,
name80sec then menu80sec, bothprobe/driver0, allplansPower saver. Candidate hash
88c481cbae96c95e89508642ba5c2edc9ccacaeb97859a337dc4c19c38e20543.
Uniform40–75 windows: name26.179 actualphase/54.048 gameVBlank persecond;
main58.670/59.611. Thus fasterclock is NOT name-entry improvement; actualname
regressed vs priorpaced-only36.174 average (runsvariable). No mainEXEinstall.
Next menuagent owns source-only opt-in completion/callback latency diagnostics
inEeScheduler; movieagent read-only identifies accurate nested416B58 hook and
queue/dependency RAMfields. Their work must distinguish cmd4VIF/DMAwait from
latecallbackworker. No source/archive builds bytheseagents duringVUaccuracy.
Timestamped actual-story `perf60_deferred_fold_story`180sec completedexit0,
session63679closed. Samecandidate88hash, no concurrentCPUwork. Native asset
ST00_00.PSS: bundledffprobe confirms30000/1001, PTSstep3003, repeat0, progressive
at10/40/70s, duration85.852433s. Tracegen1frames300→1800 wall77.803s gives
19.279 unique pictures/s versus59.753 displayticks/s; frames300→1200 were
19.773/59.780. Queue3 at sampledframe deliveries excludes sampled starvation.
MPEG timing preserves PTS/fraction; rebases only when>=onepicturelate. Earlier
round-every-frame hypothesis was withdrawn. Needcallerlatency/missingPTS/rebase
trace before functionalfix. Root SOURCE-ONLY MPEG.cpp sampledtrace now adds
pts90k/repeat/interval/target_before/correction/firstPTS/PTSbase fields. Notbuilt.

Menu agent owns source-only EeScheduler sidecar and narrow ps2_runtime.cpp
dispatchGuestBranch observation hook underPS2_EE_RENDER_COMPLETION_DIAGNOSTICS.
Track request separately: existing8-cycle checkpoint can yield BEFOREtargetFn.
Trueexecutionseams include runtimetargetFn/nextFn and schedulerdirectresume.
Exactnested416B58 source41FD00/A1=1(worker),41FB88/A1=0(dependency). Returns
41FD08/41FB90 or gateclear provecompletion; bodyyieldalone doesnot. Queue10
headtype4 paired reciprocalcmd3 = unresolved Q1/Q2; headtype7/callback416B58
andtargetreached = readyguestcompletion. Callback424C60→41FDC8 source424C9C.
Do notsharedbuild until observercomplete/sourcefrozen, since prototypes may be
inflight. Privateaccuracybuilds areauthorized, no currentlyactive rootgame.

VU privatefusion FINALaccuracy passes226cases/1876snapshots, eachname1338call
metadata audit, loading88call,128/2304/504exactcorpora and51/51VU. Savedoracle
archivesused, productionuntouched. Exclusive19.5sec timingcompleted15:54:59:
stock AB sum1301.288ms, fused BA1010.237ms, fused AB1167.736ms, stock BA1170.530ms.
Aggregate11.9% butreversegain0.24% andindividualregression; UNADOPTED. VUagent
nowprepares PRIVATE gatedRIPsampler sourceonly underoutput/perf60_vu_copy/sampler,
Suspend→GetThreadContext→phase-marker-read→Resume beforeI/O; disjointCPUaffinity,
stop/join/handlecleanup, suspensionoverheadcount. NOsamplerbuild/profileyet.

Read-onlyEEpacingreview confirmsahead-of-wall problem: chargedpolling main
1.94–2.277Bcycles/5s vs300ticks*4.915M=1.474B, acceleratingtimer/IOP/alarms.
Gate-onlycapwouldneedstable reset(hostOrigin,cycleOrigin), ZEROcharge outerwait,
wallbudget yield incheckpointDue, and exactexistingboundaryguards. No suchorigin
currentlystored; max(now,scheduled)VBlankanchors cannot serveasglobalorigin.
Noarchitectureimplementation approvedyet; completion/readiness evidencefirst.
`tools/probe_menu_scenarios.py --cursor-test` now forwards existing driver flag;
name-only will Down/Up repeatedly, main-only alreadydoes. py_compile passed.
Root EXE unchanged; all current FPS gains remain unmeasured for new fold.

Earlier checkpoint (2026-10-01 02:44 UTC): `output/perf60_dual_equiv/NobleArchimedes.exe`
is the current successfully linked candidate, SHA256
`8119cd953c9f0d42555d2e802f3f41d5d894f28a92102b707a4452dbbac550f7`.
It includes 79CB28's original entry, decoded dual-display equivalence, and opt-in
kernel/MC diagnostics. GPU verification: 359 pixel/metadata cases, 13 selector
classifications, and 13 focused executions pass. Python 18/18 passes.
Clean automated Balanced probes (`perf60_balanced_scenarios`) show main-menu
steady windows 59.4–60 guest VBlanks/s, name entry 25.97–27.4. Power saver
main-menu mean was 57.82 (`perf60_main_power_compare`). Active-load WMI reports
3700MHz/82% performance on Power saver, so idle 2200MHz is not an active CPU cap.
The earlier manual power-plan change occurred after the probe ended and is not
valid comparison evidence. The automated wrapper restores the original Power
saver plan in finally; it has been restored and verified.

The original render gate at 9395B8 has a real completion path: builder 416D58
sets it and schedules queue-10 callback 416B58 behind GIF/VIF dependencies;
VBlank 424C60 increments AD3F80 and wakes the worker, which retries against
9395C0's deadline and updates A3DD34 when swapping. A pre-existing host dispatch
patch force-clears the gate, permitting multiple main updates per VBlank.
An isolated variant removes only that patch. Old control fails on gate1→0;
restored variant passes all20 dispatch/RAM/register cases. The game link and
ordinary-input progress/performance validation are pending; no shared source
or archive changes for this restoration yet. Variant archive must use gcc-ar
and gcc-ranlib because its object has GCC LTO (plain ar loses the symbol index).

Private frontend elision has 30 real-GPU oracle cases, trace-on fallback, CPU
negative control and actual-name state parity passing, but clean timing remains
pending. Private folded VU specialization has 51/51 VU tests, 504 guard snapshots,
128 general and 2304 arithmetic cases passing; timing was contaminated, so it is
unadopted. Shared VU arithmetic remains unchanged. Root EXE is still the old
menu-follow-up binary and must only be replaced after integrated validation.

The following entries describe earlier checkpoints and their limitations.

Latest validation (2026-10-01 UTC): `output/perf60_queue_unlock/NobleArchimedes.exe`
links successfully with checked bulk guest writes, allocation-free warm GIF
transport, four-picture decoded MPEG lead, and producer unlock during logical
GPU fence wait/readout. All shared GS/Memory/MPEG/VU cases pass: PS2 350/355,
with the same five pre-existing failures listed below; CodeGenerator 61/61 from
tools/PS2Recomp. Python discovery now 18/18. Original471DB8 and79CB28 entries
are preserved by generated aliases;79CB28's72 exact leaf cases pass, and its
host registry object is ready for the next link. Root EXE remains untouched.

The latest230-second clean run (`perf60_queue_unlock_clean`) entered the attract
sequence, state(4,8,1,1), after the12-second menu dwell plus cursor exercise.
Its later59.4–60 readings are ATTRACT playback, not story or post-movie3D.
Main samples before that transition remain around50–56, not a sustained60 claim.
The subsequent diagnostic (`perf60_name_capture`) used a short dwell and reached
actual name/save/loading/story states. Name's hot VU entry is140 (~64cycles/call),
with ~134,000 calls and2.6s inclusive VU time per5s diagnostic window. Its first
two gated captures only contain0/90/A0 and miss the hot calls. A second,140-selected
capture (`perf60_name_hot/vu`) contains two669-call chains (configured limit1024)
for exact offline replay; chain0 has42,403cycles and667orderedPATH1 packets.
The80-second probe ended during driver name acceptance; that driver window error
is a probe-end race, not a game crash. New --name-only avoids the blocked workflow.

Actual story MPEG in the detailed diagnostic runs near59–60 VBlanks/s with three
queued decoded pictures, but still needs a clean final-candidate measurement.
Earlier loading captures under perf60_gpu_diag contain44 calls/254,312cycles;
they were captured during loading, NOT name entry or post-movie3D. No chain/frame
association has been established. Actual post-movie3D with471DB8 restored was
~2VBlanks/s in perf60_native_scene's uncontaminated tail; the first113seconds of
that run had a stray replay process, so discard those initial timing samples.

Windows Power saver remains unchanged. Idle WMI reports2200MHz; an active-load
Balanced comparison is planned before attributing any FPS ceiling to that setting.
Production VU arithmetic is unchanged; isolated arithmetic/ready-pipeline variants
have not demonstrated repeatable gains. A private replay shim matches full-runtime
state/packets and avoids heavy shared links. GPU selector work is checking decoded
dual-display equivalence (placement/reserved bits ignored by the CPU contract),
with profile-only fallback reasons. Periodic kernel and memory-card logs are now
opt-in in source; main host object rebuilt, runtime MemoryCard object pending.

User priority is menu and cutscene speed; first-cutscene rendering and audio are
deferred. Native NTSC pacing is 59.94 VBlanks/s; the local MPEG sequence headers
specify 29.97 unique frames/s. Count guest VBlanks, not UI redraws. Root executable
still has the menu-follow-up hash below until a validated candidate is installed.

First integrated CPU optimization run: `output/perf60_integrated_1`, roughly
19 main-menu VBlanks/s and 30–31 MPEG VBlanks/s, still below target. Since that run,
masked-alpha SIMD menu kernels, typed presentation, actual sprite texture-page
footprints, and the RotateThreadReadyQueue progress-epoch correction are in source.
VU cycle-ring/decoded-pair optimizations preserve guest cycle and arithmetic bits;
93 VU tests pass. Further arithmetic experiments remain isolated in ignored output
and were rejected when slower in clean timing.

Optional pinned paraLLEl-GS Vulkan backend is built with `PS2X_ENABLE_PGS=ON`.
Default selection then tries GPU and falls back to CPU on device failure;
`PS2_GS_BACKEND=cpu` selects CPU explicitly. Private raw GIF hooks preserve each
physical path and suppress duplicate register/image feeds. Host VIF continuation
wrappers carry scoped provenance across the arbiter copy, so the stateful GPU
parser receives original continuation pixels while the CPU parser retains its tag.
Native upload shortcuts reject PRE setup tags to preserve PRIM side effects.

First GPU run (`output/perf60_pgs_1`) was unsuitable for comparison: its RAM scan
failed among Vulkan allocations, so no menu inputs were sent; upstream fragmented
PACKED loops overread data and scanout interpreted HLE pixel widths as GS timing.
These are fixed in source and focused GPU tests. The retained pinned-source patch
also handles non-qword transfer tails. Compatibility presentation uses synchronized
GPU VRAM with the established pixel-unit CPU scanout rules, without CPU rasterization.
The headless reader now validates an opt-in runtime allocation hint inside the PID.

Candidate `output/perf60_pgs_fixed/NobleArchimedes.exe` linked successfully and
`output/perf60_pgs_fixed_1` confirms correct 512x448 title-menu output. Initial
menu windows measured roughly38–40 guest VBlanks/s, still below target. Long
driver dwell/pulses entered the title idle sequence rather than New Game; do not
interpret its later phase8 samples as the requested story cutscene. Driver uses
short cursor pulses now and has a menu-only keepalive mode. The real VIF DIRECT
then DIRECTHL continuation test passes all8 GPU texels. Python tests15/15 pass.

Next production bridge batch preserves repeated/interleaved cold partial-native
uploads, with a failing-before test and opt-in GPU mutex/raw/readback/convert/clear/
Finish counters. VU chain recorder/replayer validates execute+ordered resumes,
including pending effects, changed code/data/TOP/ITOP/D/T, exact cycles and PATH1;
49/49 tests and layout/bound rejection checks pass. Original-scheduler and direct
arithmetic replay binaries are ready to compare the actual hot captures. Arithmetic
remains experimental. Detailed phase/IOP tiny-call traces are now opt-in.

Deferred native clear experiment remains ignored in `output/diag_perf/pgs_clear`:
64 full-VRAM cases matched, unsafe omission differed on17; synchronized full-frame
timing showed no gain, so it is not in production. Shared PS2 suites348/353 passed
with no GS/Memory/VU failures. The remaining five failures also exist in the pre-turn
log. The SIF-DMA fixture now enables hardware cause5, and all10 SIF-DMA tests pass;
no production scheduler change was needed. CodeGenerator61/61 passes from its
required tools/PS2Recomp working directory. Python16/16 tests pass.

Diagnostic `output/perf60_gpu_diag` now follows ordinary input through main menu,
name entry, save bypass, loading, MPEG, and the post-MPEG 3D scene. With detailed
profiling enabled, main-menu samples are roughly35–43 VBlanks/s, name entry12–13,
steady MPEG43–52, and post-MPEG3D about2. This is still below target. Captures
contain44 VU execute/resume calls,254,312 cycles and43 ordered PATH1 packets.
All three offline interpreters match every captured output; stable execution is
about2.2x the original, but the bounded-arithmetic experiment is slower and stays
isolated. A captured chain still costs~57–60ms; its relationship to a complete
guest frame has not been established, so do not infer FPS from this replay alone.

The private bridge now releases its GPU mutex after capturing an immutable VRAM
snapshot, before CPU display conversion. A separate presentation mutex protects
reused storage; Reset/Initialize epochs reject older snapshots. Locked baseline
fails the EE-progress negative control; candidate passes concurrent feed/read/write,
two-Present buffer lifetime, reset rejection, and all233 GPU-snapshot pixel/metadata
presentation cases. Original upload/fragment/cold-order tests still pass.

Detailed HostProfile timers were unexpectedly always enabled. They now require
PS2_HOST_PROFILE=1 or an explicit profile file without a mode override; mode=rate
reports guest VBlank rate without operation timers. Normal play disables them,
and probes default to rate. Checkpoint, command and DMA latency counters follow
the same gate. The standalone five-mode regression fails before and passes after.
Only the profiling header changed, which is absent from generated chunk dependencies;
public runtime class layouts stayed unchanged. Shared runtime rebuilt successfully;
`output/perf60_unlock/NobleArchimedes.exe` linked and was validated in a clean
230-second run (`output/perf60_unlock_probe`): main42–45, name17–18, steady
MPEG52–56 guest VBlanks/s. The input driver starts approximately10seconds after
the game in these older probes; correlate phase boundaries with that offset.
New probes record their actual launch offset in timing.json/navigation.log.

After MPEG, this candidate exposed a missing original guest callback at471DB8.
The subsequent33VBlank/s hardware timer readings have a dormant main thread and
must not be counted as cutscene performance. Source now registers a generated
alias that preserves the original471DB8 prologue/body; Python source checks and
the sound-bank/level-entry executable test pass. Host objects are current, pending
the next full link and ordinary New Game verification.

A GPU logical-display adapter passed313 pixel/metadata comparisons and an
independent review. It reduces readback to the displayed image and preserves CPU
fallback for unsupported layouts. Production integration and real-game speed
validation are in progress. VU flags64 experiments remain isolated until a
repeatable speed improvement is demonstrated; arithmetic state oracles pass.

No full-speed claim is warranted yet; root EXE is still old.

## Update: 2026-09-30 — Menu and VU follow-up (still below full speed)

Root `NobleArchimedes.exe` now matches `output/candidate_menu_followup/NobleArchimedes.exe`.
SHA256: `b6f4fcf716180eb2ff714e49b62f0b6338fadf5ab0b7f602361049d4dae57800`.
Previous root build: `output/backups/NobleArchimedes_before_menu_followup_20260930.exe`.

The previous macroblock optimization mistakenly drained queued draws for small
menu uploads too. A private, scoped GIF packet policy now limits that path to
packets of at least 128 KiB; small menu/font uploads remain queued. Menu samples
previously spent ~3.8–4.0 seconds per five seconds draining; now this wait is zero.
Main-menu samples in `output/menu_followup_benchmark` are roughly 9.8–10.8 guest
VBlanks/s, versus ~4–6 in `output/menu_vif_profile`. These are not full-speed menus.
The name screen remains around 8–9/s. Cursor down/up and New Game inputs were
automated through the game window, with real guest state transitions observed.

Large flat sprites use the existing typed row writer. Opaque rows (including
depth clears) bypass redundant pixel tests. Blends with no destination operand
avoid unnecessary framebuffer reads. Exactly aligned bilinear samples can omit
zero-weight neighboring texels only when direct VRAM reads preserve cache state.
Randomized raster comparisons against the reference remain pixel-exact, including
two-worker feedback, aligned sprites, and bulk movie upload ordering.

The VU graphics packet failure was a control-flow bug: JR/JALR incorrectly used
the conditional-branch VI backup. The game's IADDIU vi1,0,0x57a / JALR vi15,vi1
must call the newly written target, not the old one. Corrected both jumps and
replaced the incorrect JR regression; conditional-branch visibility stays intact.
The full `output/menu_vu_final_validation` New Game/intro run emitted no VU packet
errors and completed the movie into guest phase (4,10,3,1). Movie throughput stays
around 20–21 VBlanks/s (~10–11 movie frames/s); this is still slow.

The generated resource-resolution callback at 0x487B68 is now exposed and tested
for both object flag paths. The next missing target is 0x471DB8 from 0x471D00.
Per-program `PS2_VU_PROFILE=1` diagnostics show no exhausted VU budgets in the
captured scene. 3D remains interpreter-bound (~1 VBlank/s), with millions of VU
cycles taking several seconds. Menu drawing remains CPU rasterizer-bound.

Verification: PS2VU1 42/42, PS2Memory 54/54, sound-bank/level-entry regression,
12 Python build-helper tests, and randomized threaded raster comparisons pass.
Unit suites used PS2_GS_THREADS=0 because their raw VRAM assertions assume Sync.
The headless tools accept PS2 environment overrides, wait briefly for pid.txt,
exercise cursor inputs, and clean their copied executable on launch failure.

Audio is unchanged and still absent: the game's custom IOP sound driver/mixer
and MPEG PCM output are not implemented. No claim of full-speed menus, movies,
gameplay, or working audio is warranted. Windows remains on Power saver.

## Update: 2026-09-30 — Movie performance follow-up

Candidate: `output/candidate_performance_final/NobleArchimedes.exe`, SHA256
`d31f8a5abae7d851681f7f040f05ed74fc5f43ee873c64d22072fb4bc32104ea`.
The root `NobleArchimedes.exe` is now this candidate. Its previous build is
preserved at `output/backups/NobleArchimedes_before_movie_performance_20260930.exe`.
This follows the loading fix below. The source now exposes the generated
animation update entry at 0x794EA0. The next observed missing indirect target
is 0x487B68 inside `sub_00487B18_0x487b18.cpp`; it is still unresolved.

Headless comparisons on this machine (still Windows Power saver, CPU reports
2200 MHz) found MPEG playback at roughly 1.5–2 guest VBlanks/s before the change
and 19–24/s afterwards. These are guest VBlanks, not movie frames: the movie
advances approximately once per two VBlanks and is still below full speed.
The upload ring waits were 4.85 seconds per six-second sample while actual
exclusive upload work was only 0.18 seconds. Waiting for earlier readers once
and performing the 16x16 CT32 / 1024-byte macroblock upload on the producer
eliminates the thousands of per-macroblock worker barriers. Other uploads
retain their original queued path; draining those hurt menu performance.
`PS2_GS_QUEUED_UPLOADS=1` restores the earlier path for comparison.

Two workers measured about 7–9 menu VBlanks/s versus 5–6 with eight workers,
so this application's default is now two. `PS2_GS_THREADS` overrides it.
The VU interpreter, GIF arbiter, and GS frontend now accept IMAGE2 (format 3),
consistent with PCSX2's GIF format definitions, and each XGKICK resets only
packet bookkeeping rather than clearing the entire 64 KiB packet buffer.

Evidence: `output/animation_update_probe` (before upload fix),
`output/video_performance_probe` (initial upload experiment), and
`output/movie_macroblocks_2_workers` (narrowed upload fix). The latter reached
Loading, the opening MPEG sequence, displayed the story video with subtitles
(`frame_3600.png`), and subsequently reached guest phase `(4,10,3,1)` without
skip inputs. World rendering and movement remain unverified. The initial
in-engine scene still runs near 0.4 VBlanks/s with VIF/VU dominating and
oversized XGKICK packet errors; do not describe the entire game as fixed.

Audio is NOT restored. `PS2AudioBackend::onSoundCommand` accepts only generic
LIBSD SID 0x80000701; this game uses custom sound modules. The IOP emulator
models SPU2 DMA status/completion but has no audio mixer. MPEG demux sends
audio guest callbacks but does not decode or output audio. The actual first
PSS audio header is Sony SShd, codec 1, 48000 Hz, stereo, 0x200-byte interleave,
with multiple private substreams. A movie PCM host path and custom driver /
SPU2 implementation are remaining work, not a sound-device setting problem.

Validation: 12 Python build-helper tests, 2 tool tests, 41 VU1 tests (new
IMAGE2 test failed on the old runtime then passed), and 72 GS tests with
`PS2_GS_THREADS=0`. The existing GS suite reads raw VRAM immediately after
submission and fails 22 assertions under asynchronous workers; the inline
run passes all 72. Threaded ordering must use synchronized readback / the
differential raster oracle, not those unsynchronized assertions.
The sound-bank / level-entry executable regression passes. The synchronized
two-worker differential sequence, ping-pong, and feedback oracles each match
the reference on all 203 cases.

Reference format sources:
https://github.com/PCSX2/pcsx2/blob/master/pcsx2/GS/GSRegs.h
https://github.com/vgmstream/vgmstream/blob/master/src/meta/sshd.c

## Update: 2026-09-30 — New Game loading

The root `NobleArchimedes.exe` now comes from
`output/candidate_loading_complete/NobleArchimedes.exe`. SHA256:
`dccf40dd0bf2fad4558cdce3394cac27d45e3376371eeedf060bc6451c87e1b0`.
The previous executable is preserved at
`output/backups/NobleArchimedes_before_loading_fix_20260930.exe`.

The original loading deadlock was reproduced headless after entering a name
and choosing Start without saving. The sound status helper always returned busy
and rewrote fixed masks. Accepted bank prepare/finish/data commands now update
per-bank state; the fallback RPC callback preserves that state instead of
replacing it with zeros. This is compatibility feedback for the unimplemented
custom IOP sound service, not a complete audio implementation.

Once that wait cleared, level setup exposed an omitted resource callback at
`0x454B40` and a split function whose JAL delay slot (`0x500000`) and return entry
(`0x500004`) were missing. Both are restored. Additional resource callback
entries are generated from the original local guest code:
`0x7A7098`, `0x7A7328`, `0x7A7358`, `0x79C930`, `0x79C960`,
`0x79C9F8`, and `0x924828`.

Persistent changes are in the root sound compatibility sources, runtime stub
registry, unity generator, and `tools/generate_resource_entries.py`. Generated
guest code, executable candidates, RAM, and frames remain ignored and local.

Validation: 11 build-helper tests, two table-generator tests, and the C++ sound
and entry regression pass. All linked objects passed source dependency checks.
`output/loading_complete_validation_20260930/navigation.log` records the final
candidate moving from `(4,10,3,3)` to `(4,10,7,0)` and `(4,10,7,1)`;
the decoder produces frames instead of remaining at the original loading wait.
An earlier candidate also reached the actual in-game Player menu (Level 1,
HP 100/100); see `output/loading_single_renderer_20260930/frame_4300.png`.
World rendering and character movement are **not verified**.

Next blockers: the final probe reports a missing animation callback
`0x794EA0` (inside `sub_00794898_0x794898.cpp`), and movie/world display is black.
The movie renderer issues hundreds of small uploads per frame and spends most
of its time waiting on the GS worker ring. One renderer thread makes the main
menu slower, so globally disabling workers is not a general optimization.
Use the new bounded `probe_headless.py`, `probe_new_game.py`, and read-only
`probe_guest_ram.py` tools for further reproduction. Runtime/submodule changes
from earlier work were preserved. Nothing has been committed.

The older snapshot below is historical.

Snapshot date: 2026-09-27. Host: Windows 11, Ryzen 7 2700X (8C/16T), MinGW g++ (scoop), raylib host window.
**Nothing is committed.** All work is uncommitted in the nested repo `tools/PS2Recomp` (see "Uncommitted state").

## 1. Where it is stuck right now

The game boots, shows the "No game data present on memory card" notice, then (with the fixes below) moves on
to play the intro FMV `\PSS\ST17_00N.PSS`. **The FMV phase runs at ~2.2 VBlanks/s (target 60).**

Cause, measured with the host profiler (`PS2_HOST_PROFILE_FILE`, see §5):

- Three guest threads at priority 41 rotate through `RotateThreadReadyQueue` (syscall 0x2B, wrapper `0x75D2D0`):
  - thread 5 = idle thread, `sub_00775D90`: `for(;;) RotateThreadReadyQueue(41)`.
  - thread 6 = decoder, `sub_00776B08`: yield, poll `func_776DE8` for stream data, `sceMpegGetPicture` (HLE stub).
  - thread 1 = stream feeder: `sceMpegDemuxPssRing` (HLE), `sceSdRemote`, etc.
- ~156k scheduler turns per host second at ~6 µs each. Each turn advances guest time by only ~67 EE cycles,
  because **syscalls and context switches cost zero guest cycles** in this runtime. Guest time therefore runs at
  ~3.5% of real speed, and the CD stream data the decoder waits for (delivered on guest-time deadlines) trickles in.

**The next step, implemented but never run** (the user interrupted the test): charge kernel time.
- `ps2xRuntime/src/lib/ps2_runtime.cpp`, `PS2Runtime::handleSyscall`: `accountCycles(200)` per syscall.
- `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`, `EeScheduler::makeRunning`: `accountCycles(800)` per thread switch.
- Built and linked as `output/diag_perf/NobleArchimedes_kcycles.exe`. **Untested.**
- Expected result: ~1,000 cycles per yield, so guest time runs at about 50% of real speed in the FMV loop.
- The constants are estimates, not measurements. They change guest timing globally; see §4 (risks).

After that, the remaining host cost per scheduler turn has three parts:
- `pendingEvents`: ~1.5 µs per call, twice per turn;
- the guest slice: ~3.7 µs;
- thread switches that still throw (see §2.3).

## 2. Fixes made in this session (all uncommitted)

### 2.1 Deadlock at the memory-card notice (the "stuck, background stops moving" bug) — FIXED, verified in game
- **Symptom:** the notice appears and the background animation freezes; 100% of guest PC samples are at `0x420740`.
- **The stuck loop:** `sub_00420710` does `do { WaitSema(m); empty = all 11 DMA-queue slots @0xAC3C40 are 0; SignalSema(m); } while(!empty)`.
  The queue is drained by the DMAC completion interrupt handler (GIF ch2 had CIS2 and CIM2 set, and slot 2 was still occupied).
- **Root cause:** `EeScheduler::checkpointDue` returned false whenever `guestDispatchDepth() != 0`
  ("Nested native calls must unwind first"). `sub_00420710` is called nested (from `0x443D30`), so the spin never
  reached a safe point. No interrupts, no VBlank (the vsync counter was frozen at 772), and no switch to
  ready thread 4 (priority 32, higher than thread 1's 41).
- **Fix:** nested checkpoints may now unwind. Generated code already unwinds by returning:
  `if (!dispatchGuestBranch(...)) return;`, and every function is resumable at its loop heads and return addresses.
  Two exceptions remain blocked:
  - (a) runtime code that called a guest function natively (SIF RPC callback/server in `Kernel/Syscalls/RPC.cpp`),
    tracked by `ps2_guest_dispatch::NativeGuestCallScope`;
  - (b) `ctx->pc == entry PC of the innermost callee` (the dispatcher reads that as "returned normally").
- **Files:** new `ps2xRuntime/include/runtime/ps2_guest_dispatch_state.h`, `ps2_runtime.cpp` (`DispatchDepthScope` records
  the callee entry PC; free functions `nativeGuestCallActive()` and `currentCalleeEntryPc()`), `RPC.cpp`, `EeScheduler.cpp`.
- **Known imperfection:** `DispatchDepthScope` sets `s_calleeEntryPc = targetPc` *before* the dispatch-level
  `checkpointDue` call in `dispatchGuestBranch`. So dispatch-level checkpoints in nested frames are always refused;
  only backward-edge checkpoints unwind. The fix: set the entry PC only around the actual `targetFn`/`nextFn` calls.
- **Not yet done:** run `ps2x_tests` (scheduler and interrupt tests) against this change.

### 2.2 Missing FMV files — FIXED
`sceCdSearchFile` looks under `extracted/`, and `extracted/PSS` did not exist, so the game retried forever.
I extracted `PSS/` (25 files, 2.2 GB) from `Castlevania - Curse of Darkness (USA).iso` with `tools/ps2_iso_reader.py`.
`DUMMY.BIN` from the ISO is still not extracted; it may never be needed.

### 2.3 Exception-free thread switch after syscalls — implemented and tested once (FMV: 0.6 → 2.2–3.4 VBlanks/s)
- **Before:** every thread switch threw `EeDispatcherTransfer` (~5–9 µs on MinGW SEH).
- **Now:** `EeScheduler::transferIfRequested(interruptSafe, ctx)` defers the switch instead of throwing when the
  syscall returns straight to its caller (the words at `ctx->pc` are `jr $ra` / `nop`) and no native guest call is active.
- **How the deferral works:**
  - it sets `m_deferredTransfer`;
  - `dispatchGuestBranch` returns false right after `targetFn`/`nextFn` while the flag is set;
  - `EeScheduler::run` clears the flag after each guest run.
- All callers in `Syscalls/Sync.cpp` and `Syscalls/Thread.cpp` now pass `ctx`.
- `blockCurrent` (WaitSema, SleepThread…) still throws; the same technique could apply there.

### 2.4 Yield-spin fast-forward — implemented, fires rarely (4 times in 200 s), harmless
- **What it does:** `EeScheduler::noteYield`. If every ready thread at the running priority has yielded with no kernel state
  change (`m_progressEpoch`, bumped in `publishSnapshot()` and on interrupt-handler dispatch) and at most 4,096 cycles
  between yields, it advances guest time to the next deadline.
- **Why it rarely fires:** thread 1 does real work between yields.
- **Log line:** `[spin-fast-forward]`.

### 2.5 Controller input path — investigated, not the blocker
- **`scePad*` reads work:** they are HLE stubs in `Kernel/Stubs/Pad.cpp`, fed by raylib gamepad/keyboard through `ps2_pad.cpp`.
- **Presses arrive:** the game reads the pad about 60 times/s, and scripted presses reached it (`pressedReads=109`).
- **Oddity, possibly relevant later:** the stub models a digital-only pad.
  - `scePadInfoMode(PAD_MODETABLE)` lists only ID 4, so the game (`0x4050F8` / `0x405040`) never switches to analog (ID 7).
  - `scePadEnterPressMode` is called every frame, and the status data stays `0x41`.
  - A real DualShock 2 reports the table `[4, 7]` and `0x73`/`0x79`.
  - Fix this if the game ignores input later.
- **Also:** `ps2_pad.cpp` ignores the keyboard whenever gamepad 0 exists.
- **New opt-in tools:** `PS2_PAD_TRACE=1` (per-second call counts, raylib gamepad detection, last status bytes) and
  `PS2_PAD_SCRIPT="20:cross,23:start"` (seconds after the first pad read, 250 ms presses).

### 2.6 Performance work earlier in this session (menu screen: 0.1 → 33–42 VBlanks/s)
All measured on the memory-card screen, which turned out to be the deadlocked state. Details are in
`output/perf-notes.md`.
- **Async stdio relay and gated logs:** `ps2_async_stdio.cpp`; the logs are behind `PS2X_ENABLE_AGRESSIVE_LOGS=OFF`.
- **Multithreaded GS rasterizer:** 8 row-band workers, per-page hazard tracking, and asynchronous present.
- **IOP fixes:** IOP batching, and the SPU2 STATX DMA-busy bit fix in `ps2xIOP` (with a test).
- **Allocator-spin fast-forward:** `isQueueSpin` in `checkpointDue`, a game-specific hack.
- **Sprite rasterizer fast path, bit-exact:** `gs_cpu_backend.cpp`, `DrawSpriteTexturedFast` / `DrawSpriteTexturedRows`
  / `WritePixelRow`, plus `GSMem::RowAccess` in `ps2_gs_memory.h`:
  - row-hoisted swizzle addressing;
  - per-draw CLUT decode;
  - SSE2 bilinear filtering;
  - direct texture reads when the draw cannot write its sampled pages (`TexturePageCache::MatchesMemory`/`Load`).
- **Debug-snapshot throttling:** `EeScheduler::publishSnapshot` is dirty-flag throttled to 10 ms, published immediately
  outside `run()` and before blocking. It was 12.7% of EE time plus heap churn. Built (`NobleArchimedes_snapfix.exe`)
  but never measured.

## 3. Validation assets
- **GS differential oracle (bit-exact, compares hashes of all 4 MiB of VRAM):** `output/diag_perf/run_raster_diff.sh <seed> <cases> <mode> [threads]`
  and `run_raster_matrix.sh <cases> <seeds...>`.
  - The reference rasterizer snapshot is in `output/diag_perf/reference_gs/`.
  - Modes: single, disjoint, sequence, pingpong, sprites, sprites-disjoint, feedback, and stale (synchronous only).
  - Last full matrix (seeds 81 and 82, 56 runs): all identical. Five transient diffs were traced to two matrix runs
    overwriting each other's files; the runner now uses PID-tagged files.
  - Mutation-tested: rounding, Z write, overlap guard, and stale-page check.
- **Replay benchmark:** `ps2xRuntime/tests/gs_sprite_raster_bench.cpp`, run on captured real draws in
  `output/diag_perf/draw_captures/` (`PS2_GS_CAPTURE_DIR` together with `PS2_GS_DRAW_STATS=1` produces them).
- **IOP tests:** pass. **`ps2x_tests`:** last known 432/437 (5 pre-existing failures), **not re-run** after the
  scheduler changes (§2.1, 2.3, 2.4, snapshot throttling). Run them first.

## 4. Risks and things to clean up
- **Build flags:** the CMake cache was changed to `CMAKE_CXX_FLAGS_RELEASE="-O3 -DNDEBUG -g"` for profiling. Revert with
  `cmake -S tools/PS2Recomp -B tools/PS2Recomp/build -DCMAKE_CXX_FLAGS_RELEASE="-O3 -DNDEBUG"`.
- **Guest chunk flags:** chunks are now built with `-O2 -fno-strict-aliasing -fwrapv` (`tools/build_recomp_chunks.py`
  `GUEST_OPT_FLAGS`); they were `-O0`. No visible regression, and no measurable speed change either.
- **Kernel cycle costs (§1):** these change guest timing globally. Verify that menus, audio and FMV pacing still behave.
- **Log gating that didn't apply:** `dispatchGuestBranch` prints `[checkpointDue] ...` on every true dispatch-level
  checkpoint. I tried to gate it behind `PS2_IF_AGRESSIVE_LOGS`, but the edit did not apply (string mismatch). Do it,
  since it can flood stderr.
- **Temporary instrumentation to remove or make opt-in:**
  - the EE guest-PC sampler in `checkpointDue` (`[pc-profile]`);
  - the IOP PC sampler and RAM dump in `ps2xIOP/src/emulator/iop_emulator.cpp` `step()`;
  - `HostProfile` periodic report;
  - `PS2_SPIN_DIAG` block in `checkpointDue`;
  - `DrawStats` (`PS2_GS_DRAW_STATS`);
  - pad trace.
- **`isQueueSpin`** (hard-coded PCs in `checkpointDue`) is a game-specific hack from earlier work. With §2.1 it may no
  longer be needed; test removing it.
- **Power plan:** Windows is on the "Power saver" plan (CPU held at ~2.2 GHz), which roughly halves every number here.
  Do not change it without asking the user.
- **Pre-existing modifications:** some files listed below were already modified before this session (for example
  `iop_cdvd.cpp`, `ps2_vfs.cpp`, `CD.cpp`, `GS.cpp`). Don't assume every diff is from this session.

## 5. How to build, run and measure
```
# runtime library (the nested CMake build)
cmake --build tools/PS2Recomp/build --config Release --target ps2_runtime --parallel 8
# guest chunks + host objects (only stale ones; ee_scheduler.h changes rebuild chunks 27, 31 and main, ~7 min;
# ps2_runtime.h changes rebuild ALL 33 chunks, ~70 min with 4 jobs, so avoid touching it)
python tools/build_recomp_chunks.py --jobs 4
# link a candidate (keep the root NobleArchimedes.exe untouched)
python tools/link_noble_archimedes.py output/diag_perf/NobleArchimedes_<name>.exe
# timed capture: in-memory stdout/stderr, host profile to <OutDir>\host_profile.log, screenshots
powershell output/diag_perf/run_capture_nul.ps1 -Exe <exe> -OutDir <dir> -Seconds 150 -SaveLogs
```
- Boot to the notice takes about 100 s of wall time at the current speed. Game windows appear on the user's desktop,
  so warn them before each run.
- **Profiling:**
  - `PS2_RIP_SAMPLES=<file>` (EE thread) and `PS2_RIP_SAMPLES_GS0=<file>` (GS worker 0), then
    `output/diag_perf/symbolize_samples.py <exe> <file>` or `abs_line_profile.py`. Link with `-g` (see
    `build_link_command` plus `-g`) for line-level results; the runtime uses LTO.
  - The `host_profile.log` line `vsync=+N (X/s)` is the frame-rate metric.

## 6. Suggested next steps, in order
1. Run `ps2x_tests`, and fix any regressions from the §2.1/§2.3/§2.4 scheduler changes.
2. Test `NobleArchimedes_kcycles.exe` in the FMV phase. If the FMV plays at about half speed or better, keep it and
   tune the constants; otherwise profile again.
3. Make `blockCurrent` deferrable like §2.3, and cut the per-turn cost of `processPendingEvents`.
4. Fix the `DispatchDepthScope` entry-PC ordering (§2.1 known imperfection).
5. Continue into the title screen and gameplay. Then revisit the frame rate there, where triangles and VU1 will
   dominate instead of sprites. Fix the pad analog/pressure modes if input is ignored.
