# Two-Stage PID Control Design Proposal

## Overview
Added new parameters to implement two-stage temperature control for faster thermal cycling with stable settling.

## New Parameters Added to Profile Structure

### Control Enable
- **`pid_two_stage_enable`**: `true/false` - Enables two-stage PID control

### Approach Phase (Aggressive Control)
- **`pid_approach_phase`**: Object containing aggressive PID settings used until temperature is within the trigger delta
  - **`pid_kp`**: `1.5` - Higher proportional gain for faster response
  - **`pid_ki`**: `0.08` - Moderate integral gain
  - **`pid_kd`**: `0.05` - Small derivative gain to prevent overshoot
  - **`pid_sp_rate_limit`**: `5.0` - Fast setpoint changes allowed
  - **`pid_max_offset`**: `10.0` - Higher maximum offset for aggressive control

### Stabilization Phase (Conservative Control)
- **`pid_stabilization_phase`**: Object containing conservative PID settings used once within trigger delta
  - **`pid_kp`**: `0.8` - Lower proportional gain for stability
  - **`pid_ki`**: `0.03` - Lower integral gain to prevent windup
  - **`pid_kd`**: `0.1` - Higher derivative gain for damping
  - **`pid_sp_rate_limit`**: `1.0` - Slower setpoint changes for stability
  - **`pid_max_offset`**: `6.0` - Lower maximum offset for fine control

### Trigger and Timing Parameters
- **`stabilization_trigger_delta`**: `2.0` - Switch to stabilization phase when within ±2.0°C of target
- **`stabilization_time_required`**: `45` - Seconds that must be stable before proceeding
- **`stabilization_consecutive_readings`**: `10` - Number of consecutive readings within tolerance required

## Control Logic Flow

1. **Start**: Use approach phase PID parameters
2. **Monitor**: Check if current temperature is within `±stabilization_trigger_delta` of target
3. **Switch**: When within delta, switch to stabilization phase PID parameters
4. **Stabilize**: Wait for `stabilization_time_required` seconds with `stabilization_consecutive_readings` within tolerance
5. **Complete**: Proceed to next step

## Benefits

- **Faster Approach**: Aggressive PID gets to temperature quickly
- **Stable Settling**: Conservative PID prevents overshoot and oscillation
- **Configurable**: All parameters can be tuned per step
- **Backward Compatible**: Existing single-stage PID still works when `pid_two_stage_enable` is false

## Implementation Requirements

The thermal cycle control code will need to:
1. Monitor current vs target temperature
2. Track which phase is active
3. Switch PID parameters when trigger conditions are met
4. Track stabilization time and consecutive readings
5. Only proceed to next step when fully stabilized

## Example Values Used

- **Approach Phase**: Fast response (kp=1.5, rate_limit=5.0)
- **Stabilization Phase**: Stable response (kp=0.8, rate_limit=1.0)
- **Trigger**: ±2.0°C (matches existing target_temp_delta)
- **Stabilization**: 45 seconds with 10 consecutive good readings
