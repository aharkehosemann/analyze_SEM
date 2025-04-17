
"""
loads sem images and takes measurements of vertical distances
images to be analyzed should be in image_dir
currently set up to only take vertical measurements, but could easily be modified to measure horizontal distances

TODO: auto-detection of scalebar is currently not reliable
"""
import matplotlib.pyplot as plt
import numpy as np
# import pytesseract
import cv2
import os
import datetime
from re import search
from skimage import io, color, filters, measure, morphology, util

# plot settings
font = {'family':'serif', 'weight':'normal', 'size':18}
ticks = {'major.size':'5', 'labelsize':'16', 'minor.visible':False}
plt.rc('text', usetex=True); plt.rc('font', **font)
plt.rc('xtick', **ticks);    plt.rc('ytick', **ticks)
plt.rcParams['text.latex.preamble'] = '\\usepackage{amsmath}'
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['figure.dpi'] = 100; plt.rcParams['savefig.dpi'] = 300   # higher resolution plots in interactive notebook and when saving pngs

### functions ###
def scalebar_pixels(image, show_scalebar=False, auto_detect=False, sb_area=(0.85, 0.98, 0.75, 0.99), aratio_min=5, width_min=30, width_max=400, fs=(14.3, 8.15)):
    # scalebar detection; auto-detection is currently not reliable

    # crop bottom right of the image containing the scalebar
    h, w = image.shape[:2]
    crop_bottom =   int(h*sb_area[0])
    crop_top    =   int(h*sb_area[1])
    crop_left   =   int(w*sb_area[2])
    crop_right  =   int(w*sb_area[3])
    cropped = image[crop_bottom:crop_top, crop_left:crop_right]

    # if auto_detect:
    #     # convert to grayscale and threshold
    #     gray   = color.rgb2gray(cropped)
    #     thresh = filters.threshold_otsu(gray)
    #     binary = gray < thresh  # adjust depending on scale bar color (black/white)

    #     # clean up and label
    #     binary  = morphology.remove_small_objects(binary, min_size=50)
    #     binary  = morphology.binary_closing(binary, morphology.rectangle(3, 3))
    #     labels  = measure.label(binary)
    #     regions = measure.regionprops(labels)

    #     # filter regions by aspect ratio to find horizontal bar
    #     for region in regions:
    #         minr, minc, maxr, maxc = region.bbox
    #         width  = maxc - minc
    #         height = maxr - minr
    #         aspect_ratio = width / height if height > 0 else 0

    #         if aspect_ratio > aratio_min and width > width_min and width < width_max:
    #             # extract the region containing the scalebar
    #             scalebar_region = binary[minr:maxr, minc:maxc]

    #             # Detect the horizontal line and perpendicular caps
    #             horizontal_line = np.sum(scalebar_region, axis=0) > (0.8 * scalebar_region.shape[0])
    #             vertical_caps   = np.sum(scalebar_region, axis=1) > (0.8 * scalebar_region.shape[1])

    #             if np.any(horizontal_line) and np.any(vertical_caps):
    #                 barlength_px = np.sum(horizontal_line)
    #                 if show_scalebar:
    #                     # Visualize the detected scalebar
    #                     bar_bbox = (minc, minr + int(h * (1 - sb_area[0])), maxc, maxr + int(h * (1 - sb_area[0])))

    #                     plt.figure(figsize=fs)
    #                     plt.imshow(image, cmap='gray')
    #                     x1, y1, x2, y2 = bar_bbox
    #                     plt.gca().add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, edgecolor='red', facecolor='none', linewidth=2))
    #                     plt.title("Detected Scale Bar")
    #                     plt.show()
    #                 return barlength_px
    #             else:
    #                 print('\nscale bar not detected; falling back to manual definition\n')

    print('\nclick on two ends of the scale bar\n')
    plt.figure(figsize=fs)
    plt.imshow(cropped, cmap='gray')
    plt.title('click two ends of the scale bar')
    scalebar_points = plt.ginput(2, timeout=0)  # click two points
    plt.close()

    # calculate pixel distance of the scale bar
    pts = scalebar_points
    (x1, y1), (x2, y2) = pts
    barlength_px = abs(x2 - x1)

    return barlength_px


