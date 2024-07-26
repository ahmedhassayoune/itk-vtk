from registration.affine import reg_affine
from registration.bspline import reg_bspline
from registration.rigid3D import reg_rigid3D
from utils import *
import sys

def help():
    print('USAGE: python register.py [TYPE]')
    print('   TYPE : ["affine", "bspline", "rigid3D"]')
    print()
    print('   affine  : ~ 5 minutes')
    print('   bspline : ~ 1 hour 32 minutes')
    print('   rigid3D : ~ 30 seconds')

if __name__ == '__main__':
    if (len(sys.argv) == 2):
        if (sys.argv[1] == 'affine'):
            reg_affine(gre1_image, gre2_image)
        elif (sys.argv[1] == 'bspline'):
            reg_bspline(gre1_image, gre2_image)
        elif (sys.argv[1] == 'rigid3D'):
            reg_rigid3D(gre1_image, gre2_image)
        else:
            help()
            exit(1)
        print('Done')
    else:
        help()
        exit(1)
