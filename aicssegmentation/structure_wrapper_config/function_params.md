# Description of parameters in each function widget

### Intensity Normalization

#### method description
Auto-contrast normalizaiton. First, *mean* and standard deviaion (*std*) of the original intensity in image are calculated. Next, the intensity is truncated into range `[mean - a * std, mean + b * std]`, and then recaled to `[0, 1]`. `a` and `b` are parameters controling effect of the adjustment.

#### Parameters:
*scaling_param: a list of two float values, corresponding to `a` and `b` in the description above.

### Size Filter

### method description
Assume the input is a binary image. The size filter will remove any objects with size smaller than `min_size`.

### Parameters:
*min_size: an integer value, corresponding to the `min_size` in the description above.
*method: selection from [`3D` | `slice-by-slice`]. `3D` means the size is calculated and applied in 3D. `slice-by-slice` means the size is calculated and applied in a slice by slice manner.