def scalebar_realunits(image, sb_area=(0.85, 0.98, 0.75, 0.99), fs=(14.3, 8.15)):
    # h, w    = image.shape[:2]
    # crop_h  = int(h * sb_area[0])
    # crop_w  = int(w * sb_area[1])
    # cropped = image[h - crop_h:, w - crop_w:]

    # gray      = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)
    # _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # text = pytesseract.image_to_string(binary, config='--psm 6')

    # match_um = search(r"([\d\.]+)\s*(μm|um)", text.lower())
    # # match_nm = search(r"([\d\.]+)\s*(nm)", text.lower())
    # if match_um:   # found scale in um
    #     return float(match_um.group(1))
    # elif match_nm:   # found scale in nm
    #     return float(match_nm.group(1))*1E-3
    # else:
    # print('could not extract real-world scale, please note the scalebar then enter length manually')
    print('note the scalebar then close the figure and enter length manually')
    plt.figure(figsize=fs)
    plt.imshow(image, cmap='gray'); plt.show()
    barlength_um = float(input("scalebar length in um: "))
    plt.close()
    return barlength_um


def measure_image(image_path, save_annotated=False, fn_comments='', sb_um=None, fs=(14.3, 8.15), sb_area=(0.85, 0.98, 0.75, 0.99), zoom_h=0.90, dist_type='vertical'):

    base_impath   = os.path.basename(image_path)
    image_dir     = os.path.dirname(image_path) + '/'
    analysis_dir  = os.path.dirname(os.path.dirname(image_dir)) + '/'
    annotated_dir = analysis_dir + 'annotated_images/'

    # load the image
    image       = io.imread(image_path)

    h, w    = image.shape[:2]   # zoom into image so it's larger
    cropped = image[:int(h*zoom_h), :]

    # measure size of scale bar in pixels
    barlength_px = scalebar_pixels(image, show_scalebar=True, sb_area=sb_area, fs=fs)
    if not barlength_px:
        print('scale bar not detected in {impath}'.format(impath=base_impath))
        return
    print('length of scale bar in pixels: {barlength_px:.0f} μm\n'.format(barlength_px=barlength_px))

    # read the real-world length of the scale bar
    barlength_um = sb_um if sb_um else scalebar_realunits(image, sb_area=sb_area, fs=fs)
    if not barlength_um:
        print('could not extract real-world scale')
        return
    print('real length of scale bar: {barlength_um:.3f} μm\n'.format(barlength_um=barlength_um))

    px_per_micron = barlength_px / barlength_um
    print('pixels per μm: {px_per_micron:.1f}\n'.format(px_per_micron=px_per_micron))

    measurements = []
    annotated_img = image.copy()

    print('\nclick pairs of points to measure vertical distances \nclose the window when done\n')

    fig_an, ax_an = plt.subplots(figsize=fs)
    # ax_an.imshow(annotated_img, cmap='gray')
    ax_an.imshow(cropped, cmap='gray')
    ax_an.set_title('click pairs of points to measure vertical distances')

    points = []

    def onclick(event):
        if event.button == 1:  # left mouse button

            # plot single point
            pt_mkr = '_' if dist_type=='vertical' else '|'
            points.append((event.xdata, event.ydata))
            # ax_an.scatter(event.xdata, event.ydata, marker='_', color='r')
            ax_an.scatter(event.xdata, event.ydata, marker=pt_mkr, color='r')
            fig_an.canvas.draw()

            if len(points) == 2:
                (x1, y1), (x2, y2) = points
                dx = abs(x2 - x1); dy = abs(y2 - y1)
                if dist_type=='vertical':
                    dist = dy / px_per_micron
                    box_coords = (x1+20, (y1+y2)/2)
                elif dist_type=='horizontal':
                    dist = dx / px_per_micron
                    box_coords = ((x1+x2)/2, y1+30)
                print('\nmeasured vertical distance: {dist:.0f} nm'.format(dist=dist*1E3))

                # store the measurement
                measurements.append((base_impath, len(measurements)+1, dist*1E3))

                # annotate the image
                if dist_type=='vertical':
                    ax_an.plot([x1, x1], [y1, y2], 'r-')
                elif dist_type=='horizontal':
                    ax_an.plot([x1, x2], [y1, y1], 'r-')
                ax_an.annotate('{msmt_num}: \n{dist:.0f} nm'.format(msmt_num=len(measurements), dist=dist*1E3), box_coords, color='k', bbox=dict(boxstyle='square, pad=0.3', fc='w', ec='k', lw=1), fontsize=6, ha='center')
                fig_an.canvas.draw()

                # reset points for the next measurement
                points.clear()

    cid = fig_an.canvas.mpl_connect('button_press_event', onclick)   # connect the click event to the figure
    plt.show()
    fig_an.canvas.mpl_disconnect(cid)   # disconnect the event handler when the figure is closed

    if save_annotated and measurements:
        anim_path = annotated_dir + base_impath.split('.')[0] + fn_comments + '.pdf'
        ax_an.set_title('')
        fig_an.savefig(anim_path, dpi=300, bbox_inches='tight')
    plt.close()

    return [(m[0], m[1], m[2]) for m in measurements]
