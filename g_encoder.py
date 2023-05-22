# This module currently works in 2 steps:
# 1 convert the path list into a set of pseudo-instruction
# 2 print these pseudo instructions as GCode instructions

from enum import Enum

FEED_RATE = 10000
DRAW_ACCEL = 500  # acceleration
TRAVEL_ACCEL = 1500
PEN_DELAY = 100  # time for pen to raise or lower (ms)
JERK = 1.0  # jerk


# Pseudo-Instructions definitions:
PseudoInstTypes = Enum("PseudoInstTypes", ["SET", "CODE"])


def c(stmt: str):
    return (PseudoInstTypes.CODE, stmt)


def s(**args):
    return (PseudoInstTypes.SET, args)


# instructions
lift_pen = s(pen=False)
lower_pen = s(pen=True)
home_pen = c("G28")


def move_to(point):
    s(pos=point)


def set_accel(a):
    s(accel=a)


set_inst_lowerings = {
    "pen": lambda draw: [
        f"G4 P{PEN_DELAY}",
        "M280 P0 S0 G0 Z0" if draw else "M280 P0 S100 G0 Z10",
    ],
    "pos": lambda point: [f"G0 X{point[0]:.3f} Y{point[1]:.3f}"],
    "accel": lambda accel: [f"M204 T{accel}"],
}


class GEncoder:
    def _move_point(point, accel):
        return [set_accel(accel), move_to(point)]

    def _raised_move(self, point):
        return [
            "TravelMove",
            lift_pen,
            *self._move_point(point, TRAVEL_ACCEL),
            lower_pen,
        ]

    def _draw_path(self, path):
        return [
            *self._raised_move(path[0]),
            *[
                inst
                for point in path[1:]
                for inst in self._move_point(point, DRAW_ACCEL)
            ],
        ]

    def _build__pseudo_instruction_list(self, paths):
        return [
            "HEADER",
            c(f"G0 F{FEED_RATE}"),
            c(f"M205 X{JERK}"),
            home_pen,
            "BODY",
            *[self._draw_path(path) for path in paths],
            "FOOTER",
            lift_pen,
            c("G0 X0"),
            c("M84"),  # Disable Steppers
            c("M282"),  # dePowers Servo
        ]

    def _optimize_pseudo_instructions(self, instructions):
        state = {}
        filtered_instructions = []
        for inst in instructions:
            inst_type, inst_body = inst

            # If this is a set instruction and we're already at that
            # value in the state then skip this instruction. This will
            # remove consecutive multiple moves to the same point.
            if inst_type == PseudoInstTypes.SET:
                key, val = inst_body.items()[0]
                if state[key] == val:
                    continue
            filtered_instructions.append(inst)
        return filtered_instructions

    def _lower_pseudo_instruction(self, inst):
        if isinstance(inst, str):
            return f";; {inst}"
        inst_type, inst_body = inst
        if inst_type == PseudoInstTypes.CODE:
            return inst_body
        key, val = inst_body.items()[0]
        return set_inst_lowerings[key](val)

    def encode(self, paths, f):
        instructions = self._build__pseudo_instruction_list(paths)
        opt_instructions = self._optimize_pseudo_instructions(instructions)
        g_code = self._lower_pseudo_instruction(opt_instructions)

        for inst in g_code:
            print(inst, file=f)
