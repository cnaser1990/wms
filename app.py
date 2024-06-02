import io
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import numpy as np
from PIL import Image
import rasterio
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGE_PATH = "path_to_your_image.tif"

def validate_bbox(bbox: str) -> list:
    bbox_values = list(map(float, bbox.split(',')))
    if len(bbox_values) != 4:
        raise ValueError("Bounding box should have exactly 4 values")
    return bbox_values

def read_raster(bbox_values: list, width: int, height: int) -> np.ndarray:
    with rasterio.open(IMAGE_PATH) as src:
        window = src.window(*bbox_values)
        data = src.read(
            window=window, 
            out_shape=(src.count, height, width), 
            resampling=rasterio.enums.Resampling.bilinear
            )
        nodata = src.nodata
        if nodata is not None:
            data[data == nodata] = 0
    return np.clip(data, 0, 255)

def apply_transparency(img: Image.Image, transparency: int) -> Image.Image:
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[:3] == (0, 0, 0):
            alpha = 255 - int((transparency / 100) * 255)
            new_data.append((0, 0, 0, alpha))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def create_tile(data: np.ndarray, transparency: int, format: str) -> Image.Image:
    if data.shape[0] == 1:
        img = Image.fromarray(data[0].astype(np.uint8), mode='L').convert("RGBA")
        if transparency > 0:
            img = apply_transparency(img, transparency)
    else:
        img = Image.fromarray(np.transpose(data, (1, 2, 0)).astype(np.uint8), mode='RGBA')
        if transparency > 0:
            img = apply_transparency(img, transparency)

    if format.lower() == "jpeg":
        img = img.convert("RGB")
    return img


# http://localhost:8000/wms?bbox=51.49628407,34.12773635,51.49814594,34.13008529&width=512&height=256&transparent=90&format=png
@app.get("/wms")
def wms(
    bbox: str = Query(...), 
    width: int = Query(512), 
    height: int = Query(512), 
    transparent: int = Query(0, ge=0, le=100),
    format: str = Query("png", regex="^(png|jpeg)$")
):
    logger.info(f"Received WMS request with bbox: {bbox}, width: {width}, height: {height}, transparency: {transparent}, format: {format}")  
    try:
        bbox_values = validate_bbox(bbox)
        data = read_raster(bbox_values, width, height)
        img = create_tile(data, transparent, format)
        buffer = io.BytesIO()
        img.save(buffer, format=format.upper())
        buffer.seek(0)
        return StreamingResponse(buffer, media_type=f"image/{format}")
    except Exception as e:
        logger.error(f"Error processing WMS request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
