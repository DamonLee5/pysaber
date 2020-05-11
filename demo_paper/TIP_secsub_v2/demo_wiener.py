import numpy as np
from pysaber import wiener_deblur
import matplotlib.pyplot as plt
from PIL import Image
import yaml

rad_file = 'data/art_10mm.tif'
bright_file = 'data/art_bright.tif'
dark_file = 'data/art_dark.tif'

sdd = 71012.36
sod = 10003.60
pix_wid = 0.675
rwls_reg = [0.8*1e-3]

reg_start = 3.0
reg_mult = 1.05

rad = np.asarray(Image.open(rad_file))
bright = np.asarray(Image.open(bright_file))
dark = np.asarray(Image.open(dark_file))
norm_rad = (rad-dark)/(bright-dark)

src_params = {}
src_params['source_FWHM_x_axis'] = 2.7
src_params['source_FWHM_y_axis'] = 3.0
src_params['norm_power'] = 1.0
src_params['cutoff_FWHM_multiplier'] = 10

det_params = {}
det_params['detector_FWHM_1'] = 1.8
det_params['detector_FWHM_2'] = 135.7
det_params['detector_weight_1'] = 0.92
det_params['norm_power'] = 1.0
det_params['cutoff_FWHM_1_multiplier'] = 10 
det_params['cutoff_FWHM_2_multiplier'] = 10

rwls_stds = []
for reg in rwls_reg:
    rwls_img = np.asarray(Image.open('results_art/art_rwls_reg{:.2e}.tif'.format(reg)))
    sh = rwls_img.shape
    rwls_stds.append(np.std(rwls_img[:sh[0]//4,:sh[1]//4]))

print('RWLS stds {}'.format(rwls_stds))

wiener_img = wiener_deblur(norm_rad,sod,sdd-sod,pix_wid,src_params,det_params,reg_start)
wn_stds = [np.std(wiener_img[:sh[0]//4,:sh[1]//4])]
wn_reg = [reg_start] 
print('Wiener reg {:.2e}, std {:.2e}'.format(wn_reg[-1],wn_stds[-1]))
while wn_stds[-1] > min(rwls_stds):
    reg_start = reg_start*reg_mult 
    wiener_img = wiener_deblur(norm_rad,sod,sdd-sod,pix_wid,src_params,det_params,reg_start)
    wn_stds.append(np.std(wiener_img[:sh[0]//4,:sh[1]//4]))
    wn_reg.append(reg_start) 
    img = Image.fromarray(wiener_img)
    img.save('results_art/art_wiener_reg{:.2e}.tif'.format(reg_start))   
    print('Wiener reg {:.2e}, std {:.2e}'.format(wn_reg[-1],wn_stds[-1]))

for reg,std in zip(rwls_reg,rwls_stds):
    idx = np.argmin(np.fabs(wn_stds-std))
    print('RWLS (reg,std)=({:.2e},{:.2e}), Wiener (reg,std)=({:.2e},{:.2e})'.format(reg,std,wn_reg[idx],wn_stds[idx])) 