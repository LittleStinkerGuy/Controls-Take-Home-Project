// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

package frc.robot.subsystems.Motor;

import static edu.wpi.first.units.Units.*;
import edu.wpi.first.units.measure.*;

import com.ctre.phoenix6.configs.CurrentLimitsConfigs;
import com.ctre.phoenix6.configs.TalonFXConfiguration;
import com.ctre.phoenix6.hardware.TalonFX;
import com.ctre.phoenix6.signals.NeutralModeValue;
import com.ctre.phoenix6.sim.TalonFXSimState;

public class TalonFXMotor extends Motor {

  private final TalonFX motor;
  private final TalonFXSimState motorSim;

  public TalonFXMotor(int deviceID) {
    motor = new TalonFX(deviceID, "can");
    motorSim = new TalonFXSimState(motor);

    TalonFXConfiguration config = new TalonFXConfiguration();
    // lowk chat gpt-ed these values idk what they do
    config.MotorOutput.NeutralMode = NeutralModeValue.Coast;
    config.CurrentLimits = new CurrentLimitsConfigs()
        .withStatorCurrentLimit(60.0)
        .withStatorCurrentLimitEnable(true)
        .withSupplyCurrentLimit(40.0)
        .withSupplyCurrentLimitEnable(true);
    motor.getConfigurator().apply(config);
    initNT();
  }

  public int getId() {
    return motor.getDeviceID();
  }

  public Voltage getBusVoltage() {
    return motor.getSupplyVoltage().getValue();
  }

  public Current getOutputCurrent() {
    return motor.getTorqueCurrent().getValue();
  }

  public Temperature getTemperature() {
    return motor.getDeviceTemp().getValue();
  }

  public void setSpeed(Dimensionless speed) {
    motor.set(speed.in(Value) * 6000);

    motorSim.setRotorVelocity(speed.in(Value));
  }

  public AngularVelocity getVelocity() {
    return motor.getVelocity().getValue();

  }

  public Dimensionless getSetSpeed() {
    return Value.of(motor.get());
  }

  public void setPosition(Angle position) {
    motor.setPosition(position);

    motorSim.setRawRotorPosition(position);
  }

  public Angle getPosition() {
    return motor.getPosition().getValue();
  }

  public void stopMotor() {
    motor.stopMotor();

    motorSim.setRotorVelocity(0);
  }
}
