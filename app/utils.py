from io import BytesIO
import hashlib
from PIL import Image
from imagehash import dhash

import faiss
import numpy as np
from faiss import IndexBinaryFlat

def load_index(filename:str = 'faiss_index', hash_size: int = 16) -> IndexBinaryFlat:
    d = hash_size**2
    try:
        return faiss.read_index_binary(f'{filename}_{d}')
    except RuntimeError:
        return faiss.IndexBinaryFlat(d)

def save_index(index: IndexBinaryFlat, filename:str = 'faiss_index', hash_size: int = 16) -> None:
    d = hash_size**2
    faiss.write_index_binary(index, f'{filename}_{d}')



def read_imagefile(data):
    image = Image.open(data)
    return image

def hash_image(im: Image, hash_size: int) -> np.ndarray:
    im_hash = dhash(im[0], hash_size=hash_size)

    # convert image hash from [hash_size, hash_size] binary array 
    # to uint8 [1, hash_size**2] array
    return np.packbits(np.array(im_hash.hash).reshape(1,hash_size**2), axis=1)

def check_duplicate(index: IndexBinaryFlat, img_hash: np.ndarray, thresh: int) -> bool:
    (lims, D, I) = index.range_search(img_hash, thresh)
    print(lims, len(D), I)
    return len(D) > 0

    
def read_gblfile(data):
    # image = Image.open(BytesIO(data))
    # print(image)
    file = BytesIO(data)
    return file

# BLOCK_SIZE = 65536 # The size of each read from the file


def hash_gbl(im, hash_size: int) -> np.ndarray:
    file_hash = hashlib.sha256() # Create the hash object, can use something other than `.sha256()` if you
    with open(im, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data: 
                break
            file_hash.update(data)
    listttt = list(bin(int.from_bytes(file_hash.digest(), 'little'))[2:146]) #2:227
    desired_array = [int(numeric_string) for numeric_string in listttt]
   
    return np.packbits(np.array(desired_array).reshape(1, hash_size**2), axis=1)
