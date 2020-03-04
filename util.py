import os
import numpy as np
import tensorflow as tf
from PIL import Image
from augment import augment_function

def check_folder(log_dir):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir

def shannon_entropy(x):
    """
    Shannon entropy of a 2D array
    """
    xprime = np.maximum(np.minimum(x, 1-1e-8), 1e-8)
    return -np.sum(xprime*np.log2(xprime), axis=1)


def dataset(data_samples, ys = None, imshape=(32,32), num_channels=3,
                 num_parallel_calls=None, norm=255, batch_size=256,
                 augment=False, unlab_fps=None, shuffle=False,
                 sobel=False, single_channel=False):
    """
    return a tf dataset that iterates over a list of images once
    
    :fps: list of filepaths
    :ys: array of corresponding labels
    :imshape: constant shape to resize images to
    :num_channels: channel depth of images
    :batch_size: just what you think it is
    :augment: augmentation parameters (or True for defaults, or False to disable)
    :unlab_fps: list of filepaths (same length as fps) for semi-
        supervised learning
    :shuffle: whether to shuffle the dataset
    :sobel: whether to replace the input image with its sobel edges
    :single_channel: if True, expect a single-channel input image and 
        stack it num_channels times.
    
    Returns
    :ds: tf.data.Dataset object to iterate over data. The dataset returns
        (x,y) tuples unless unlab_fps is included, in which case the structure
        will be ((x, x_unlab), y)
    :num_steps: number of steps (for passing to tf.keras.Model.fit())
    """
    if augment:
        _aug = augment_function(imshape, augment)
    
    ds = tf.data.Dataset.from_tensor_slices(data_samples)
    if augment: ds = ds.map(_aug, num_parallel_calls=num_parallel_calls)
    if sobel: ds = ds.map(_sobelize, num_parallel_calls=num_parallel_calls)

    if unlab_fps is not None:
        u_ds = _image_file_dataset(unlab_fps, imshape=imshape, num_channels=num_channels,
                      num_parallel_calls=num_parallel_calls, norm=norm,
                      single_channel=single_channel)
        if augment: u_ds = u_ds.map(_aug, num_parallel_calls=num_parallel_calls)
        if sobel: u_ds = u_ds.map(_sobelize, num_parallel_calls=num_parallel_calls)
        ds = tf.data.Dataset.zip((ds, u_ds))
    if ys is not None:
        ys = tf.data.Dataset.from_tensor_slices(ys)
        #if unlab_fps is not None:
        #    ys = ds.zip((ys,ys))
        #    #ys = ds.zip((u_ds,ys))
        ds = ds.zip((ds, ys))

    ds = ds.batch(batch_size)
    #if sobel:
    #    ds = ds.map(_sobelize, num_parallel_calls=num_parallel_calls)
    ds = ds.prefetch(1)

    num_steps = int(np.ceil(len(data_samples)/batch_size))
    return ds, num_steps




def _load_img(f, norm=255, num_channels=3, resize=None):
    """
    Generic image-file-to-numpy-array loader. Uses filename
    to choose whether to use PIL or GDAL.

    :f: string; path to file
    :norm: value to normalize images by
    :num_channels: number of input channels (for GDAL only)
    :resize: pass a tuple to resize to
    """
    if type(f) is not str:
        f = f.numpy().decode("utf-8")
    if ".tif" in f:
        img_arr = tiff_to_array(f, swapaxes=True,
                             norm=norm, num_channels=num_channels)
    else:
        img = Image.open(f)
        img_arr = np.array(img).astype(np.float32)/norm

    if resize is not None:
        img_arr = np.array(Image.fromarray(
                (255*img_arr).astype(np.uint8)).resize((resize[1], resize[0]))
                    ).astype(np.float32)/norm
    # single-channel images will be returned by PIL as a rank-2 tensor.
    # we need a rank-3 tensor for convolutions, and may want to repeat
    # across 3 channels to work with standard pretrained convnets.
    if len(img_arr.shape) == 2:
        img_arr = np.stack(num_channels*[img_arr], -1)
    return img_arr.astype(np.float32)  # if norm is large, python recasts the array as float64
