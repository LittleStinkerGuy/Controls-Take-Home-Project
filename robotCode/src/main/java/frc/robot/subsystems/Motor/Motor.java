package frc.robot.subsystems.Motor;

import static edu.wpi.first.units.Units.*;

import java.util.EnumSet;
import java.util.concurrent.atomic.AtomicBoolean;

import edu.wpi.first.networktables.DoublePublisher;
import edu.wpi.first.networktables.DoubleSubscriber;
import edu.wpi.first.networktables.BooleanPublisher;
import edu.wpi.first.networktables.BooleanSubscriber;
import edu.wpi.first.networktables.NetworkTable;
import edu.wpi.first.networktables.NetworkTableEvent;
import edu.wpi.first.networktables.NetworkTableInstance;
import edu.wpi.first.wpilibj2.command.SubsystemBase;

public abstract class Motor extends SubsystemBase implements MotorInterface {
    NetworkTableInstance ntInstance;

    NetworkTable motorStatsTable;
    NetworkTable motorCommandsTable;

    DoublePublisher busVoltagePublisher;
    DoublePublisher outputCurrentPublisher;
    DoublePublisher temperaturePublisher;
    DoublePublisher velocityPublisher;
    DoublePublisher setSpeedPublisher;
    DoublePublisher positionPublisher;

    DoubleSubscriber desiredSpeedSubscriber;
    DoublePublisher desiredSpeedPublisher;
    DoubleSubscriber newPositionSubscriber;
    DoublePublisher newPositionPublisher;
    BooleanSubscriber stopSubscriber;
    BooleanPublisher stopPublisher;
    BooleanSubscriber resetSubscriber;
    BooleanPublisher resetPublisher;

    private final AtomicBoolean updateSpeed = new AtomicBoolean(false);
    private final AtomicBoolean updatePosition = new AtomicBoolean(false);
    private final AtomicBoolean updateStop = new AtomicBoolean(false);
    private final AtomicBoolean updateReset = new AtomicBoolean(false);

    private volatile double desiredSpeedCached = 0;
    private volatile double newPositionCached = 0;
    private volatile boolean stopCached = false;
    private volatile boolean resetCached = false;

    public void resetPosition() {
        this.setPosition(Rotations.of(0));
    }

    public void initNT() {
        ntInstance = NetworkTableInstance.getDefault();
        motorStatsTable = ntInstance.getTable("MotorStats").getSubTable(Integer.toString(getId()));
        motorCommandsTable = ntInstance.getTable("MotorController").getSubTable(Integer.toString(getId()));

        busVoltagePublisher = motorStatsTable.getDoubleTopic("busVoltage").publish();
        outputCurrentPublisher = motorStatsTable.getDoubleTopic("outputCurrent").publish();
        temperaturePublisher = motorStatsTable.getDoubleTopic("temperature").publish();
        velocityPublisher = motorStatsTable.getDoubleTopic("velocity").publish();
        setSpeedPublisher = motorStatsTable.getDoubleTopic("setSpeed").publish();
        positionPublisher = motorStatsTable.getDoubleTopic("position").publish();

        motorCommandsTable.getDoubleTopic("desiredSpeed").publish().set(0);
        motorCommandsTable.getDoubleTopic("newPosition").publish().set(0);
        motorCommandsTable.getBooleanTopic("stop").publish().set(false);
        motorCommandsTable.getBooleanTopic("reset").publish().set(false);

        desiredSpeedSubscriber = motorCommandsTable.getDoubleTopic("desiredSpeed").subscribe(0);
        newPositionSubscriber = motorCommandsTable.getDoubleTopic("newPosition").subscribe(0);
        stopSubscriber = motorCommandsTable.getBooleanTopic("stop").subscribe(false);
        resetSubscriber = motorCommandsTable.getBooleanTopic("reset").subscribe(false);

        ntInstance.addListener(desiredSpeedSubscriber, EnumSet.of(NetworkTableEvent.Kind.kValueRemote),
                event -> {
                    System.out.println("4");
                    desiredSpeedCached = event.valueData.value.getDouble();
                    updateSpeed.set(true);
                });

        ntInstance.addListener(newPositionSubscriber, EnumSet.of(NetworkTableEvent.Kind.kValueRemote),
                event -> {
                    System.out.println("5");
                    newPositionCached = event.valueData.value.getDouble();
                    updatePosition.set(true);
                });

        ntInstance.addListener(stopSubscriber, EnumSet.of(NetworkTableEvent.Kind.kValueRemote),
                event -> {
                    System.out.println("6");
                    stopCached = event.valueData.value.getBoolean();
                    updateStop.set(true);
                });

        ntInstance.addListener(resetSubscriber, EnumSet.of(NetworkTableEvent.Kind.kValueRemote),
                event -> {
                    System.out.println("7");
                    resetCached = event.valueData.value.getBoolean();
                    updateReset.set(true);
                });
    }

    public void publishToNT() {
        busVoltagePublisher.set(getBusVoltage().in(Volts));
        outputCurrentPublisher.set(getOutputCurrent().in(Amps));
        temperaturePublisher.set(getTemperature().in(Celsius));
        velocityPublisher.set(getVelocity().in(RPM));
        setSpeedPublisher.set(getSetSpeed().in(Value));
        positionPublisher.set(getPosition().in(Rotations));
    }

    public void updateMotorState() {
        if (updateSpeed.getAndSet(false)) {
            setSpeed(Percent.of(desiredSpeedCached));
            System.out.println(Percent.of(desiredSpeedCached));
        }
        if (updatePosition.getAndSet(false) && !Double.isNaN(newPositionCached)) {
            setPosition(Rotations.of(newPositionCached));
            System.out.println(Rotations.of(newPositionCached));
        }
        if (updateStop.getAndSet(false) && stopCached) {
            stopMotor();
            System.out.println("1");
        }
        if (updateReset.getAndSet(false) && resetCached) {
            resetPosition();
            System.out.println("2");
        }
    }

    @Override
    public void periodic() {
        updateMotorState();
        publishToNT();
    }

}
