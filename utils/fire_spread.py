def generate_fire_spread(ignition_x, ignition_y, steps=10):
    spread_frames = []
    current_fire = set([(ignition_x, ignition_y)])

    for step in range(steps):
        new_fire = set()
        for x, y in current_fire:
            neighbors = [
                (x + 1, y), (x - 1, y),
                (x, y + 1), (x, y - 1),
                (x + 1, y + 1), (x - 1, y - 1),
                (x - 1, y + 1), (x + 1, y - 1)
            ]
            new_fire.update(neighbors)
        current_fire.update(new_fire)

        # Save current step frame
        frame = [{"x": x, "y": y, "intensity": 1.0} for x, y in current_fire]
        spread_frames.append(frame)

    return spread_frames
