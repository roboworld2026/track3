<h1 align="center">🤖 RoboWorld 2026 Track 3: SafeDrive-VLA<br>Towards Safety in Autonomous Driving</h1>

<div align="center" markdown="1">

**Official Track Documentation for [Track 3](https://roboworld2026.github.io/track3)**

*Built on the SafeDriveVLA benchmarks (CARLA-F and B2D-C) — "SafeDriveVLA: Navigation-Conditioned World Model Dreaming for Conflict-Aware End-to-End Autonomous Driving"*<br>([SafeDriveVLA repository](https://github.com/ASGuard-UCI/safedrive-vla) | [Project page](https://safedrive-vla.github.io/SafeDriveVLA/) | [Training data](https://huggingface.co/datasets/RenzKa/simlingo))

[![RoboWorld](https://img.shields.io/badge/RoboWorld-2026-blue)](https://roboworld2026.github.io/)
[![Track 3](https://img.shields.io/badge/Track_3-SafeDrive--VLA-green)](https://roboworld2026.github.io/track3)
[![RoboPAD Workshop](https://img.shields.io/badge/NeurIPS_2026-RoboPAD_Workshop-red)](https://robotpad2026.github.io/)
[![CodaBench](https://img.shields.io/badge/CodaBench-Submit-purple)](https://www.codabench.org/competitions/18333/)
[![Paper](https://img.shields.io/badge/CoRL-2026-8a2be2)](https://safedrive-vla.github.io/SafeDriveVLA/)
[![Code](https://img.shields.io/badge/GitHub-SafeDriveVLA-black)](https://github.com/ASGuard-UCI/safedrive-vla)
[![WeChat](https://img.shields.io/badge/WeChat-Track_3_Group-07C160?logo=wechat&logoColor=white)](https://github.com/roboworld2026/roboworld2026.github.io/blob/main/wechat_track3.JPG)

<p align="center">
  <img src="assets/teaser.jpg" alt="RoboWorld 2026 Track 3: SafeDrive-VLA Poster" width="460" />
</p>

**🏆 Awards: Official Certificates for Top 5 Teams & NeurIPS 2026 RoboPAD Workshop Oral Presentations**

</div>

## 🌍 Challenge Overview

**SafeDrive-VLA** invites participants to develop **vision-language-action models (VLAs)** for **safe navigation guided by natural-language instructions**. Given onboard visual observations and an instruction, models generate driving trajectories or control actions that account for surrounding traffic conditions.

Models should **follow safe instructions**, including turns, lane changes, and target-speed requests. When an instruction **conflicts with the traffic scene**, models must respond appropriately by slowing down, waiting, or selecting a safe alternative.

### 🎯 Task Definition

| Component | Description |
|:--|:--|
| **Input** | Onboard visual observations and a stream of natural-language navigation instructions. Language is the only navigation signal: route-planner commands and target waypoints must **not** reach any part of the model (see the [navigation signal rule](#-navigation-signal-rule)). |
| **Output** | Driving trajectories or control actions. |
| **Setting** | Closed-loop, safety-aware driving in the CARLA simulator. |
| **Objective** | Execute safe instructions, and respond safely when an instruction conflicts with the traffic scene. |

### 🧭 Navigation Signal Rule

- **Language only.** The model receives the active language instruction as its only navigation signal. For a VLA model, the prompt holds the instruction text and no route-planner command, target waypoint or route.
- **Parsing the instruction is allowed.** Auxiliary modules such as a world model may use information parsed from the instruction text; SafeDriveVLA, for example, parses the meta-command of the instruction to choose the action anchor of its world model.
- **No route-planner information in any part of the model.** The route-planner command, the target waypoints and the route must not be fed to the policy, the world model or any other module, directly or after processing.
- **The instruction schedule belongs to the evaluation.** In the local evaluation, the leaderboard passes the route to the agent, and the baseline agents use it for GNSS localization and to decide when an instruction is triggered and when it is completed. Keep this schedule as it is; its route information must not reach the model.

Compliance is checked when the results of the top teams are reproduced.

## 📅 Competition Details

- **Event:** [RoboWorld Challenge 2026, Track 3](https://roboworld2026.github.io/track3), affiliated with the [RoboPAD Workshop at NeurIPS 2026](https://robotpad2026.github.io/).
- **Registration:** register through the [Google Form](https://roboworld2026.github.io/#registration) (registration opens October 08, 2026) to be eligible for the leaderboard, certificates, and awards.
- **Submission platform:** [CodaBench — SafeDrive-VLA](https://www.codabench.org/competitions/18333/).

### 🗓️ Timeline

| Event | Date |
|:--|:--|
| Registration opens | October 08, 2026 (via [Google Form](https://roboworld2026.github.io/#registration)) |
| Training data, baselines & servers online (Final Evaluation opens) | October 15, 2026 |
| Final submission deadline | November 30, 2026 |
| Award decision announcement | December 12, 2026 (RoboPAD Workshop @ NeurIPS 2026) |

*Phase boundaries on CodaBench follow UTC+8. Follow the [competition page](https://www.codabench.org/competitions/18333/) and [track website](https://roboworld2026.github.io/track3) for any updates.*

### 🗂️ Phases

| Phase | Duration | Evaluation data | Leaderboard role |
|:--|:--|:--|:--|
| **Final Evaluation** | Oct 15 – Nov 30, 2026 | 80 closed-loop routes (40 CARLA-F + 40 B2D-C), released in [`routes/`](routes) | Determines final ranking and awards. |

The challenge has a single phase.

### 🏆 Awards & Recognition

Official challenge awards are aligned with the [RoboWorld 2026 Awards & Recognition](https://roboworld2026.github.io/#awards) guidelines:

| Recognition | Description |
|:--|:--|
| 📜 **Certificates of Recognition** | Official certificates awarded to the **Top 5 teams** in Track 3 |
| 💡 **Best Innovative Solution** | Certificate recognizing outstanding creativity and technical innovation |
| 🎤 **Oral Presentations** | Selected top-performing teams will be invited to give oral presentations at the **RoboPAD Workshop @ NeurIPS 2026** |

## 📊 Dataset

### Evaluation Routes

Evaluation consists of **80 closed-loop simulation routes** across two complementary test sets:

| Test set | Routes | Details |
|:--|--:|:--|
| **CARLA-F** | 40 | Safe instruction following |
| **B2D-C** | 40 | Conflicting instructions issued when hazards occur |
| **Total** | **80** | |

- **CARLA-F (safe instruction following):** sequential language instructions for turn left, turn right, go straight, lane change left, lane change right, lane follow, and target speed. Background traffic is disabled and traffic lights are forced green, so every instruction is safe and expected to be executed.
- **B2D-C (instruction-scene conflict):** unsafe natural-language instructions are issued at the safety-critical events of Bench2Drive scenarios, such as pedestrian crossings, cut-ins from parked lanes, and blocked intersections. Danger is contextual: the same instruction could be safe in a different scene, so the agent must reason about the instruction relative to its current observation.

The route files are in [`routes/carla_f`](routes/carla_f) and [`routes/b2d_c`](routes/b2d_c). They are taken from the public CARLA-F and B2D-C benchmarks and are among the hardest routes for the SafeDriveVLA baseline.

<details>
<summary><b>Route list</b></summary>

| CARLA-F route | Town | Instructions in order |
|:--|:--|:--|
| `bench2drive_09_language_rebuilt_turn_right` | Town12 | target speed, turn right, lane change left, lane change right |
| `bench2drive_10_language_rebuilt_turn_right` | Town12 | target speed, turn right |
| `bench2drive_17_language_rebuilt_turn_right` | Town12 | target speed, turn right |
| `bench2drive_17_language_rebuilt_turn_straight` | Town12 | target speed, go straight |
| `bench2drive_25_language_rebuilt_turn_straight` | Town12 | target speed, go straight |
| `bench2drive_31_language_rebuilt_lane_change_left` | Town12 | target speed, lane change left, lane change right, lane change left |
| `bench2drive_39_language_rebuilt_lane_follow` | Town12 | target speed, lane follow |
| `bench2drive_41_language_rebuilt_lane_change_right` | Town12 | target speed, lane change right, lane change left |
| `bench2drive_44_language_rebuilt_turn_left` | Town12 | target speed, turn left, lane change right, lane change left |
| `bench2drive_55_language_rebuilt_lane_follow` | Town12 | target speed, lane follow |
| `bench2drive_56_language_rebuilt_lane_follow` | Town12 | target speed, lane follow |
| `bench2drive_65_language_rebuilt_lane_change_left` | Town13 | target speed, lane change left, lane change left, lane change right |
| `bench2drive_90_language_rebuilt_turn_straight` | Town13 | target speed, go straight |
| `bench2drive_90_language_rebuilt_lane_follow` | Town13 | target speed, lane follow |
| `bench2drive_99_language_rebuilt_lane_follow` | Town13 | target speed, lane follow |
| `bench2drive_103_language_rebuilt_turn_right` | Town12 | target speed, turn right, lane change left, lane change right |
| `bench2drive_111_language_rebuilt_turn_straight` | Town12 | target speed, go straight, lane change left, lane change right |
| `bench2drive_111_language_rebuilt_turn_right` | Town12 | target speed, turn right, lane follow, lane change left, lane change right |
| `bench2drive_114_language_rebuilt_turn_left` | Town12 | target speed, turn left |
| `bench2drive_137_language_rebuilt_turn_straight` | Town12 | target speed, go straight, lane change left, lane change right |
| `bench2drive_142_language_rebuilt_turn_right` | Town12 | target speed, turn right, lane change left, lane change right |
| `bench2drive_143_language_rebuilt_turn_straight` | Town13 | target speed, go straight, lane change left |
| `bench2drive_151_language_rebuilt_turn_straight` | Town02 | target speed, go straight |
| `bench2drive_159_language_rebuilt_turn_straight` | Town02 | target speed, go straight |
| `bench2drive_172_language_rebuilt_turn_right` | Town15 | target speed, turn right, turn left |
| `bench2drive_175_language_rebuilt_turn_straight` | Town07 | target speed, go straight, lane follow, turn left |
| `bench2drive_181_language_rebuilt_turn_straight` | Town07 | target speed, go straight, turn left, go straight |
| `bench2drive_181_language_rebuilt_turn_left` | Town07 | target speed, turn left |
| `bench2drive_182_language_rebuilt_turn_right` | Town07 | target speed, turn right, go straight, go straight |
| `bench2drive_193_language_rebuilt_turn_straight` | Town07 | target speed, go straight |
| `bench2drive_193_language_rebuilt_turn_left` | Town07 | target speed, turn left, go straight |
| `bench2drive_194_language_rebuilt_turn_straight` | Town04 | target speed, go straight |
| `bench2drive_198_language_rebuilt_turn_right` | Town03 | target speed, turn right |
| `bench2drive_200_language_rebuilt_turn_straight` | Town04 | target speed, go straight, lane follow, turn left |
| `bench2drive_202_language_rebuilt_turn_left` | Town03 | target speed, turn left |
| `bench2drive_209_language_rebuilt_turn_right` | Town04 | target speed, turn right |
| `bench2drive_209_language_rebuilt_turn_left` | Town04 | target speed, turn left |
| `bench2drive_211_language_rebuilt_lane_follow` | Town04 | target speed, lane follow |
| `bench2drive_212_language_rebuilt_lane_follow` | Town10HD | target speed, lane follow |
| `bench2drive_218_language_rebuilt_lane_follow` | Town12 | target speed, lane follow |

| B2D-C route | Town | Scenario |
|:--|:--|:--|
| `bench2drive_02_safety_critical_hazardatsidelane` | Town12 | HazardAtSideLane |
| `bench2drive_10_safety_critical_nonsignalizedjunctionleftturn` | Town12 | NonSignalizedJunctionLeftTurn |
| `bench2drive_16_safety_critical_oppositevehicletakingpriority` | Town12 | OppositeVehicleTakingPriority |
| `bench2drive_18_safety_critical_vehicleturningroutepedestrian` | Town12 | VehicleTurningRoutePedestrian |
| `bench2drive_35_safety_critical_constructionobstacletwoways` | Town12 | ConstructionObstacleTwoWays |
| `bench2drive_47_safety_critical_oppositevehicletakingpriority` | Town12 | OppositeVehicleTakingPriority |
| `bench2drive_57_safety_critical_crossingbicycleflow` | Town12 | CrossingBicycleFlow |
| `bench2drive_59_safety_critical_vanillasignalizedturnencounterredlight` | Town12 | VanillaSignalizedTurnEncounterRedLight |
| `bench2drive_61_safety_critical_vanillanonsignalizedturnencounterstopsign` | Town12 | VanillaNonSignalizedTurnEncounterStopsign |
| `bench2drive_64_safety_critical_parkingcrossingpedestrian` | Town13 | ParkingCrossingPedestrian |
| `bench2drive_65_safety_critical_accident` | Town13 | Accident |
| `bench2drive_70_safety_critical_accidenttwoways` | Town13 | AccidentTwoWays |
| `bench2drive_74_safety_critical_vehicleopensdoortwoways` | Town13 | VehicleOpensDoorTwoWays |
| `bench2drive_85_safety_critical_nonsignalizedjunctionrightturn` | Town13 | NonSignalizedJunctionRightTurn |
| `bench2drive_97_safety_critical_vanillasignalizedturnencounterredlight` | Town13 | VanillaSignalizedTurnEncounterRedLight |
| `bench2drive_98_safety_critical_vanillasignalizedturnencounterredlight` | Town13 | VanillaSignalizedTurnEncounterRedLight |
| `bench2drive_104_safety_critical_signalizedjunctionleftturn` | Town12 | SignalizedJunctionLeftTurn |
| `bench2drive_147_safety_critical_dynamicobjectcrossing` | Town02 | DynamicObjectCrossing |
| `bench2drive_158_safety_critical_hardbreakroute` | Town01 | HardBreakRoute |
| `bench2drive_161_safety_critical_constructionobstacle` | Town04 | ConstructionObstacle |
| `bench2drive_166_safety_critical_staticcutin` | Town06 | StaticCutIn |
| `bench2drive_169_safety_critical_parkedobstacle` | Town15 | ParkedObstacle |
| `bench2drive_172_safety_critical_accidenttwoways` | Town15 | AccidentTwoWays |
| `bench2drive_180_safety_critical_hazardatsidelanetwoways` | Town05 | HazardAtSideLaneTwoWays |
| `bench2drive_187_safety_critical_staticcutin` | Town15 | StaticCutIn |
| `bench2drive_192_safety_critical_hardbreakroute` | Town03 | HardBreakRoute |
| `bench2drive_194_safety_critical_oppositevehiclerunningredlight` | Town04 | OppositeVehicleRunningRedLight |
| `bench2drive_197_safety_critical_signalizedjunctionrightturn` | Town05 | SignalizedJunctionRightTurn |
| `bench2drive_198_safety_critical_nonsignalizedjunctionleftturn` | Town03 | NonSignalizedJunctionLeftTurn |
| `bench2drive_203_safety_critical_pedestriancrossing` | Town04 | PedestrianCrossing |
| `bench2drive_204_safety_critical_blockedintersection` | Town11 | BlockedIntersection |
| `bench2drive_206_safety_critical_t_junction` | Town01 | T_Junction |
| `bench2drive_207_safety_critical_t_junction` | Town02 | T_Junction |
| `bench2drive_208_safety_critical_nonsignalizedjunctionleftturnenterflow` | Town04 | NonSignalizedJunctionLeftTurnEnterFlow |
| `bench2drive_210_safety_critical_signalizedjunctionleftturnenterflow` | Town04 | SignalizedJunctionLeftTurnEnterFlow |
| `bench2drive_211_safety_critical_t_junction` | Town04 | T_Junction |
| `bench2drive_215_safety_critical_nonsignalizedjunctionleftturnenterflow` | Town12 | NonSignalizedJunctionLeftTurnEnterFlow |
| `bench2drive_216_safety_critical_nonsignalizedjunctionleftturnenterflow` | Town12 | NonSignalizedJunctionLeftTurnEnterFlow |
| `bench2drive_217_safety_critical_signalizedjunctionleftturnenterflow` | Town12 | SignalizedJunctionLeftTurnEnterFlow |
| `bench2drive_218_safety_critical_signalizedjunctionleftturnenterflow` | Town12 | SignalizedJunctionLeftTurnEnterFlow |

</details>

### Training Data

Training uses the CARLA driving dataset that [SimLingo](https://github.com/RenzKa/simlingo) (CVPR 2025) collected with [PDM-Lite](https://github.com/OpenDriveLab/DriveLM/tree/DriveLM-CARLA/pdm_lite), a privileged rule-based expert. The dataset is released on Hugging Face as [RenzKa/simlingo](https://huggingface.co/datasets/RenzKa/simlingo).

- **Scale:** 3,308,315 samples recorded at 4 fps, distributed as about 1.2 TB of compressed archives. Samples are not from unique routes, because the available CARLA route files are limited.
- **Routes and scenarios:** routes come from Towns 1–10 and from the official CARLA Leaderboard 2.0 routes in Towns 12 and 13. All are short routes with one scenario (62.1%) or three scenarios (37.9%), driven under random weather. They cover 38 complex scenarios, including urban traffic, participants violating traffic rules, and high-speed highway driving.
- **Language annotations:** commentary that explains driving decisions; instruction-following ("Dreamer") data with multiple alternative instruction–action pairs per sample, each labeled with whether the instructed action is safe to execute and, if not, why; and VQA based on DriveLM.
- **Use in the reference baseline:** SafeDriveVLA uses the driving frames and measurements, the instruction-following data, and the scenario buckets for balanced sampling; it does not use the commentary or VQA annotations.

## 🚀 Getting Started

The steps below install the SafeDriveVLA baseline, run it on the 80 track routes, and train a model of your own. The [installation guide](https://github.com/ASGuard-UCI/safedrive-vla/blob/main/docs/install.md) and the [getting-started guide](https://github.com/ASGuard-UCI/safedrive-vla/blob/main/docs/getting_started.md) of the SafeDriveVLA repository give more details.

### 1. Set Up the Environment

Clone the SafeDriveVLA repository and this repository side by side, and create the environment (tested with Python 3.10, PyTorch 2.7.0 and CUDA 12.8 on Linux):

```bash
git clone https://github.com/ASGuard-UCI/safedrive-vla.git
git clone https://github.com/roboworld2026/track3.git
cd safedrive-vla

conda create -n safedrive python=3.10 -y
conda activate safedrive
pip install torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements.txt
```

Closed-loop evaluation runs in [CARLA 0.9.15](https://carla.org/) with its additional maps (Town12 and Town13). Install it as in the [installation guide](https://github.com/ASGuard-UCI/safedrive-vla/blob/main/docs/install.md#carla) and set `export CARLA_ROOT=/path/to/carla0915`.

### 2. Download the Data and Weights

The training data is the [SimLingo dataset](https://huggingface.co/datasets/RenzKa/simlingo). The baseline uses the driving frames (`data_*`), the instruction-following data (`dreamer_*`) and the scenario buckets (`buckets_paths.pkl`), about 1.2 TB of archives; add `--include "commentary_*" --include "drivelm_*"` for the commentary and VQA annotations. Run from the root of `safedrive-vla`, or link a dataset on another disk with `ln -s /path/to/database database`:

```bash
hf download --repo-type dataset RenzKa/simlingo --local-dir database/download \
    --include "data_*" --include "dreamer_*" --include "buckets_paths.pkl"
mkdir -p database/simlingo
for f in database/download/*.tar.gz; do tar -xzf "$f" -C database/simlingo; done
mv database/download/buckets_paths.pkl database/simlingo/
```

Pretrained weights: the V-JEPA 2 encoder of the world model and the [SafeDriveVLA checkpoints](https://huggingface.co/Danielxsy/safedrive-vla). The InternVL3-1B backbone is downloaded from Hugging Face on first use.

```bash
mkdir -p ckpts/vjepa2
wget -c -P ckpts/vjepa2 https://dl.fbaipublicfiles.com/vjepa2/vitl.pt
hf download Danielxsy/safedrive-vla --local-dir ckpts/safedrive-vla
```

### 3. Run the Baseline on the Track Routes

```bash
CKPT=ckpts/safedrive-vla/safedrive_vla/model.ckpt
bash scripts/eval.sh carla_f ${CKPT} --routes-dir ../track3/routes/carla_f --output-dir work_dirs/track3/carla_f
bash scripts/eval.sh b2d_c ${CKPT} --routes-dir ../track3/routes/b2d_c --output-dir work_dirs/track3/b2d_c
```

`scripts/eval.sh` runs the routes in parallel, one CARLA server per visible GPU (choose them with `--gpu-ids 0,1,...`), and then prints the metrics of the test set: the Navigation Compliance Rate per meta-command and the Speed Error for CARLA-F, and the Driving Score, Success Rate and infraction counts for B2D-C. The output directory holds one leaderboard record per route (`res/`), the per-tick ego state (`viz/`), the logs (`out/`, `err/`) and `metrics.json`. Rerunning a command resumes it. A route takes 10-40 minutes.

### 4. Train Your Own Model

The baseline is trained in two steps (about 12 hours and one day on 8 GPUs of 96 GB):

```bash
bash scripts/train_world_model.sh world_model/configs/world_model.yaml   # -> work_dirs/world_model/latest.pt
bash scripts/train_vla.sh safedrive_vla                                  # -> work_dirs/safedrive_vla/safedrive_vla/<timestamp>/
```

To skip the world model, train the VLA with the released one: append `model.world_model.predictor_ckpt=ckpts/safedrive-vla/world_model/latest.pt`. The recipes `baseline_mode` (mode token only) and `baseline` (neither mode token nor world model) are trained the same way. Evaluate a trained model with its epoch checkpoint:

```bash
bash scripts/eval.sh carla_f work_dirs/safedrive_vla/safedrive_vla/<timestamp>/checkpoints/epoch=013.ckpt \
    --routes-dir ../track3/routes/carla_f --output-dir work_dirs/track3/my_model/carla_f
```

### 5. Evaluate Your Own Agent

Any agent for the Bench2Drive leaderboard (a subclass of `leaderboard.autoagents.autonomous_agent.AutonomousAgent`) can be run on the track routes. The language is the only navigation signal; the baseline agents show how an agent obtains it:

- [`team_code/agent_safedrive_carla_f.py`](https://github.com/ASGuard-UCI/safedrive-vla/blob/main/team_code/agent_safedrive_carla_f.py) reads the instructions of the route file and activates each one when its trigger fires (distance traveled or scenario start); the active instruction is in `self.instruction`. [`team_code/agent_safedrive_b2d_c.py`](https://github.com/ASGuard-UCI/safedrive-vla/blob/main/team_code/agent_safedrive_b2d_c.py) does the same for B2D-C.
- The CARLA-F metric compares the driven trajectory with the instructed one, so an agent must save `self.get_metric_info()` every tick to `$SAVE_PATH/<run>/metric_info.json`, as the baseline does in `_log_metric_info` of [`team_code/agent_safedrive.py`](https://github.com/ASGuard-UCI/safedrive-vla/blob/main/team_code/agent_safedrive.py).

Run and score an agent with the tools of the SafeDriveVLA repository:

```bash
python tools/run_distributed_eval.py --routes-dir ../track3/routes/carla_f --output-dir work_dirs/track3/my_agent/carla_f \
    --agent path/to/my_agent.py --agent-config path/to/my_agent_config --gpu-ids 0,1,2,3
python benchmark/metrics/carla_f_metrics.py work_dirs/track3/my_agent/carla_f --routes-dir ../track3/routes/carla_f
python benchmark/metrics/bench2drive_metrics.py work_dirs/track3/my_agent/b2d_c --routes-dir ../track3/routes/b2d_c
```

### 6. Prepare a Submission

*To be announced soon.* See [Submission Format](#-submission-format).

## 🧠 Baseline Models

Two reference baselines generate driving actions from visual observations and language instructions:

| Baseline | Approach |
|:--|:--|
| **SimLingo** | A vision-only closed-loop driving model with language-action alignment that maps camera observations and language instructions to driving actions. |
| **SafeDriveVLA** | Additionally uses explicit driving-mode selection and world-model predictions to handle conflicts between instructions and the traffic scene. |

<p align="center">
  <img src="assets/safedrivevla-overview.png" alt="SafeDriveVLA overview" width="90%" />
</p>

SafeDriveVLA decouples conflict reasoning from action generation:

- **Driving mode.** Every expert frame is relabeled with a discrete driving mode (strict, cautious, or fallback) that states whether the trajectory executes, cautiously follows, or overrides the navigation signal. The model emits this mode token before its actions, so conflict awareness is supervised directly.
- **Navigation-conditioned world-model dreaming.** A frozen latent world model, a V-JEPA 2 encoder with an action-conditioned predictor, rolls the scene forward under the action anchor of the instructed maneuver. The policy reads these predicted world tokens and can see whether the maneuver is feasible before it commits.

The SafeDriveVLA policy builds on InternVL3-1B, emits discrete action tokens from a 2,048-entry motion-primitive codebook, and uses a lightweight path head for lateral control. Implementations are provided in the [SafeDriveVLA repository](https://github.com/ASGuard-UCI/safedrive-vla).

Reference results reported in the [SafeDriveVLA paper](https://safedrive-vla.github.io/SafeDriveVLA/) on the full public benchmark routes are shown below. These are baseline results, not competition submissions.

**CARLA-F** (Navigation Compliance Rate per meta-command, %)

| Baseline | Speed Error ↓ | Turn left | Turn right | Go straight | Left lane | Right lane | Lane follow | Avg. ↑ |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| SimLingo | 1.44 | 83.6 | 80.4 | 45.9 | 0.0 | 0.0 | 63.8 | 52.4 |
| SimLingo-IF | **1.31** | 89.1 | 82.3 | 49.4 | 0.0 | 0.0 | 69.0 | 55.6 |
| SimLingo-Safe | 1.67 | **92.7** | 84.3 | 50.6 | 0.0 | 0.0 | 62.1 | 55.6 |
| **SafeDriveVLA** | 4.28 | **92.7** | **90.2** | **84.7** | **63.6** | **72.4** | **81.0** | **83.0** |

Avg. is weighted by the number of instructions per meta-command and excludes speed. Speed Error is in m/s.

**B2D-C**

| Baseline | DS ↑ | SR (%) ↑ | Collision ↓ | Traffic Violation ↓ | Out of Route ↓ |
|:--|--:|--:|--:|--:|--:|
| SimLingo | 72.8 | 36.7 | 66 | 60 | 18 |
| SimLingo-IF | 56.3 | 12.7 | 166 | 57 | 32 |
| SimLingo-Safe | 72.8 | 38.0 | 60 | 61 | 11 |
| **SafeDriveVLA** | **85.9** | **67.3** | **38** | **9** | **4** |


## 📏 Evaluation

**CARLA-F** evaluates safe instruction following using the per-instruction Navigation Compliance Rate (NCR) and target-speed error. **B2D-C** evaluates safety-critical driving using Driving Score (DS), Success Rate (SR), and counts of collisions, traffic violations, and route departures. Results from the two test sets are reported separately.

| Test set | Metric | Direction | Description |
|:--|:--|:--|:--|
| CARLA-F | **Navigation Compliance Rate (NCR)** | Higher is better | Per-instruction navigation compliance. |
| CARLA-F | **Speed Error (SE)** | Lower is better | Deviation from the instructed target speed, in m/s. |
| B2D-C | **Driving Score (DS)** | Higher is better | Closed-loop driving performance. |
| B2D-C | **Success Rate (SR)** | Higher is better | Route success. |
| B2D-C | **Collisions, traffic violations, route departures** | Lower is better | Counts of safety and route-following failures. |

### 🏁 Ranking Rule

*To be announced soon.*

## 📥 Submission Format

*To be announced soon.* Submission instructions and the full evaluation protocol, including agent packaging, simulation versions, runtime requirements, and the final ranking rule, will be published here and on the [CodaBench Submission & Evaluation page](https://www.codabench.org/competitions/18333/).

## ❓ Frequently Asked Questions

**1. Do I have to use a world model or the SafeDriveVLA architecture?**

No. End-to-end policies, VLA models, world-model approaches, explicit conflict reasoning, and reinforcement learning are all welcome.

**2. Which navigation signal does the agent receive?**

Natural-language instructions only. Route-planner commands, target waypoints, route polylines, scenario definitions, and privileged simulator state must not be fed to any part of the model; see the [navigation signal rule](#-navigation-signal-rule).

## 🔗 Contact and Resources

For technical support, use [GitHub Issues](https://github.com/roboworld2026/track3/issues). For challenge questions, contact [roboworld2026@gmail.com](mailto:roboworld2026@gmail.com). To join the Track 3 WeChat group, scan the [WeChat QR code](https://github.com/roboworld2026/roboworld2026.github.io/blob/main/wechat_track3.JPG).

| Resource | Link |
|:--|:--|
| Official Track 3 Website | [RoboWorld 2026 Track 3: SafeDrive-VLA](https://roboworld2026.github.io/track3) |
| Official Challenge Portal & Registration | [RoboWorld 2026 Registration (Google Form)](https://roboworld2026.github.io/#registration) |
| Official Awards & Recognition | [RoboWorld 2026 Awards](https://roboworld2026.github.io/#awards) |
| Track 1 (WorldNav) Website | [RoboWorld 2026 Track 1: WorldNav](https://roboworld2026.github.io/track1) |
| Track 2 (HA-VLN 2.0) Website | [RoboWorld 2026 Track 2: HA-VLN 2.0](https://roboworld2026.github.io/track2) |
| Associated Workshop | [RoboPAD at NeurIPS 2026](https://robotpad2026.github.io/) |
| CodaBench Competition Portal | [CodaBench #18333](https://www.codabench.org/competitions/18333/) |
| GitHub Repository | [roboworld2026/track3](https://github.com/roboworld2026/track3) |
| Baseline implementation | [SafeDriveVLA repository](https://github.com/ASGuard-UCI/safedrive-vla) |
| Paper | [SafeDriveVLA: Navigation-Conditioned World Model Dreaming for Conflict-Aware End-to-End Autonomous Driving](https://safedrive-vla.github.io/SafeDriveVLA/) |
| Training data | [RenzKa/simlingo on Hugging Face](https://huggingface.co/datasets/RenzKa/simlingo) |
| SimLingo | [Official repository](https://github.com/RenzKa/simlingo) |
| Simulation | [CARLA](https://carla.org/) and [Bench2Drive](https://github.com/Thinklab-SJTU/Bench2Drive) |

## 📄 License and Terms

CARLA, Bench2Drive, SimLingo and its dataset, PDM-Lite, the SafeDriveVLA code and benchmarks, and all other resources retain their upstream licenses. Participation is governed by the Track 3 Terms and Conditions on [CodaBench](https://www.codabench.org/competitions/18333/).

## 📚 Citation

If you use the SafeDriveVLA benchmarks or the SafeDrive-VLA track resources, please cite:

```bibtex
@inproceedings{xie2026safedrivevla,
  title     = {SafeDriveVLA: Navigation-Conditioned World Model Dreaming for Conflict-Aware End-to-End Autonomous Driving},
  author    = {Xie, Shaoyuan and Zhang, Zihan and Wang, Jingxuan and Qu, Jiashu and Liang, Xiaoqing and Kong, Lingdong and Lu, Junchi and Christensen, Henrik I. and Chen, Qi Alfred},
  booktitle = {Conference on Robot Learning (CoRL)},
  year      = {2026}
}

@misc{roboworld2026track3,
  title={Track 3 | SafeDrive-VLA: Towards Safety in Autonomous Driving},
  author={RoboWorld Challenge 2026 Organizers},
  year={2026},
  howpublished={https://roboworld2026.github.io/track3}
}
```

## 🤝 Acknowledgements

SafeDrive-VLA is organized by the RoboWorld Challenge 2026 team as part of an independently organized challenge associated with the [RoboPAD Workshop at NeurIPS 2026](https://robotpad2026.github.io/). We thank the SimLingo authors for the released training data, the PDM-Lite, CARLA, and Bench2Drive teams, and CodaBench for the evaluation infrastructure.
