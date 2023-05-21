
FeedRate = 10000
drawAccel = 500  # acceleration
travelAccel = 1500
penDelay = 100  # time for pen to raise or lower (ms)
jerk = 1.0  # jerk


# definitions
liftPen = [f"G4 P{penDelay}", "M280 P0 S100 G0 Z10"]
lowerPen = [f"G4 P{penDelay}", "M280 P0 S0 G0 Z0"]
homePen = ["G28"]


def comment(text):
    return f";; {text}"

def raised_move(point):
    return [
        comment("TravelMove"),
        *liftPen,
        *move_point(point, travelAccel),
        *lowerPen,
    ]


def move_point(point, accel):
    x, y = point
    return [
        f"M204 T{accel}",
        f"G0 X{x:.3f} Y{y:.3f}"]


def draw_path(path):
    return [*raised_move(path[0]), *[move_point(point, drawAccel) for point in path[1:]]]


def g_encode(paths):
    instructions = [
        # G-code HEADER
        comment("HEADER"),
        "G0 F{FeedRate}",
        f"M205 X{jerk}",
        *liftPen,
        *homePen,
        # G-code BODY
        comment("Body"),
        *[draw_path(path) for path in paths],
        comment("FOOTER"),
        *liftPen,
        "G0 X0",
        "M84",  # Disable Steppers
        "M282",  # dePowers Servo
    ]

    for inst in instructions:
        print(inst)
