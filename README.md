# Web Map Service (WMS)

This project provides a Web Map Service (WMS) using FastAPI and Rasterio. It processes raster images, applies transparency, and returns the tile in either PNG or JPEG format.

## Features

- Validate bounding box inputs
- Read and process raster images
- Apply transparency to images
- Serve images in PNG or JPEG format via an API endpoint

## Requirements

- Python 3.9+
- FastAPI
- Uvicorn
- Pillow
- Rasterio
- NumPy

## Installation

**1. Clone the repository:**
 * git clone https://github.com/cnaser1990/wms.git
 * cd wms
   
**2. Create a virtualenv and install dependencies :**
 * python -m venv venv
 * source venv/bin/activate
 * pip install -r requirements.txt
   
**3. Put your file path in code** 

**4. Run app :**
 * uvicorn app:app --reload --port 8000
   
**6. Make a GET request to the /wms endpoint with the following query parameters:**
 * bbox (required): Bounding box coordinates (comma-separated values)
 * width (optional): Width of the output image (default: 512)
 * height (optional): Height of the output image (default: 512)
 * transparent (optional): Transparency percentage (0-100, default: 0)
 * format (optional): Output image format (png or jpeg, default: png).
 * Example : http://localhost:8000/wms?bbox=51.49628407,34.12773635,51.49814594,34.13008529&width=500&height=600&transparent=90&format=png
