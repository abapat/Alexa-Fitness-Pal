import csv
import math

pushup_cycle = []

cycle_data = []

def dump_record():
    global pushup_cycle
    # try:
    cnt = 0
    gyro_x_mean = 0
    gyro_y_mean = 0
    gyro_z_mean = 0
    accel_x_mean = 0
    accel_y_mean = 0
    accel_z_mean = 0
    rot_x_mean = 0
    rot_y_mean = 0

    gyro_x_sd = 0
    gyro_y_sd = 0
    gyro_z_sd = 0
    accel_x_sd = 0
    accel_y_sd = 0
    accel_z_sd = 0
    rot_x_sd = 0
    rot_y_sd = 0

    gyro_x_min = 1000000
    gyro_y_min = 1000000
    gyro_z_min = 1000000
    accel_x_min = 1000000
    accel_y_min = 1000000
    accel_z_min = 1000000
    rot_x_min = 1000000
    rot_y_min = 1000000


    gyro_x_max = -1000000
    gyro_y_max = -1000000
    gyro_z_max = -1000000
    accel_x_max = -1000000
    accel_y_max = -1000000
    accel_z_max = -1000000
    rot_x_max = -1000000
    rot_y_max = -1000000

    for pushup in pushup_cycle:
        cnt += 1
        gyro_x_mean = (gyro_x_mean * (cnt - 1) + pushup.gyro_x) / cnt
        gyro_y_mean = (gyro_y_mean * (cnt - 1) + pushup.gyro_y) / cnt
        gyro_z_mean = (gyro_z_mean * (cnt - 1) + pushup.gyro_z) / cnt

        accel_x_mean = (accel_x_mean * (cnt - 1) + pushup.accel_x) / cnt
        accel_y_mean = (accel_y_mean * (cnt - 1) + pushup.accel_y) / cnt
        accel_z_mean = (accel_z_mean * (cnt - 1) + pushup.accel_z) / cnt

        rot_x_mean = (rot_x_mean * (cnt - 1) + pushup.rot_x) / cnt
        rot_y_mean = (rot_y_mean * (cnt - 1) + pushup.rot_y) / cnt


        if(pushup.gyro_x < gyro_x_min):
            gyro_x_min = pushup.gyro_x
        if (pushup.gyro_y < gyro_y_min):
            gyro_y_min = pushup.gyro_y
        if (pushup.gyro_z < gyro_z_min):
            gyro_z_min = pushup.gyro_z

        if (pushup.accel_x < accel_x_min):
            accel_x_min = pushup.accel_x
        if (pushup.accel_y < accel_y_min):
            accel_y_min = pushup.accel_y
        if (pushup.accel_z < accel_z_min):
            accel_z_min = pushup.accel_z

        if(pushup.rot_x < rot_x_min):
            rot_x_min = pushup.rot_x
        if (pushup.rot_y < rot_y_min):
            rot_y_min = pushup.rot_y



        if (pushup.gyro_x > gyro_x_max):
            gyro_x_max = pushup.gyro_x
        if (pushup.gyro_y > gyro_y_max):
            gyro_y_max = pushup.gyro_y
        if (pushup.gyro_z > gyro_z_max):
            gyro_z_max = pushup.gyro_z

        if (pushup.accel_x > accel_x_max):
            accel_x_max = pushup.accel_x
        if (pushup.accel_y > accel_y_max):
            accel_y_max = pushup.accel_y
        if (pushup.accel_z > accel_z_max):
            accel_z_max = pushup.accel_z

        if (pushup.rot_x > rot_x_max):
            rot_x_max = pushup.rot_x
        if (pushup.rot_y > rot_y_max):
            rot_y_max = pushup.rot_y

    for pushup in pushup_cycle:
        gyro_x_sd += math.pow(pushup.gyro_x - gyro_x_mean, 2)
        gyro_y_sd += math.pow(pushup.gyro_y - gyro_y_mean, 2)
        gyro_z_sd += math.pow(pushup.gyro_z - gyro_z_mean, 2)

        accel_x_sd += math.pow(pushup.accel_x - accel_x_mean, 2)
        accel_y_sd += math.pow(pushup.accel_y - accel_y_mean, 2)
        accel_z_sd += math.pow(pushup.accel_z - accel_z_mean, 2)

        rot_x_sd += math.pow(pushup.rot_x - rot_x_mean, 2)
        rot_y_sd += math.pow(pushup.rot_y - rot_y_mean, 2)

    cycle_data.append([gyro_x_mean, gyro_y_mean, gyro_z_mean, accel_x_mean, accel_y_mean, accel_z_mean, rot_x_mean, rot_y_mean, gyro_x_max-gyro_x_min, gyro_y_max-gyro_y_min, gyro_z_max-gyro_z_min, accel_x_max-accel_x_min, accel_y_max-accel_y_min, accel_z_max-accel_z_min, rot_x_max-rot_x_min, rot_y_max-rot_y_min, gyro_x_sd, gyro_y_sd, gyro_z_sd, accel_x_sd, accel_y_sd, accel_z_sd, rot_x_sd, rot_y_sd])
    pushup_cycle = []
    return True
    # except:
    #     return False



class Pushup:
    'Common base class for all pushups'

    def __init__(self, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z, rot_x, rot_y):
        self.gyro_x = float(gyro_x)
        self.gyro_y = float(gyro_y)
        self.gyro_z = float(gyro_z)
        self.accel_x = float(accel_x)
        self.accel_y = float(accel_y)
        self.accel_z = float(accel_z)
        self.rot_x = float(rot_x)
        self.rot_y = float(rot_y)


pushup_sequence = []
with open("push_up_dataset.csv", "rb") as f:
    reader = csv.reader(f)
    for row in reader:
        pushup_sequence.append(Pushup(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))


fcount = 0
last_gyro_x = 100

print pushup_sequence
# -ve +ve | -ve STOP !
for pushup in pushup_sequence:
    current_gyro_x = pushup.gyro_x
    if(current_gyro_x < 0 and last_gyro_x > 0):
        print "------------------------------"
        if (dump_record()):
            pushup_cycle.append(pushup)
        else:
            print "ERROR"
    else:
        print "gyro_x:", current_gyro_x
        pushup_cycle.append(pushup)
    last_gyro_x = current_gyro_x

ofile = open('push_up_records.csv', "wb")
writer = csv.writer(ofile)

for row in cycle_data:
    writer.writerow(row)




