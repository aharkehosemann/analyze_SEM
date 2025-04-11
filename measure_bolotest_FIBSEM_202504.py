from measure_SEM_routines import *
import csv

### user switches ###
# save measurement csv and/or annotated images?
save_csv       = True
save_annotated = True

### config ###
fs = (14.3, 8.15)   # figsize - make this big for accurate measurements

# image and csv file paths
fn_comments   = '_testing_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
image_dir     = '/Users/angi/NIS/Bolotest_Analysis/FIB/Bolotest_FIB/April_2025/measurements/'
annotated_dir = image_dir + 'annotated_images/'
csv_dir       = image_dir + 'csvs/'
output_csv    = csv_dir   + 'vertical_measurements'+fn_comments+'.csv'


os.makedirs(annotated_dir, exist_ok=True)
os.makedirs(csv_dir, exist_ok=True)

all_measurements = []

for filename in sorted(os.listdir(image_dir)):
    if filename.lower().endswith('.tif'):
        full_path = os.path.join(image_dir, filename)
        print('\nprocessing {}'.format(filename))
        results = measure_image(full_path, fs=fs, save_annotated=save_annotated, fn_comments=fn_comments)
        all_measurements.extend(results)

### save to csv
if save_csv:
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Image', 'Measurement #', 'Vertical Distance [nm]'])
        for row in all_measurements:
            writer.writerow(row)
    print('\n{num_msmts} measurements saved to {output_csv}'.format(num_msmts=len(all_measurements), output_csv=output_csv))

