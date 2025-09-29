"""
Motor NT client library using ntcore (WPILib NT4).

Provides a simple interface to read motor stats and issue commands
(speed, position, stop, reset) against the following NetworkTables layout:

  MotorStats/<id>/{busVoltage, outputCurrent, temperature, velocity, setSpeed, position}
  MotorController/<id>/{desiredSpeed, newPosition, stop, reset}

Tested against the API documented in RobotPy ntcore.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
from ntcore import NetworkTableInstance


@dataclass
class MotorData:
    busVoltage: float
    outputCurrent: float
    temperature: float
    velocity: float
    setSpeed: float
    position: float


class MotorNTClient:
    """Lightweight client for the Java `Motor` NT schema.

    Usage:
        client = MotorNTClient(server="127.0.0.1")
        client.start()
        data = client.get_motor_data(1)
        client.set_speed(1, 0.5)
        client.set_position(1, 10.0)  # rotations
        client.stop(1)
        client.reset(1)
        client.stop_client()
    """

    def __init__(
        self,
        server: Optional[str] = None,
        team: Optional[int] = None,
        port: Optional[int] = None,
        client_name: str = "DriverUI",
    ):
        self.inst = NetworkTableInstance.getDefault()
        self.server = server
        self.team = team
        self.port = (
            port
            if port is not None
            else getattr(NetworkTableInstance, "kDefaultPort4", 5810)
        )
        self.client_name = client_name
        self._started = False

        # Cache topic subscribers (stats) and publishers (commands) per motor id
        self._stats_subs: Dict[int, Dict[str, Any]] = {}
        self._cmd_pubs: Dict[int, Dict[str, Any]] = {}

    # ------------------------ lifecycle ------------------------
    def start(self) -> None:
        """Start NT as a client and connect to the server (robot or sim)."""
        # Ensure a clean start
        try:
            self.inst.stopClient()
            self.inst.stopDSClient()
        except Exception:
            pass

        if self.team is not None:
            # Use Driver Station discovery (works best when running on the DS machine)
            self.inst.startClient4(self.client_name)
            self.inst.setServerTeam(self.team, self.port)
        elif self.server is not None:
            self.inst.startClient4(self.client_name)
            self.inst.setServer([self.server], self.port)
        else:
            # Default to localhost (useful for simulation on the same machine)
            self.inst.startClient4(self.client_name)
            self.inst.setServer(["127.0.0.1"], self.port)

    def stop_client(self) -> None:
        self.inst.stopClient()
        self._started = False

    # ------------------------ internals ------------------------
    def _ensure_stats_subs(self, motor_id: int) -> Dict[str, Any]:
        subs = self._stats_subs.get(motor_id)
        if subs is not None:
            return subs
        stats = self.inst.getTable("MotorStats").getSubTable(str(motor_id))
        subs = {
            "busVoltage": stats.getDoubleTopic("busVoltage").subscribe(0.0),
            "outputCurrent": stats.getDoubleTopic("outputCurrent").subscribe(0.0),
            "temperature": stats.getDoubleTopic("temperature").subscribe(0.0),
            "velocity": stats.getDoubleTopic("velocity").subscribe(0.0),
            "setSpeed": stats.getDoubleTopic("setSpeed").subscribe(0.0),
            "position": stats.getDoubleTopic("position").subscribe(0.0),
        }
        self._stats_subs[motor_id] = subs
        return subs

    def _ensure_cmd_pubs(self, motor_id: int) -> Dict[str, Any]:
        pubs = self._cmd_pubs.get(motor_id)
        if pubs is not None:
            return pubs
        cmds = self.inst.getTable("MotorController").getSubTable(str(motor_id))
        pubs = {
            "desiredSpeed": cmds.getDoubleTopic("desiredSpeed").publish(),
            "newPosition": cmds.getDoubleTopic("newPosition").publish(),
            "stop": cmds.getBooleanTopic("stop").publish(),
            "reset": cmds.getBooleanTopic("reset").publish(),
        }
        # Initialize command defaults expected by the Java side
        pubs["desiredSpeed"].set(0.0)
        pubs["newPosition"].set(0.0)
        pubs["stop"].set(False)
        pubs["reset"].set(False)
        self._cmd_pubs[motor_id] = pubs
        return pubs

    # ------------------------ reads ------------------------
    def get_motor_data(self, motor_id: int) -> MotorData:
        """Fetch all stats for a motor id (snapshot).

        Returns a MotorData dataclass with fields: busVoltage, outputCurrent,
        temperature, velocity, setSpeed, position.
        """
        subs = self._ensure_stats_subs(motor_id)
        return MotorData(
            busVoltage=float(subs["busVoltage"].get()),
            outputCurrent=float(subs["outputCurrent"].get()),
            temperature=float(subs["temperature"].get()),
            velocity=float(subs["velocity"].get()),
            setSpeed=float(subs["setSpeed"].get()),
            position=float(subs["position"].get()),
        )

    # ------------------------ commands ------------------------
    def set_speed(self, motor_id: int, percent_output: float) -> None:
        """Command motor to a percent output in range [-1.0, 1.0]."""
        pubs = self._ensure_cmd_pubs(motor_id)
        pubs["stop"].set(False)
        v = float(percent_output)
        pubs["desiredSpeed"].set(v)

    def set_position(self, motor_id: int, rotations: float) -> None:
        """Command motor to an absolute position in *rotations*."""
        pubs = self._ensure_cmd_pubs(motor_id)
        pubs["reset"].set(False)
        pubs["newPosition"].set(float(rotations))

    def stop(self, motor_id: int) -> None:
        """Issue a one-shot stop command."""
        pubs = self._ensure_cmd_pubs(motor_id)
        pubs["stop"].set(True)
        print("stop")

    def reset(self, motor_id: int) -> None:
        """Request a position reset (to 0 rotations)."""
        pubs = self._ensure_cmd_pubs(motor_id)
        pubs["reset"].set(True)
        print("reset")


# # ------------------------ simple CLI test ------------------------
# def interactive_test():
#     """
#     Simple command-line test harness.
#     - Creates a `MotorNTClient`
#     - Connects to the NT server
#     - Uses motor id 1 ("kraken motor at one")
#     - Prompts the user to issue commands or read stats
#     """
#     import os

