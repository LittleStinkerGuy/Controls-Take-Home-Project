# Daniel Kharis Controls Take Home Project

The change log will be updated with every commit and will walk through my though process of implementing changes and challenges I faced working on them.

Todo:

-   [ ] Create basic code to move various models of motors in `./robotCode`
    -   [x] Kraken Support
    -   [x] Falcon Support
    -   [x] SparkMax Support
    -   [x] Network Table Support
    -   [ ] Create motor instances with network table
-   [ ] Add support for motor movement in `./driverUI`
-   [ ] Create a basic debug library in `./RobotCode`
-   [ ] Add logging system in `./driverUI`
-   [ ] Add more commands to motor features

## Changelog

### 1. Basic Project Setup

**Changes Made:**

1. Created two folders: One for the driver UI and one to create sample code to test the UI with.
2. Initialized a WPILib project
3. Initialized a python project with a venv and generated a .gitignore with [CodeZombie's VSCode extension](https://marketplace.visualstudio.com/items?itemName=codezombiech.gitignore)

**Challenges Faced:**
N/A

### 2. Create Subsystems for TalonFX motors and SparkMax motors

**Changes Made:**

1. Updated README for specific motor support
2. Created `Motor` interface to easily support both motor controllers later in the code
3. Added support for FalconFX motors which includes Kraken and Falcon Motors
4. Added support for SparkMax

**Challenges Faced:**

1. Finding specific documentation for motors
2. Constructing the `Motor` interface to be compatible with both motor libraries
3. Handling the fact that a SparkMax motor can have both an absolute and relative encoder

**Solutions**

1. Found code samples in various parts of the web including [Swayam's WWRF code repo](https://github.com/swaswa999/FRC-Coding-and-Controls-Basics/tree/main) and [last year's GRT code](https://github.com/grt192/GRT2025/tree/pre-idaho). Also used auto generated Javadoc documentation.
2. Changed definition of current and voltage getters because FalconFX exposes a couple values (like `motor.getSupplyVoltage()` or `motor.getMotorVoltage()`) and SparkMax only exposes one.
3. If `setPosition()` is used with an absolute encoder, it doesn't do anything. (Bad Solution)

### 3. Add support for reading motor state and moving motors

**Changes Made:**

1. Changed setup of motor subsystem to include the `MotorInterface` interface and `Motor` abstract class to implement network table code with all instances of `Motor`
2. Created a `MotorTester` subsystem to create test motors
3. Added network table implementation to `Motor` class

**Challenges Faced:**

1. Identifying "correct" network table implementation and schema
2. Handling possible race conditions in code
3. Understanding overall WPILib project structure
4. The network table implementation to change motor values seemed not to work

**Solutions**

1. Once again taking inspiration from [last year's GRT code](https://github.com/grt192/GRT2025/tree/pre-idaho) and ChatGPT.
2. I did research on race condition in Java and discovered AtomicBooleans and the `Volatile` Keyword
3. Digging into documentation and also discovering command robots vs timed robots.
4. Looking into the manufacturers' documentation revealed that a separate sim library was required to get them to show changes.
