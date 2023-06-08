from typing import Optional

from pygltflib import GLTF2
from pygltflib.utils import ImageFormat
import os

from fastapi import FastAPI, File, UploadFile
from fastapi.param_functions import Form
from fastapi.middleware.cors import CORSMiddleware

from app.models import AddResponse
from app.utils import check_duplicate, hash_image, read_imagefile, load_index, save_index, read_gblfile, hash_gbl

app = FastAPI(
  title="Duplicate image detection system",
  version="1.0",
  description="An API for detecting duplicate images from a user-defined database"
)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
Upload a single image to the duplicate image database
"""
@app.post("/api/add/image", status_code=201, response_model=AddResponse)
async def add_image(file: UploadFile = File(...), hash_size:Optional[int] = Form(16), 
    index_name:Optional[str] = Form('faiss_index')):

    # load index
    index = load_index(index_name, hash_size)

    img = read_imagefile(await file.read())
    img_hash = hash_image(img, hash_size)

    # update index and save
    index.add(img_hash)
    save_index(index, hash_size=hash_size)

    return {"added": [file.filename] }

"""
Upload multiple images to the duplicate image database
"""
# @app.post("/api/add/images", status_code=201, response_model=AddResponse)
# async def add_images(files: List[UploadFile] = File(...), 
#     hash_size:Optional[int] = Form(16), index_name:Optional[str] = Form('faiss_index')):

#     # load index
#     index = load_index(index_name, hash_size)

#     # hash images
#     imgs = [read_imagefile(await file.read()) for file in files]
#     img_hashes = [hash_image(img, hash_size) for img in imgs]

#     # update index and save
#     for img_hash in img_hashes:
#         index.add(img_hash)
    
#     save_index(index, hash_size=hash_size)

#     return {"added": [file.filename for file in files]}

# @app.post("/api/add/images", status_code=201, response_model=AddResponse)
# async def add_images(files: UploadFile = File(...), 
#     hash_size:Optional[int] = Form(8), index_name:Optional[str] = Form('faiss_index')):

#     if files.filename:
#         fn = os.path.basename(files.filename)

#         open(fn, 'wb').write(files.file.read())
#         gltf = GLTF2().load(fn)
#         # gltf.images[0].name = "cube.png"  # will save the data uri to this file (regardless of data format)
#         # print(gltf.images)
#         gltf.convert_images(ImageFormat.FILE, override=True) 
#         # print(gltf)

#     # load index

#     folder_dir = "D:\myprojects\python\DUP-IMG-SEARCH"
#     for images in os.listdir(folder_dir):
#         if (images.endswith(".png" or '.jpg')):
#             index = load_index(index_name, hash_size)

#             # with open(images, 'rb') as f:
#             #     print(f)
#             #     imgs = [read_imagefile(f.read())]
#             #     # print(imgs)
#             img_hashes = hash_image(images, hash_size)
    
#             index.add(img_hashes)
    
#             save_index(index, hash_size=hash_size)

#     return {"added": [files.filename]}

@app.post("/api/add/images", status_code=201, response_model=AddResponse)
async def add_images(file: UploadFile = File(...), 
    hash_size:Optional[int] = Form(16), index_name:Optional[str] = Form('faiss_index')):

    if file.filename:
        fn = os.path.basename(file.filename)
        open(fn, 'wb').write(file.file.read())

        gltf = GLTF2().load(fn)
        gltf.convert_images(ImageFormat.FILE, override=True) 

    if (len(gltf.images) > 0):
        folder_dir = "D:\myprojects\python\DUP-IMG-SEARCH"
        for images in os.listdir(folder_dir):
            if (images.endswith(".png") or images.endswith('.jpg')):
                index = load_index(index_name, hash_size)

                
                imgs = [read_imagefile(images)]
                img_hashes = hash_image(imgs, hash_size)
        
                index.add(img_hashes)
        
                save_index(index, hash_size=hash_size)

        for things in os.listdir(folder_dir):
            if things.endswith('.png') or things.endswith('.jpg') or things.endswith('.glb'):
                os.remove(things) 

        return {"added": [file.filename]}

    else:

            # load index
        index = load_index(index_name, 12)

        # hash image
        # img = read_gblfile(await file.read())
        img_hash = hash_gbl(fn, 12)

        index.add(img_hash)
        
        save_index(index, hash_size=12)

        folder_dir = "D:\myprojects\python\DUP-IMG-SEARCH"
        for things in os.listdir(folder_dir):
            if things.endswith('.glb'):
                os.remove(things) 

    return {"added": [file.filename]}


"""
Check an image against the duplicate image database
"""
@app.post("/api/check")
async def check_image(dist:int = Form(...), file: UploadFile = File(...), 
    hash_size:Optional[int] = Form(16), index_name:Optional[str] = Form('faiss_index')):

    if file.filename:
        fn = os.path.basename(file.filename)
        open(fn, 'wb').write(file.file.read())

        gltf = GLTF2().load(fn)
        gltf.convert_images(ImageFormat.FILE, override=True)

    if (len(gltf.images) > 0):
        folder_dir = "D:\myprojects\python\DUP-IMG-SEARCH"
        for images in os.listdir(folder_dir):
            if (images.endswith(".png") or images.endswith('.jpg')):
                print(gltf.images)

                index = load_index(index_name, hash_size)

                imgs = [read_imagefile(images)]
                img_hashes = hash_image(imgs, hash_size)

                if (check_duplicate(index, img_hashes, dist)):
                    for things in os.listdir(folder_dir):
                        if things.endswith('.png') or things.endswith('.jpg') or things.endswith('.glb'):
                            os.remove(things) 
                    return {"duplicated": True}
                else:
                    for things in os.listdir(folder_dir):
                        if things.endswith('.png') or things.endswith('.jpg') or things.endswith('.glb'):
                            os.remove(things) 
                    return {'duplicated': False}
    else:
        

            # load index
        index = load_index(index_name, 12)

        # hash image
        # img = read_gblfile(await file.read())
        img_hash = hash_gbl(fn, 12)

        folder_dir = "D:\myprojects\python\DUP-IMG-SEARCH"
        for things in os.listdir(folder_dir):
            if things.endswith('.glb'):
                os.remove(things) 

        return {"duplicated": check_duplicate(index, img_hash, dist)}


# """
# Check an image against the duplicate image database
# """
# @app.post("/api/check")
# async def check_image(dist:int = Form(...), file: UploadFile = File(...), 
#     hash_size:Optional[int] = Form(8), index_name:Optional[str] = Form('faiss_index')):

