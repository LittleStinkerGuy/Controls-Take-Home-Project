package frc.robot.subsystems.MotorTester;

import java.util.ArrayList;
import java.util.List;

import edu.wpi.first.networktables.BooleanSubscriber;
import edu.wpi.first.networktables.NetworkTableInstance;
import edu.wpi.first.wpilibj2.command.SubsystemBase;
import frc.robot.subsystems.Motor.Motor;
import frc.robot.subsystems.Motor.SparkMaxMotor;
import frc.robot.subsystems.Motor.TalonFXMotor;

public class MotorTester extends SubsystemBase {
    private final List<Motor> motors = new ArrayList<>();
    private final BooleanSubscriber estopSub;

    public MotorTester() {
        motors.add(new TalonFXMotor(1));
        motors.add(new SparkMaxMotor(2, false));
        motors.add(new SparkMaxMotor(3, true));
        motors.add(new TalonFXMotor(4));

        NetworkTableInstance nt = NetworkTableInstance.getDefault();
        estopSub = nt.getTable("MotorController").getBooleanTopic("emergencyStop").subscribe(false);
    }

    @Override
    public void periodic() {
        if (estopSub.get()) {
            motors.forEach(Motor::stopMotor);
        }
    }
}
