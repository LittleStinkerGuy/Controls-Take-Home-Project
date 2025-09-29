package frc.robot.subsystems.Motor;

import edu.wpi.first.units.measure.*;

public interface MotorInterface {
    public int getId();

    public Voltage getBusVoltage();

    public Current getOutputCurrent();

    public Temperature getTemperature();

    public void setSpeed(Dimensionless speed);

    public AngularVelocity getVelocity();

    public Dimensionless getSetSpeed();

    public void setPosition(Angle position);

    public Angle getPosition();

    public void resetPosition();

    public void stopMotor();

    public void initNT();

    public void publishToNT();
}
