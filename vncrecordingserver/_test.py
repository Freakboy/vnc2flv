import glob
import os
from subprocess import run
path = '/home/zeel/Desktop/vnc2flv/vncrecordingserver'
# path = os.getcwd()
# print(path)
li = []
for infile in glob.glob(os.path.join(path, '*.flv')):
    # os.popen('cd {}'.format(path))
    # print(infile.split('/')[6])
    filename = infile.split('/')[6]
    # print(type(infile))

    li.append(filename)

    # os.popen('ffmpeg -i {} output.mp4'.format(infile))
print(li)
# print(li[0])
for l in li :
    l1 = l.split('f')[0]
    print(l1)
    # if '{}mp4'.format(l1) is None:
    if os.path.exists('%smp4' % (l1)) == False:
        # os.popen('ffmpeg -i {} {}mp4'.format(l, l1))
        run('ffmpeg -i {} {}mp4'.format(l, l1),shell=True)

    # os.system('ffmpeg -i {} {}mp4'.format(l,l1))
# os.system('ffmpeg -i {} output.mp4'.format(li[0]))