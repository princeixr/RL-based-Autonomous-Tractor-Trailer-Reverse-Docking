# Trajectory-Aware Reinforcement Learning for Autonomous Tractor–Trailer Reverse Docking

## Project Proposal

**Team size:** Two members  
**Project type:** Simulation, motion planning, control, and reinforcement learning  
**Primary deliverable:** A reproducible simulation in which a tractor–trailer identifies a selected loading-dock goal, plans a reverse maneuver, and parks safely without collision or jackknifing.

## 1. Abstract

Reversing a tractor–trailer into a loading dock is a difficult control problem because the vehicle is nonlinear, nonholonomic, underactuated, and unstable while moving backward. Small steering errors can cause the articulation angle to diverge and lead to jackknifing. This project proposes a modular simulated autonomy system for reverse docking at a logistics service center. A trajectory planner will generate a feasible reference path to a selected dock, and a trajectory-aware reinforcement learning controller will steer the vehicle along that path. A model-based controller will provide a conventional baseline and, if time permits, expert demonstrations for imitation learning.

Development will proceed in stages: mathematical modeling, a lightweight two-dimensional simulator, baseline control, reinforcement learning, path planning, and integration into a three-dimensional simulator. Ground-truth vehicle and dock poses will be used first so that planning and control can be validated independently of perception. Simulated LiDAR mapping, localization, and camera-based dock-number recognition will be treated as later integration or stretch objectives. Performance will be measured over randomized scenarios using parking success, collision and jackknife rates, final pose error, maneuver time, steering smoothness, and computation time.

## 2. Motivation

Loading-dock parking is repetitive, safety-critical, and challenging even for experienced drivers. An autonomous system must coordinate perception, path planning, and control while respecting the geometry and instability of an articulated vehicle. Reinforcement learning may produce adaptive controllers, but learning the complete task directly from raw sensor data would require extensive training and make failures difficult to diagnose.

This project therefore uses a hybrid, modular approach. Classical geometry and vehicle models provide structure, while reinforcement learning handles the nonlinear feedback-control problem. Each subsystem will expose a clear interface so it can be tested, replaced, and improved independently.

## 3. Problem Statement

Given:

- A tractor connected to one conventional semitrailer
- The vehicle's estimated configuration
- A map containing dock boundaries and static obstacles
- A selected loading-dock pose

the system must generate and execute a low-speed maneuver that places the trailer inside the target dock while:

- Avoiding collision with dock walls and obstacles
- Keeping the articulation angle within a safe range
- Respecting steering-angle and steering-rate limits
- Reaching specified final position and orientation tolerances
- Producing smooth, physically plausible control commands

The central research question is:

> Can a PPO controller using trajectory-relative preview states reliably reverse a tractor–trailer into a loading dock, and how does it compare with a model-based controller under randomized starting poses, vehicle-model variation, and observation noise?

## 4. Hypotheses

1. A trajectory-relative observation containing lateral error, heading errors, articulation angle, and preview information will learn faster and generalize better than an observation based only on global coordinates.
2. A nonlinear model predictive controller (NMPC) will provide strong safety and accuracy under nominal model conditions.
3. A trained PPO policy may require less online computation and may be more tolerant of moderate model variation than a fixed model-based controller.
4. A hybrid architecture—classical task and path planning followed by learned trajectory tracking—will be more reliable and interpretable than an end-to-end sensor-to-steering policy.

## 5. Objectives

### 5.1 Primary objectives

1. Implement and validate a low-speed tractor–trailer kinematic model.
2. Build a lightweight 2D environment for rapid development and RL training.
3. Implement a conventional trajectory-tracking baseline, preferably NMPC.
4. Implement a trajectory-aware PPO controller for reverse path following.
5. Generate a feasible reference maneuver from an approach pose to a selected dock.
6. Build a logistics-yard scene and articulated vehicle in MuJoCo or another suitable 3D simulator.
7. Compare the learned and conventional controllers under identical randomized test conditions.

### 5.2 Secondary objectives

1. Test robustness to observation noise, actuator delay, and changes in trailer geometry.
2. Add static-obstacle representation and collision-aware planning.
3. Provide a perception interface that accepts an estimated vehicle pose, map, and selected dock pose.

### 5.3 Stretch objectives

