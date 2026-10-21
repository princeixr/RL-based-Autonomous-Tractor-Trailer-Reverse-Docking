# Trajectory-Aware Reinforcement Learning for Autonomous Tractor-Trailer Reverse Docking

**Team:** Two-member course project  
**Area:** Reinforcement learning, motion planning, and autonomous vehicle simulation

## Abstract

Reversing a tractor-trailer into a loading dock is a challenging control problem because the vehicle is nonlinear, nonholonomic, underactuated, and unstable while moving backward. Small steering errors can cause the articulation angle to grow and lead to jackknifing. This project proposes a modular simulated autonomy system that plans and executes a safe reverse-docking maneuver at a logistics service center. A path planner will produce a reference trajectory to a selected loading door, and a trajectory-aware Proximal Policy Optimization (PPO) controller will steer the vehicle along it. A model-based controller will provide a conventional baseline. The system will first be developed in a lightweight two-dimensional environment and then transferred to a three-dimensional MuJoCo simulation. Performance will be evaluated over randomized scenarios using docking success, collision and jackknife rates, final pose error, maneuver time, steering smoothness, and controller computation time.

## Problem and Research Question

The system receives the tractor and trailer configuration, a static map, and the pose of a selected loading dock. It must place the trailer within a specified position and orientation tolerance while avoiding obstacles, respecting steering limits, and maintaining a safe articulation angle. The central research question is: **Can a PPO controller using trajectory-relative preview information reliably reverse a tractor-trailer into a dock, and how does it compare with a model-based controller under changes in starting pose, vehicle parameters, and observation noise?**

We hypothesize that trajectory-relative observations will be easier to learn from than raw global coordinates. The model-based controller is expected to provide strong nominal safety and accuracy, while PPO may offer fast online control and greater tolerance to moderate model variation after suitable training.

## Objectives and Scope

The project has five primary objectives:

1. Implement and validate a low-speed tractor-trailer kinematic model.
2. Develop reference-path generation and path-relative error measurements.
3. Implement a conventional trajectory-tracking baseline, preferably nonlinear model predictive control (NMPC).
4. Train a PPO controller for reverse trajectory following and docking.
5. Integrate the planner and controllers with a 3D logistics-yard simulation and compare them quantitatively.

The core scope includes one tractor, one conventional semitrailer, static obstacles, a known map, a known target dock pose, and low-speed operation. Simulator ground truth will initially provide localization so that planning and control can be evaluated independently. Simulated LiDAR mapping and camera-based dock-number recognition are extensions rather than core requirements. Dynamic traffic, multiple trailers, high-speed dynamics, and an end-to-end sensor-to-steering policy are outside the core scope.

## Proposed Method

Development will begin with a Python/Gymnasium-style 2D environment. The vehicle state will include tractor position and heading, trailer heading, articulation angle, steering angle, and velocity. Collision, jackknife, and parking-success checks will be implemented before controller training. Early tests will cover straight reversing, constant-steering motion, and recovery from small initial articulation angles.

The planner will initially supply predefined straight and curved paths, followed by a Reeds-Shepp or Hybrid A*-based reference generator if time permits. Because a car-like path does not guarantee a safe trailer articulation history, all generated paths will be checked through the tractor-trailer model.

The PPO observation will emphasize trailer lateral error, truck and trailer heading errors, articulation angle, steering state, distance to the goal, and several preview points along the path. The action will be a bounded steering or steering-rate command at a fixed low reverse speed. The reward will combine progress, tracking accuracy, steering smoothness, successful docking, collision avoidance, and jackknife prevention. Safety limits will also be enforced by termination or a separate supervisor rather than only through reward penalties.

The conventional baseline will minimize tracking, articulation, and steering costs while respecting vehicle constraints. After validation in 2D, both controllers will be connected through a common interface to the same articulated MuJoCo vehicle and logistics-yard scene.

<!-- PAGE BREAK -->

## Two-Member Work Plan

