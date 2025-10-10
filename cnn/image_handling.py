from PIL import Image
import warp as wp
import numpy as np

@wp.kernel
def convolve(kernel: wp.array(dtype=float),
             kernel_width: int,
             kernel_half: int,
             pixels: wp.array(dtype=wp.vec3),
             num_rows: int,
             num_cols: int,
             output: wp.array(dtype=wp.vec3)):
    '''Apply supplied convolution kernel to the given image.'''
    tid = wp.tid()
    row_idx = tid // num_cols
    col_idx = tid % num_cols
    new_val = wp.vec3(0., 0., 0.)
    
    # The new value of a pixel is the weighted sum of the kernel applied to surrounding pixels
    for i in range(kernel_width):
        for j in range(kernel_width):
            term_row = row_idx - kernel_half + i
            term_col = col_idx - kernel_half + j

            # Prevent segmentation faults for edge pixels
            if 0 <= term_row < num_rows and 0 <= term_col < num_cols:
                new_val += kernel[kernel_width * i + j] * pixels[num_cols * term_row + term_col]
    
    output[tid] = new_val

def launch_convolution(image: Image, kernel: list | np.ndarray | wp.array = None, kernel_width: int=3):
    '''Apply supplied convolution kernel to the given image. Takes a PIL Image object and potential
    kernel specifications and returns a convolved copy PIL Image.'''
    if kernel is None:
        width_squared = pow(kernel_width, 2.)
        kernel = wp.array(np.ones(int(width_squared)) / width_squared, dtype=float)     # Default homogeneous kernel
    else:
        if not isinstance(kernel, wp.array):
            kernel = wp.array(kernel, dtype=float)
        
        kernel = kernel.flatten()
        kernel_width = int(np.sqrt(kernel.shape[0]))
    
    # Prepare Warp kernel arguments
    kernel_half = kernel_width // 2
    pixels = wp.array(np.asarray(image), dtype=wp.vec3).flatten()
    (num_cols, num_rows) = image.size
    output = wp.zeros(num_rows * num_cols, dtype=wp.vec3)

    # Convolve all pixels in parallel
    wp.launch(kernel=convolve,
              dim=num_rows*num_cols,
              inputs=[kernel,
                      kernel_width,
                      kernel_half,
                      pixels,
                      num_rows,
                      num_cols,
                      output])

    # Configure output array for Image object
    output = output.numpy().reshape(num_rows, num_cols, 3)
    return Image.fromarray(output.astype(np.uint8))

if __name__ == '__main__':
    image = Image.open('cnn\images\cat_in_grass.jfif')
    convolved_image = launch_convolution(image, kernel_width=5)
    convolved_image.save(r'cnn\images\blurry_cat.png')