#     # Allow the user to specify connection via env or prompt
#     server = os.environ.get("NT_SERVER")
#     team = os.environ.get("NT_TEAM")
#     port_env = os.environ.get("NT_PORT")
#     port = int(port_env) if port_env else None

#     if server is None and team is None:
#         try:
#             raw = input(
#                 "Enter NT server hostname/IP (blank for 127.0.0.1) or 'team:<num>': "
#             ).strip()
#         except EOFError:
#             raw = ""
#         if raw.startswith("team:"):
#             try:
#                 team = int(raw.split(":", 1)[1])
#             except Exception:
#                 print("Invalid team number; defaulting to localhost")
#                 server = "127.0.0.1"
#         elif raw:
#             server = raw
#         else:
#             server = "127.0.0.1"

#     # Build client
#     client = MotorNTClient(server=server, team=int(team) if team else None, port=port)
#     print(
#         f"Starting NT client (server={server}, team={team}, port={port or client.port})..."
#     )
#     client.start()

#     motor_id = 1  # "kraken motor at one"
#     print("\nConnected. Using motor id = 1.")
#     print(
#         "Commands: \n"
#         "  s  - set speed (percent -100..100)\n"
#         "  p  - set position (rotations)\n"
#         "  x  - stop (boolean)\n"
#         "  r  - reset (boolean)\n"
#         "  g  - get/read stats\n"
#         "  q  - quit\n"
#     )

#     def read_and_print():
#         try:
#             d = client.get_motor_data(motor_id)
#             print(
#                 f"busVoltage={d.busVoltage:.2f}V, current={d.outputCurrent:.2f}A, temp={d.temperature:.2f}C, "
#                 f"velocity={d.velocity:.2f}rpm, setSpeed={d.setSpeed:.2f}, position={d.position:.3f}rot"
#             )
#         except Exception as e:
#             print(f"Read failed: {e}")

#     while True:
#         try:
#             cmd = input("Enter command (s/p/x/r/g/q): ").strip().lower()
#         except EOFError:
#             cmd = "q"

#         if cmd == "q":
#             break
#         elif cmd == "s":
#             try:
#                 pct = float(input("Percent output [-100..100]: ").strip())
#             except Exception:
#                 print("Invalid number")
#                 continue
#             pct = max(-100.0, min(100.0, pct))
#             try:
#                 client.set_speed(motor_id, pct / 100.0)
#                 print(f"desiredSpeed <- {pct/100.0:.2f}")
#             except Exception as e:
#                 print(f"set_speed failed: {e}")
#         elif cmd == "p":
#             try:
#                 rot = float(input("Position (rotations): ").strip())
#             except Exception:
#                 print("Invalid number")
#                 continue
#             try:
#                 client.set_position(motor_id, rot)
#                 print(f"newPosition <- {rot:.3f}")
#             except Exception as e:
#                 print(f"set_position failed: {e}")
#         elif cmd == "x":
#             try:
#                 client.stop(motor_id)
#                 print("stop <- True->False pulse sent")
#             except Exception as e:
#                 print(f"stop failed: {e}")
#         elif cmd == "r":
#             try:
#                 client.reset(motor_id)
#                 print("reset <- True->False pulse sent")
#             except Exception as e:
#                 print(f"reset failed: {e}")
#         elif cmd == "g":
#             read_and_print()
#         else:
#             print("Unknown command")

#     try:
#         client.stop_client()
#     except Exception:
#         pass
#     print("Client stopped. Bye.")


# interactive_test()
