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
PseudoInstType = Enum("PseudoInstType", ["SET", "CODE"])
MachineSetting = Enum("MachineSetting", ["PEN", "POS", "ACCEL"])


c = lambda stmt: (PseudoInstType.CODE, stmt)
s = lambda k, v: (PseudoInstType.SET, (k, v))

# instructions
lift_pen = s(MachineSetting.PEN, False)
lower_pen = s(MachineSetting.PEN, True)
home_pen = c("G28")
move_to = lambda point: s(MachineSetting.POS, point)
set_accel = lambda a: s(MachineSetting.ACCEL, a)


set_inst_lowerings = {
    MachineSetting.PEN: lambda draw: [
        f"G4 P{PEN_DELAY}",
        "M280 P0 S0 G0 Z0" if draw else "M280 P0 S100 G0 Z10",
    ],
    MachineSetting.POS: lambda point: [f"G0 X{point[0]:.3f} Y{point[1]:.3f}"],
    MachineSetting.ACCEL: lambda accel: [f"M204 T{accel}"],
}


class GEncoder:
    def _move_point(self, point, accel):
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

    def _build_pseudo_instruction_list(self, paths):
        return [
            "HEADER",
            c(f"G0 F{FEED_RATE}"),
            c(f"M205 X{JERK}"),
            home_pen,
            "BODY",
            *[inst for path in paths for inst in self._draw_path(path)],
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
            # skip comments
            if not isinstance(inst, str):
                inst_type, inst_body = inst
                # If this is a set instruction and we're already at that
                # value in the state then skip this instruction. This will
                # remove consecutive multiple moves to the same point.
                if inst_type == PseudoInstType.SET:
                    key, val = inst_body
                    if key in state and state[key] == val:
                        continue
                    state[key] = val

            filtered_instructions.append(inst)

        return filtered_instructions

    def _lower_pseudo_instruction(self, inst):
        if isinstance(inst, str):
            return [f";; {inst}"]
        inst_type, inst_body = inst
        if inst_type == PseudoInstType.CODE:
            return [inst_body]
        key, val = inst_body
        return set_inst_lowerings[key](val)

    def _lower_pseudo_instructions(self, pseudos):
        return [
            inst
            for pseudo_inst in pseudos
            for inst in self._lower_pseudo_instruction(pseudo_inst)
        ]

    def encode(self, paths, f):
        instructions = self._build_pseudo_instruction_list(paths)
        opt_instructions = self._optimize_pseudo_instructions(instructions)
        g_code = self._lower_pseudo_instructions(opt_instructions)

        for inst in g_code:
            print(inst, file=f)