1. Simulated LiDAR occupancy mapping and localization
2. Camera-based loading-door number detection using tags or OCR
3. Imitation or offline reinforcement learning from baseline-controller demonstrations
4. Automatic selection among multiple docks
5. Forward repositioning when a reverse-only maneuver is infeasible
6. Dynamic obstacles

## 6. Scope

### 6.1 Minimum viable project

The minimum successful project will include:

- One tractor and one conventional semitrailer
- Low-speed operation on level ground
- A known static logistics-yard map
- A known target dock pose
- Simulator ground-truth localization
- Fixed or bounded reverse velocity
- Steering or steering rate as the primary control action
- Static dock walls and obstacles
- Collision and jackknife detection
- At least one predefined or automatically generated reference path
- One model-based or classical baseline controller
- One trained PPO controller
- Randomized evaluation with quantitative results
- A final 3D simulation and demonstration video

### 6.2 Explicit non-goals for the core project

The core project will not attempt to:

- Learn steering directly from raw camera images or point clouds
- Train a new visual recognition model from scratch
- Model high-speed tire, suspension, or powertrain dynamics
- Handle pedestrians, forklifts, or other dynamic traffic
- Control multiple trailers
- Demonstrate real-world deployment or safety certification
- Reproduce a full commercial autonomous-driving stack

These exclusions prevent integration complexity from overwhelming the main research question.

## 7. Background and Relation to the Repository Papers

### 7.1 Trajectory-state model-based reinforcement learning

The paper *Trajectory State Model-based Reinforcement Learning for Truck-trailer Reverse Driving* motivates using path-relative errors and preview reference points as the RL state. Its main value to this project is the separation of trajectory generation from learned trajectory tracking. It also establishes PPO and LQR as relevant comparison methods. The paper is simulation-only and omits several reproducibility details, so this project will define the observation, action, reward, constraints, and evaluation protocol explicitly.

### 7.2 Nonlinear MPC local planning

The paper *A Non-linear MPC Local Planner for Tractor-Trailer Vehicles in Forward and Backward Maneuvering* demonstrates a useful development sequence: first implement a controller in a headless Python simulation, then integrate it into a physics simulator with sensors. It treats obstacle avoidance, input limits, and jackknifing as constraints. This project adopts that staged process, although the complete ROS/Autoware integration is outside the minimum scope.

### 7.3 Hierarchical graph search and reinforcement learning

The paper *A Hierarchical Approach for Tractor-trailer Motion Planning Using Graph Search and Reinforcement Learning* separates long-horizon route selection from short-horizon dynamically feasible trajectory generation. It reinforces the decision not to use one end-to-end policy for the entire logistics yard. Its reference-line graph is a possible extension if multiple lanes and docks are added.

### 7.4 Imitation and offline reinforcement learning

The paper *Edge-based Imitation Learning for Autonomous Tasks: A Case Study on Tractor-Trailer Positioning* shows how an expert policy can generate demonstrations for behavioral cloning, IQL, or TD3-BC. Its vehicle uses a steerable drawbar trailer rather than the conventional semitrailer planned here, but its demonstration-learning workflow remains relevant as a stretch objective.

## 8. Proposed System Architecture

```text
Camera ----> Dock identifier/OCR ----> Selected dock ID and pose
                                         |
LiDAR -----> Mapping/localization --------+
                                         v
                              Task and goal generator
                                         |
                                         v
                                Global/path planner
                                         |
                              Reference path and preview
                                         |
                                         v
                         PPO controller or NMPC baseline
                                         |
                                         v
                                Safety supervisor
                                         |
                          Steering and velocity commands
                                         |
                                         v
                           Tractor-trailer simulator
```

During early development, the camera, LiDAR, and localization modules will be replaced with simulator ground truth. Their output interfaces will nevertheless be defined from the start:

```text
VehicleState:
    tractor_pose = (x, y, heading)
    trailer_heading
    articulation_angle
    steering_angle
    velocity

DockGoal:
    dock_id
    target_pose = (x, y, heading)
    dock_width
    dock_depth

EnvironmentMap:
    obstacle polygons or occupancy grid
```

## 9. Technical Method

### 9.1 Tractor–trailer model

The initial environment will use a low-speed kinematic bicycle model for the tractor and a kinematic trailer model. A representative state is:

\[
s=[x_t,y_t,\theta_t,\theta_r,\delta,v]
\]

where \(\theta_t\) and \(\theta_r\) are the tractor and trailer headings. The articulation angle is:

\[
\phi=\operatorname{wrap}(\theta_t-\theta_r)
\]

Initial assumptions are:

- Level, high-friction ground
- Low speed
- Negligible lateral tire slip
- Known vehicle dimensions
- Rigid tractor and trailer bodies
- Bounded steering angle and steering rate

The 2D model will be verified before it is used for controller training.

### 9.2 Reference trajectory and planning

Development will begin with hand-authored straight and curved reference paths. Later versions may use:

1. Reeds–Shepp paths as geometric references
2. Hybrid A* with tractor–trailer state propagation
3. A reference-line graph for a multi-dock yard

A Reeds–Shepp path will be treated as a guide rather than a guarantee of trailer feasibility because it does not by itself model trailer articulation.

### 9.3 Conventional controller

The preferred baseline is nonlinear MPC implemented with CasADi and IPOPT. Its objective will penalize lateral and heading error, articulation, steering effort, and steering-rate variation:

\[
J=\sum_{k=0}^{N-1}
\left(
w_y e_{y,k}^2+
w_r e_{\theta_r,k}^2+
w_t e_{\theta_t,k}^2+
w_\phi \phi_k^2+
w_\delta \delta_k^2+
w_{\Delta\delta}\Delta\delta_k^2
\right)
\]

The optimization will enforce steering, steering-rate, articulation, and vehicle-dynamics constraints. If full NMPC cannot be completed within the schedule, a geometric feedback or LQR controller will be retained as the minimum baseline.

### 9.4 Reinforcement-learning formulation

The initial PPO controller will use a fixed reverse speed and output a bounded steering-rate command:

\[
a_t=\dot{\delta}_t
\]

The proposed observation is:

\[
o_t=[e_y,e_{\theta_r},e_{\theta_t},\phi,\dot{\phi},\delta,v,d_{goal},p_1,\ldots,p_N]
\]

where \(p_1,\ldots,p_N\) represent preview-point errors or local path curvature. All quantities will be normalized, and angular differences will be wrapped consistently.

A candidate reward is:

\[
r_t=
w_p\Delta d_{progress}
-w_y e_y^2
-w_r e_{\theta_r}^2
-w_t e_{\theta_t}^2
-w_\phi P_{jackknife}
-w_s\dot{\delta}^2
-w_c I_{collision}
-w_{time}
\]

Successful parking will receive a terminal bonus. Collision and severe articulation will terminate the episode. Safety-critical limits will also be checked outside the reward function so they cannot be ignored through reward tradeoffs.

### 9.5 Three-dimensional simulation

MuJoCo is the preferred simulator because the primary research focus is control and reinforcement learning. The model will include:

- Separate tractor and trailer rigid bodies
- A hitch yaw joint
- Front-wheel steering
- Wheel or body actuation sufficient for low-speed motion
- Steering position and rate limits
- Collision geometry for the vehicle, docks, and obstacles
- Cameras and range sensors only after control integration succeeds

Gazebo is an alternative if ROS and realistic sensor integration become the dominant project objective. The team will not maintain both simulator stacks.

### 9.6 Perception integration

Perception will be added in three levels:

1. **Ground truth:** simulator supplies vehicle and dock poses.
2. **Noisy observations:** controlled noise, latency, and dropped measurements are applied to ground truth.
3. **Simulated sensors:** LiDAR produces a map or obstacle representation, and the camera identifies a dock marker or number.

For a course-scale implementation, dock identification may use AprilTags, ArUco markers, or existing OCR rather than a newly trained vision network.

## 10. Incremental Development Checkpoints

Each checkpoint has a concrete exit condition. Later work should not depend on a checkpoint that has not passed.

### Checkpoint 1: Task specification and interfaces

Deliverables:

- Vehicle and dock dimensions
- State, action, and coordinate conventions
- Success, collision, and jackknife definitions
- Module interfaces and configuration format

Exit condition: both team members can construct the same scenario from the written specification without relying on undocumented assumptions.

### Checkpoint 2: Verified 2D vehicle model

Deliverables:

- Kinematic update function
- 2D vehicle visualization
- Tests for straight and constant-steering motion
- Collision and articulation calculations

