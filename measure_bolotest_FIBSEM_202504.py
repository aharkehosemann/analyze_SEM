from measure_SEM_routines import *
import csv

"""
put images to measure in .../measurements/legX/images/
if scale bars on all images are the same, set sb_um to that value in um
if sb_um = None, scalebar size will be entered manually in the terminal
"""

### user switches ###
# dist_type = 'vertical'
dist_type = 'horizontal'

# save measurement csv and/or annotated images?
save_csv       = True
save_annotated = True

### config ###
# fs = (14.3, 8.15)   # figsize - make this big for accurate measurements
fs = (20, 10)   # figsize - make this big for accurate measurements
# sb_um = 0.500
sb_um = None
deg_rot = -3.5

# image and csv file paths
fn_comments   = '_testrotation_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
leg_dir       = 'widths/'
analysis_dir  = '/Users/angi/NIS/Bolotest_Analysis/FIB/Bolotest_FIB/April_2025/measurements/' + leg_dir
image_dir     = analysis_dir + 'images/'
annotated_dir = analysis_dir + 'annotated_images/'
csv_dir       = analysis_dir + 'csvs/'
output_csv    = csv_dir      + dist_type + '_measurements' + fn_comments+'.csv'

# create directories if they don't already exist
os.makedirs(annotated_dir, exist_ok=True)
os.makedirs(csv_dir,       exist_ok=True)

all_measurements = []

for filename in sorted(os.listdir(image_dir)):
    if filename.lower().endswith('.tif'):
        image_path = os.path.join(image_dir, filename)
        print('\nprocessing {}'.format(filename))
        results = measure_image(image_path, sb_area=(0.85, 0.98, 0.70, 0.99), sb_um=sb_um, fs=fs, save_annotated=save_annotated, fn_comments=fn_comments,
                                deg_rot=deg_rot, dist_type=dist_type)
        all_measurements.extend(results)

    ### save to csv after each image
    if save_csv:
        with open(output_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            # writer.writerow(['Image', 'Measurement #', 'Vertical Distance [nm]'])
            writer.writerow(['image', 'detector', 'side', 'measurement #', dist_type + ' distance [nm]'])
            for row in all_measurements:
                writer.writerow(row)
        print('\n{num_msmts} measurements saved to {output_csv}'.format(num_msmts=len(all_measurements), output_csv=output_csv))
