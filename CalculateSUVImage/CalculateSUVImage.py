#!/usr/bin/env python-real

import SimpleITK as sitk
import sys
import os

if len ( sys.argv ) < 6 or len ( sys.argv ) > 7:
    print( "Usage: CalculateSUVImage <input> <inputUnits=kBq_cc|Bq_cc|nCi_cc> <IDMbq> <bodyWeightkg> <output> [same|float32*|float64]" )
    sys.exit ( 1 )

def calcSUVFactor(inputUnits, IDMbq, bodyWeightkg):
    factor = 1.0
    if inputUnits=="nCi_cc": # go to kBq/cc
        factor = 0.037
    elif inputUnits=="Bq_cc":
        factor = 1/1000.0
    factor /= (IDMbq/bodyWeightkg) # MBq/kg is the same as kBq/g, assumed to be equivalent to kBq/cc (1 g = 1cc)
    return factor

reader = sitk.ImageFileReader()
reader.SetFileName(sys.argv[1])
image = reader.Execute()

pixelID = sitk.sitkFloat32
if len( sys.argv ) == 7:
    if sys.argv[6] == "same":
        pixelID = image.GetPixelID()
    elif sys.argv[6] == "float64":
        pixelID = sitk.sitkFloat64

inputUnits = sys.argv[2]
IDMbq = float(sys.argv[3])
bodyWeightkg = float(sys.argv[4])
suvFactor = calcSUVFactor(inputUnits, IDMbq, bodyWeightkg)

shiftScale = sitk.ShiftScaleImageFilter()
shiftScale.SetScale(suvFactor)
try:
    shiftScale.SetOutputPixelType(pixelID)
    image = shiftScale.Execute(image)
except:
    image = shiftScale.Execute(image)
    caster = sitk.CastImageFilter()
    caster.SetOutputPixelType(pixelID)
    image = caster.Execute(image)

writer = sitk.ImageFileWriter()
writer.SetFileName (sys.argv[5])
writer.Execute (image)
