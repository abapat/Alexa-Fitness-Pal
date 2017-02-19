jump_cycle = []

jump_data = []

class Jump:
    'Common base class for all jumps'

    def __init__(self, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z, rot_x, rot_y):
        self.gyro_x = float(gyro_x)
        self.gyro_y = float(gyro_y)
        self.gyro_z = float(gyro_z)
        self.accel_x = float(accel_x)
        self.accel_y = float(accel_y)
        self.accel_z = float(accel_z)
        self.rot_x = float(rot_x)
        self.rot_y = float(rot_y)


def detect_jump(raw_data):
    numJumps = 0
    jump_sequence = []
    for row in raw_data:
        jump_sequence.append(Jump(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

    fcount = 0
    last_gyro_z = 100

    # -ve +ve | -ve STOP !
    for jump in jump_sequence:
        current_gyro_z = jump.gyro_z
        if(current_gyro_z < 0 and last_gyro_z > 0):
            if (current_gyro_z + last_gyro_z > 300):
                numJumps += 1
            else:
                print "Your jumps aren't perfect. Are you jumping really ?"
        last_gyro_z = current_gyro_z


    print "You jumped", numJumps, "times"