Exit condition: timestep-refinement tests are stable, the hitch geometry remains connected, and expected maneuvers have the correct direction and curvature.

### Checkpoint 3: Basic reverse stabilization

Deliverables:

- Straight reference path
- Hand-designed or linear baseline controller
- Random initial articulation tests

Exit condition: the trailer converges toward a straight reference line from a documented range of initial states without jackknifing.

### Checkpoint 4: Trajectory tracking and NMPC baseline

Deliverables:

- Path-relative error computation
- Preview-point representation
- Curved reference paths
- NMPC or fallback baseline

Exit condition: the baseline follows the test path and reaches the docking tolerance in at least 90% of nominal validation cases.

### Checkpoint 5: PPO environment and training

Deliverables:

- Gymnasium-compatible environment
- Reward and termination definitions
- Reproducible training configuration
- Saved policy checkpoints and learning curves

Exit condition: PPO exceeds a simple steering baseline on held-out initial poses and completes nominal docking without persistent reward exploitation.

### Checkpoint 6: Path-planning integration

Deliverables:

- Start-to-dock reference generation
- Collision checking along the reference
- Planner/controller interface

Exit condition: the same controller can receive multiple generated paths without controller-specific path modifications.

### Checkpoint 7: MuJoCo integration

Deliverables:

- Articulated 3D vehicle
- Logistics-yard scene
- Controller adapter
- State and action comparison against the 2D environment

Exit condition: predefined action sequences behave consistently in 2D and MuJoCo, and at least one complete reverse-docking maneuver succeeds in 3D.

### Checkpoint 8: Evaluation and optional perception

Deliverables:

- Randomized evaluation suite
- Baseline-versus-PPO plots
- Robustness experiments
- Optional dock recognition or LiDAR demonstration

Exit condition: results can be regenerated from documented commands and include both successful and failed trials.

## 11. Two-Member Work Division

The work is divided by subsystem ownership while preserving shared review and integration. Each member leads one critical path and reviews the other. This avoids duplicate effort without creating knowledge silos.

### Member A: Vehicle Modeling, Reference Generation, and Baseline Control Lead

Primary responsibilities:

- Define coordinate frames and vehicle geometry
- Implement and validate the 2D kinematic model
- Implement collision and jackknife checks
- Implement path-relative error and preview-point calculations
- Create predefined docking paths and a simple reference generator
- Implement a reliable classical controller first; add NMPC only if the core baseline is ready early
- Define model-based constraints and safety-supervisor rules
- Lead quantitative controller-baseline evaluation

Secondary responsibilities:

- Review PPO observation and reward design
- Help diagnose whether RL failures originate in dynamics, geometry, or training
- Document mathematical models and planning algorithms

### Member B: Reinforcement Learning, 3D Simulation, and Integration Lead

Primary responsibilities:

- Wrap the verified 2D model as a Gymnasium environment
- Implement PPO training, checkpointing, logging, and evaluation
- Design normalization, curriculum, reward, and domain randomization
- Build the MuJoCo articulated vehicle and logistics-yard scene
- Implement the controller-to-MuJoCo adapter
- Add controlled observation noise after the nominal controller succeeds
- Add sensor interfaces only as a stretch task after the evaluation pipeline is frozen
- Lead experiment automation and demonstration-video generation

Secondary responsibilities:

- Review model tests and baseline-controller behavior
- Document RL configurations, simulator assets, and reproducibility steps

### Shared responsibilities

- Agree on state/action/interface definitions before implementation
- Review every subsystem through small test scenarios
- Maintain the integration branch and resolve interface mismatches together
- Define evaluation scenarios and success thresholds
- Run final experiments and interpret results
- Write the report and prepare the presentation

### Ownership and review matrix