#     if file.filename:
#         fn = os.path.basename(file.filename)

#         open(fn, 'wb').write(file.file.read())
#         gltf = GLTF2().load(fn)
#         # gltf.images[0].name = "cube.png"  # will save the data uri to this file (regardless of data format)
#         # print(gltf.images)
#         gltf.convert_images(ImageFormat.FILE, override=True) 
#         # print(gltf)

#     # load index

#     folder_dir = "D:\myprojects\python\DUP-IMG-SEARCH"
#     for images in os.listdir(folder_dir):
#         if (images.endswith(".png")):
#             index = load_index(index_name, hash_size)
#             print(index)
#             # print(images)
#             # with open(images, 'rb') as f:
#             #     print(f)
#             #     imgs = [read_imagefile(f.read())]
#             #     # print(imgs)
#             img_hashes = hash_image(images, hash_size)
#             if (check_duplicate(index, img_hashes, dist)):
#                 print(index)
#                 return {"duplicated"}
#             else:
#                 return {'good to go'}
#             # return {"duplicate": check_duplicate(index, img_hashes, dist)}    

# @app.post("/api/check")
# async def check_image(dist:int = Form(...), file: UploadFile = File(...), 
#     hash_size:Optional[int] = Form(8), index_name:Optional[str] = Form('faiss_index')):

#     # load index
#     index = load_index(index_name, hash_size)

#     # hash image
#     img = read_imagefile(await file.read())
#     img_hash = hash_image(img, hash_size)

#     return {"duplicate": check_duplicate(index, img_hash, dist)}
