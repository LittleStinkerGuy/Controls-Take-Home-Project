package frc.robot.subsystems;

import static edu.wpi.first.units.Units.Rotations;
import edu.wpi.first.units.measure.*;

public interface Motor {
    public int getId();

    public Voltage getBusVoltage();

    public Current getOutputCurrent();

    public Temperature getTemperature();

    public void setSpeed(Dimensionless speed);

    public AngularVelocity getVelocity();

    public Dimensionless getSetSpeed();

    public void setPosition(Angle position);

    public Angle getPosition();

    public default void resetPosition() {
        this.setPosition(Rotations.of(0));
    };

    public void stopMotor();
}
