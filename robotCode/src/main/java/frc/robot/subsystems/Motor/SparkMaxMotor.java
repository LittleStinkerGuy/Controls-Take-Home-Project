package frc.robot.subsystems.Motor;

import com.revrobotics.spark.SparkLowLevel.MotorType;
import com.revrobotics.spark.config.SparkMaxConfig;
import com.revrobotics.spark.SparkMax;

import static edu.wpi.first.units.Units.*;
import edu.wpi.first.units.measure.*;

import com.revrobotics.spark.SparkBase.PersistMode;
import com.revrobotics.spark.SparkBase.ResetMode;

public class SparkMaxMotor extends Motor {
    private final SparkMax motor;
    boolean absoluteEncoder;

    public SparkMaxMotor(int deviceID, boolean encoderPluggedIn) {
        motor = new SparkMax(deviceID, MotorType.kBrushless);
        absoluteEncoder = encoderPluggedIn;

        SparkMaxConfig globalConfig = new SparkMaxConfig();
        motor.configure(globalConfig, ResetMode.kResetSafeParameters, PersistMode.kPersistParameters);
        initNT();
    }

    public int getId() {
        return motor.getDeviceId();
    }

    public Voltage getBusVoltage() {
        return Volts.of(motor.getBusVoltage());
    }

    public Current getOutputCurrent() {
        return Amps.of(motor.getOutputCurrent());
    };

    public Temperature getTemperature() {
        return Celsius.of(motor.getMotorTemperature());
    }

    public void setSpeed(Dimensionless speed) {
        motor.set(speed.in(Value));
    }

    public AngularVelocity getVelocity() {
        double v = absoluteEncoder ? motor.getAbsoluteEncoder().getVelocity()
                : motor.getEncoder().getVelocity();
        return RPM.of(v);
    }

    public Dimensionless getSetSpeed() {
        return Value.of(motor.get());
    }

    // kinda bad practice for absolute encoder but 🤷‍♂️
    public void setPosition(Angle position) {
        if (!absoluteEncoder) {
            motor.getEncoder().setPosition(position.in(Rotations));
        }
    };

    public Angle getPosition() {
        double p = absoluteEncoder ? motor.getAbsoluteEncoder().getPosition()
                : motor.getEncoder().getPosition();
        return Rotations.of(p);
    }

    public void stopMotor() {
        super.desiredSpeedPublisher.set(0);
        motor.stopMotor();
    };
}