| Component | Lead | Reviewer | Integration dependency |
|---|---|---|---|
| Requirements and interfaces | Shared | Shared | None |
| Kinematic model | Member A | Member B | First dependency for both workstreams |
| Geometry/collision checks | Member A | Member B | Used by training and evaluation |
| Classical baseline; optional NMPC | Member A | Member B | Requires verified model |
| Reference-path generation | Member A | Member B | PPO starts on fixed paths; automatic planning is optional |
| Gymnasium environment | Member B | Member A | Requires model API |
| PPO training | Member B | Member A | Uses fixed paths before planner completion |
| MuJoCo vehicle and yard | Member B | Member A | Can proceed beside controller development |
| 2D-to-3D controller adapter | Member B | Member A | Requires stable controller interface |
| Safety supervisor | Member A | Member B | Integrated with both controllers |
| Perception extensions | Member B | Member A | Stretch work only after Week 5 evaluation freeze |
| Experiment design | Shared | Shared | Requires both controllers |
| Report and presentation | Shared by section | Cross-reviewed | Uses frozen experimental results |

## 12. Parallel Work Plan

The project has six weeks. The key efficiency strategy is to freeze interfaces during the first two days, maintain parallel workstreams, and integrate at the end of every week. PPO will begin on fixed paths instead of waiting for an automatic planner, and MuJoCo scene construction will begin while the 2D controller work is underway.

| Period | Member A | Member B | Required checkpoint |
|---|---|---|---|
| Week 1 | Freeze geometry and conventions; implement kinematics, articulation, collision, and success checks | Create the repository/configuration structure, Gymnasium skeleton, plotting tools, and a basic MuJoCo vehicle/yard shell | By Day 2, freeze state/action/configuration interfaces. By week end, scripted actions pass straight and constant-steering tests in 2D. |
| Week 2 | Implement path-relative errors, fixed docking references, safety rules, and a simple classical tracking controller | Complete the Gymnasium environment, logging, randomized resets, and PPO smoke tests; continue the MuJoCo model | Baseline completes straight reverse stabilization and follows at least one curved reference; PPO can run complete episodes. |
| Week 3 | Improve the baseline and add a simple start-to-dock reference generator; attempt NMPC only if the fallback baseline already passes | Train and tune PPO on fixed paths; validate reward behavior; finish the controllable MuJoCo vehicle | Run the first fair 2D PPO-versus-baseline comparison on held-out initial poses. |
| Week 4 | Finalize collision/jackknife safety checks and validate 2D-to-3D state conventions | Connect both controllers to MuJoCo and tune only the simulator adapter or documented controller parameters | Complete one end-to-end reverse dock in MuJoCo with the baseline and attempt it with PPO; compare fixed-action rollouts across simulators. |
| Week 5 | Run the baseline evaluation batch and analyze failure categories | Run PPO evaluation, add one controlled robustness condition, and capture demonstrations | Freeze code, random seeds, evaluation scenarios, metrics, and plots by the end of the week. |
| Week 6 | Write the modeling, safety, baseline, and results sections | Write the RL, simulation, and reproducibility sections; produce the final video | Cross-review the report, reproduce selected runs, prepare the presentation, and submit the final artifacts. |

### Six-week decision gates

- **End of Week 1:** If the model is not verified, both members stop feature work and fix it.
- **End of Week 2:** If the baseline cannot track a fixed path, automatic planning is removed from scope.
- **End of Week 3:** If PPO has not learned a useful policy, simplify to fixed speed, fixed paths, and a curriculum; do not add sensors.
- **End of Week 4:** If transfer to MuJoCo is unreliable, preserve the 2D quantitative study and use one validated scripted or baseline 3D demonstration.
- **Start of Week 5:** No new core features. Only evaluation, bug fixes, documentation, and presentation work are allowed.

Camera dock recognition, LiDAR mapping, imitation learning, dynamic obstacles, and a hierarchical multi-dock planner are stretch goals and are not scheduled into the six-week critical path.

## 13. Integration Practices

To minimize integration time:

1. Maintain one canonical configuration file for vehicle dimensions, limits, timestep, dock geometry, and success tolerances.
2. Define a stable environment API before parallel development begins.
3. Keep controller inputs in path-relative form so the same controller works in 2D and 3D.
4. Use prerecorded states and paths as fixtures when another subsystem is unavailable.
5. Add automated smoke tests for dynamics, collision, angle wrapping, and controller I/O.
6. Integrate at least once per week rather than waiting until all modules are complete.
7. Freeze evaluation seeds and scenarios before final tuning.
8. Record dependency versions, random seeds, training configurations, and model checkpoints.
9. Require the non-owner to reproduce each major milestone before it is declared complete.

A suggested repository structure is:

```text
project/
├── configs/
├── docs/
├── models/
│   ├── kinematics.py
│   └── geometry.py
├── planning/
├── control/
│   ├── baseline/
│   └── rl/
├── environments/
│   ├── gym_env/
│   └── mujoco/
├── perception/
├── evaluation/
├── tests/
├── scripts/
└── results/
```

## 14. Evaluation Plan

At least 100 held-out trials per condition will be used where computation permits. Both controllers will receive identical initial states, target docks, vehicle parameters, and observation conditions.

### 14.1 Primary metrics

- Docking success rate
- Collision rate
- Jackknife rate
- Final lateral error
- Final longitudinal error
- Final trailer-heading error
- Maximum absolute articulation angle
- Maneuver duration
- Path length
- Steering smoothness or accumulated steering-rate cost
- Mean and worst-case controller computation time

### 14.2 Proposed comparisons

1. PPO versus NMPC or the selected classical baseline
2. Global-coordinate PPO versus trajectory-relative PPO
3. PPO without preview points versus PPO with preview points
4. Perfect state observations versus noisy observations
5. Nominal trailer geometry versus unseen trailer dimensions
6. Fixed starting pose versus randomized approach poses

### 14.3 Success criteria

The minimum final system should:

- Complete at least 90% of nominal held-out docking scenarios
- Produce no collision in successful trials
- Keep articulation below the defined safety threshold
- Meet the documented final position and heading tolerances
- Demonstrate at least one reproducible complete maneuver in the 3D simulator
- Report failures rather than excluding them from the results

The exact numerical docking tolerances will be frozen during Checkpoint 1 based on vehicle and dock dimensions.

## 15. Risks and Mitigations

| Risk | Likely effect | Mitigation |
|---|---|---|
| Incorrect kinematic signs or frames | Neither controller learns or tracks correctly | Unit tests, plotted fixed-action rollouts, and timestep refinement before RL |
| NMPC solver instability | Baseline misses schedule | Use shorter horizons, warm starts, multiple shooting, or retain an LQR/geometric fallback |
| Sparse reward or reward exploitation | PPO fails or learns unsafe shortcuts | Curriculum, progress shaping, external safety termination, and trajectory inspection |
| 2D-to-3D dynamics mismatch | Trained policy fails in MuJoCo | Validate identical action sequences, randomize model parameters, and fine-tune only after validation |
| Simulator setup consumes excessive time | Core experiments remain incomplete | Use simple collision meshes and ground-truth state; postpone detailed visuals and sensors |
| Perception errors dominate control results | Research question becomes unclear | Evaluate perfect state, controlled noise, and full perception as separate experiment levels |
| Work becomes siloed between members | Integration delay and low shared understanding | Lead/reviewer ownership, weekly integration, and cross-reproduction of milestones |
| Too many objectives | Incomplete final system | Protect the minimum scope and remove stretch goals in the stated order |

## 16. Expected Contributions

The project is expected to produce:

1. A reproducible staged environment for tractor–trailer reverse docking.
2. A clear trajectory-relative RL state representation for articulated reverse control.
3. A controlled comparison between PPO and a model-based baseline.
4. An analysis of robustness to initial-state, observation, and vehicle-parameter variation.
5. A modular path from ground-truth control experiments toward LiDAR- and camera-assisted docking.

## 17. Final Deliverables

- Source code and configuration files
- Verified 2D tractor–trailer environment
- Baseline controller
- PPO training and evaluation pipeline
- Saved trained policy and training curves
- Reference-path planner
- MuJoCo or equivalent 3D logistics-yard simulation
- Randomized evaluation dataset and plots
- Demonstration video including successes and representative failures
- Final technical report
- Presentation describing the design, experiments, results, limitations, and future work

## 18. Planned Cut Order

If schedule pressure occurs, features will be removed in this order:

1. Dynamic obstacles
2. Full camera OCR, replaced by an AprilTag/ArUco marker
3. LiDAR mapping and localization, replaced by noisy ground truth
4. Imitation/offline reinforcement learning
5. Multi-dock automatic route selection
6. Automatic planning, replaced by predefined reference paths
7. Full NMPC, replaced by a documented classical tracking baseline

The following will not be cut: the verified vehicle model, collision and jackknife checks, a baseline controller, PPO, randomized evaluation, and a complete reverse-docking demonstration.
