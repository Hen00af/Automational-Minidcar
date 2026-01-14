"""Integration test: Sensor-based wall-following with AutoCarMove.

This script demonstrates how to use AutoCarMove with sensor-based
wall-following logic using P-control.
"""
from __future__ import annotations

import logging
import sys
import time
from pathlib import Path
from typing import Tuple

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from auto_car_if.actuation.motor_driver import CarDriver
from test_move.actuation.auto_car_move import AutoCarMove

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_sensor_distances() -> Tuple[float, float, float]:
    """Read distance values from sensors (left, front, right).
    
    This is a placeholder function. In a real implementation, this would
    read from actual VL53L0X or ultrasonic sensors.
    
    Returns:
        Tuple of (left_distance_cm, front_distance_cm, right_distance_cm)
        Returns dummy values for testing.
    """
    # TODO: Replace with actual sensor reading
    # For now, return dummy values simulating a wall-following scenario
    left_dist = 30.0   # cm - left wall distance
    front_dist = 50.0  # cm - front obstacle distance
    right_dist = 25.0  # cm - right wall distance
    
    return (left_dist, front_dist, right_dist)


def wall_following_control(
    left_dist: float,
    front_dist: float,
    right_dist: float,
    kp: float = 0.5,
    target_distance: float = 25.0,
    min_front_distance: float = 20.0,
) -> Tuple[float, float, bool]:
    """Calculate steering and speed using wall-following P-control.
    
    Wall-following logic:
    - Follows the right wall (keeps right_dist close to target_distance)
    - If front obstacle is too close, returns stop flag
    - Uses P-control to adjust steering based on error
    
    Args:
        left_dist: Distance to left wall in cm
        front_dist: Distance to front obstacle in cm
        right_dist: Distance to right wall in cm
        kp: Proportional gain for P-control (default: 0.5)
        target_distance: Target distance to right wall in cm (default: 25.0)
        min_front_distance: Minimum safe front distance in cm (default: 20.0)
        
    Returns:
        Tuple of (steering_intensity, speed, should_stop)
        - steering_intensity: 0.0-1.0 (0=straight, 1=max turn)
        - speed: 0.0-1.0 (0=stop, 1=max speed)
        - should_stop: True if emergency stop is needed
    """
    # Emergency stop if front obstacle is too close
    if front_dist < min_front_distance:
        logger.warning(f"Front obstacle too close: {front_dist:.1f}cm < {min_front_distance:.1f}cm")
        return (0.0, 0.0, True)
    
    # Calculate error: positive means too close to right wall (need to turn left)
    # negative means too far from right wall (need to turn right)
    error = right_dist - target_distance
    
    # P-control: steering intensity proportional to error
    # Normalize error to steering intensity (max error = 20cm -> max intensity = 1.0)
    max_error = 20.0  # cm
    steering_intensity = abs(error) / max_error
    steering_intensity = min(1.0, steering_intensity)  # Clamp to [0.0, 1.0]
    
    # Base speed (reduce if front is getting close)
    base_speed = 0.4
    if front_dist < 40.0:
        # Slow down as front obstacle approaches
        speed = base_speed * (front_dist / 40.0)
    else:
        speed = base_speed
    
    # Determine turn direction based on error sign
    # error > 0: too far from right wall -> turn right
    # error < 0: too close to right wall -> turn left
    # error = 0: perfect distance -> go straight
    
    logger.debug(
        f"Wall-following: left={left_dist:.1f}cm, front={front_dist:.1f}cm, "
        f"right={right_dist:.1f}cm, error={error:.1f}cm, "
        f"intensity={steering_intensity:.3f}, speed={speed:.3f}"
    )
    
    return (steering_intensity, speed, False)


def main() -> None:
    """Main execution loop for sensor-based wall-following."""
    logger.info("=" * 60)
    logger.info("Sensor-based Wall-Following Test")
    logger.info("=" * 60)
    
    # Initialize CarDriver
    # Note: This will attempt to connect to hardware
    # For testing without hardware, you may need to use a mock driver
    try:
        driver = CarDriver()
        logger.info("CarDriver initialized successfully")
    except Exception as exc:
        logger.error(f"Failed to initialize CarDriver: {exc}")
        logger.error("Make sure hardware is connected and I2C is enabled")
        logger.error("For testing without hardware, consider using a mock driver")
        return
    
    # Initialize AutoCarMove
    car = AutoCarMove(driver)
    logger.info("AutoCarMove initialized successfully")
    
    # Control parameters
    kp = 0.5  # P-control gain
    target_distance = 25.0  # Target distance to right wall (cm)
    min_front_distance = 20.0  # Minimum safe front distance (cm)
    loop_delay = 0.1  # Control loop delay in seconds (10Hz)
    
    logger.info(f"Control parameters: kp={kp}, target_dist={target_distance}cm, "
                f"min_front={min_front_distance}cm, loop_rate={1/loop_delay:.1f}Hz")
    logger.info("Starting control loop... (Press Ctrl+C to stop)")
    
    try:
        while True:
            # Read sensor values
            left_dist, front_dist, right_dist = read_sensor_distances()
            
            # Calculate control output
            steering_intensity, speed, should_stop = wall_following_control(
                left_dist, front_dist, right_dist,
                kp=kp,
                target_distance=target_distance,
                min_front_distance=min_front_distance,
            )
            
            # Execute control
            if should_stop:
                logger.warning("Emergency stop triggered!")
                car.stop()
                # Wait a bit before continuing (or break to exit)
                time.sleep(1.0)
                # Optionally break to exit on emergency stop
                # break
            else:
                # Calculate error for steering direction
                error = right_dist - target_distance
                
                if abs(error) < 2.0:  # Within tolerance, go straight
                    car.make_straight(speed)
                    logger.info(f"Straight: speed={speed:.3f}")
                elif error > 0:  # Too far from right wall, turn right
                    car.make_right(steering_intensity, speed)
                    logger.info(f"Right: intensity={steering_intensity:.3f}, speed={speed:.3f}")
                else:  # Too close to right wall, turn left
                    car.make_left(steering_intensity, speed)
                    logger.info(f"Left: intensity={steering_intensity:.3f}, speed={speed:.3f}")
            
            # Control loop delay
            time.sleep(loop_delay)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user (Ctrl+C)")
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}", exc_info=True)
    finally:
        # Cleanup
        logger.info("Stopping vehicle and cleaning up...")
        car.stop()
        driver.cleanup()
        logger.info("Cleanup complete")


if __name__ == "__main__":
    main()