Work will be divided by subsystem ownership, with the other member serving as reviewer. This permits parallel progress without creating knowledge silos.

**Member A - Modeling, Reference Generation, and Baseline Control**

- Define coordinate frames, geometry, constraints, and success criteria.
- Implement and test the 2D vehicle model, collision detection, and jackknife checks.
- Develop fixed docking references, path-relative errors, and a simple reference generator.
- Implement a reliable classical controller; attempt NMPC only after the fallback baseline works.
- Lead baseline evaluation and document the mathematical model.

**Member B - Reinforcement Learning, 3D Simulation, and Integration**

- Build the Gymnasium environment around the verified model.
- Implement PPO training, logging, checkpointing, and domain randomization.
- Build the articulated MuJoCo vehicle and logistics-yard scene.
- Integrate both controllers with the 3D simulator.
- Lead experiment automation, visualization, and 2D-to-3D integration.

Both members will agree on interfaces early, review each other's components, integrate weekly, and jointly run the final experiments and demonstration.

## Milestones and Schedule

| Period | Main outcome |
|---|---|
| Week 1 | Freeze interfaces; validate kinematics, geometry, collision, articulation, and scripted 2D motion. Start the Gymnasium and MuJoCo shells in parallel. |
| Week 2 | Complete fixed-path tracking with a classical controller and make the PPO environment run full randomized episodes. |
| Week 3 | Train PPO on fixed paths, finish the controllable MuJoCo vehicle, and run the first fair 2D controller comparison. |
| Week 4 | Integrate both controllers with MuJoCo, compare fixed-action rollouts across simulators, and complete the first 3D reverse dock. |
| Week 5 | Freeze features and run held-out baseline, PPO, and one robustness experiment using fixed seeds and metrics. |
| Week 6 | Analyze failures, finalize plots and video, cross-review the report, reproduce selected runs, and prepare the presentation. |

Each week ends with an integration checkpoint. Automatic planning and sensors will be removed if the fixed-path baseline is not complete by Week 2. No new core features will be added after Week 4.

## Evaluation

The controllers will be evaluated on at least 100 held-out trials per condition where computation permits. Identical starting states and target docks will be used for both methods. Primary metrics are docking success rate, collision rate, jackknife rate, final lateral and longitudinal error, trailer-heading error, maximum articulation angle, maneuver time, path length, steering smoothness, and control computation time.

Experiments will compare PPO with the conventional baseline, global-coordinate observations with trajectory-relative observations, and perfect state information with noisy observations. Additional tests will vary starting pose and trailer geometry. Failed trials will be reported and categorized rather than excluded.

The minimum success target is at least 90% completion in nominal held-out scenarios, no collision during successful trials, compliance with the articulation limit, and a reproducible complete docking maneuver in the 3D simulator.

## Expected Outcomes and Deliverables

The project will produce a verified 2D environment, path planner, conventional controller, trained PPO policy, articulated 3D simulation, evaluation suite, quantitative comparison, and demonstration video. Its principal contribution will be an interpretable evaluation of trajectory-aware RL for articulated reverse docking.

If schedule pressure occurs, perception and advanced planning will be removed before the core controller comparison and 3D reverse-docking demonstration.

## Selected References

1. H. Yan et al., "Trajectory State Model-based Reinforcement Learning for Truck-trailer Reverse Driving," ICRCA, 2024.
2. B. Moradi and M. Mehrandezh, "A Non-linear MPC Local Planner for Tractor-Trailer Vehicles in Forward and Backward Maneuvering," arXiv:2212.11427, 2022.
3. H. Ma et al., "A Hierarchical Approach for Tractor-trailer Motion Planning Using Graph Search and Reinforcement Learning," ECC, 2025.
4. C. Menz and A. Wenzel, "Edge-based Imitation Learning for Autonomous Tasks: A Case Study on Tractor-Trailer Positioning," at-Automatisierungstechnik, 2026.
