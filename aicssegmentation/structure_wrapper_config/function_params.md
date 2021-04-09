# Description of parameters in each function widget

***Note: the parameters described here are only for the widgets in the Napari plugin. Not all parameters are exposed to the widget for the sake of simplicity. For programmer users, please refer the full documentation to see the detailed APIs.***  

### 1. Intensity Normalization

#### method description
Auto-contrast normalizaiton. First, *mean* and standard deviaion (*std*) of the original intensity in image are calculated. Next, the intensity is truncated into range `[mean - a * std, mean + b * std]`, and then recaled to `[0, 1]`. `a` and `b` are parameters controling effect of the adjustment.

#### parameters:
* scaling_param: a list of two float values, corresponding to `a` and `b` in the description above.


### 2. Intensity Normalization with bound

#### method description
Auto-contrast normalization. Similat to *Intensity Normalization* above, but with two extra parameters: one upper bound and one lower bound. The intensity of the image will be first clipped into the range defined by the upper bound and the lower bound, and then do the normalization as in *Intensity Normalization*.

#### parameters:
* scaling_param: a list of four values. The first two are float values, as in *Intensity Normalization*. The last two are integer values corresponding to the lower bound and upper bound respectively.

### 3. Intensity Normalization using min-max with bound

#### method description
Min-Max normalization, but the intensity will be clipped by an upper bound first. Namely, any original intensity value higher than an upper bound will be considered as outlier and reset using min intensity of the image. After the clipping, the max intensity will be mapped to 1 and min intensity will be mapped to 0

#### parameters:
* scaling_param: a list of one integer value, corresponding to the upper bound described above.

### 4. Edge Preserving Smoothing

#### method description
A smoothing method that reduce the noise, while retaining the sharp edges.

#### parameters:
N/A

### 5. Image Smoothing Gaussian 3D

#### method description
A smoothing method based on 3D Gaussian filter

#### parameters:
* sigma: the size of the Gaussian kernal. Larger kernel will result in more smoothing effect.


### 6.

#### method description


#### parameters:

### 4.

#### method description


#### parameters:

### 4.

#### method description


#### parameters:

### 4.

#### method description


#### parameters:

### 4.

#### method description


#### parameters:



### Size Filter

### method description
Assume the input is a binary image. The size filter will remove any objects with size smaller than `min_size`.

### Parameters:
*min_size: an integer value, corresponding to the `min_size` in the description above.
*method: selection from [`3D` | `slice-by-slice`]. `3D` means the size is calculated and applied in 3D. `slice-by-slice` means the size is calculated and applied in a slice by slice manner.
