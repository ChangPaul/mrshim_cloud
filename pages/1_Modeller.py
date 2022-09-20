# -*- coding: utf-8 -*-
"""
 Copyright (C) MR Shim GmbH - All Rights Reserved
 Unauthorized copying of this file, via any medium is strictly prohibited
 proprietary and confidential

Created on Fri Aug 05 22:20:04 2022

@author: Paul
"""
import toml
import tempfile
import streamlit as st
import numpy as np

from pathlib import Path
from fileio import loadmri
from imageproc import imagesegm
from shimutils import plot3dimage
from scipy.ndimage import median_filter, morphology


file_ext = ["par", "rec", "npz"]

# ==============================================
#                   FUNCTIONS
# ==============================================

def download_files(file_list, dirpath="", file_ext=None):
    file_list = [f for f in file_list if (file_ext is None) or (Path(f.name).suffix.lower()[1:] in file_ext)]
    for file in file_list:
        with open(Path(dirpath) / file.name, "wb") as f:
            f.write(file.getbuffer())
    return [Path(dirpath) / f.name for f in file_list]

@st.cache
def import_data_files(ref_file, data_file):
    with tempfile.TemporaryDirectory() as tmpdirname:
        b0maps = download_files(data_file, dirpath=tmpdirname, file_ext=file_ext)
        b0maps = [
            loadmri(f)[2] for f in b0maps
            if (f.suffix.lower() == ".par" and (f.with_suffix(".rec").name.lower() in [f.name.lower() for f in b0maps])) or \
                (f.suffix.lower().endswith(".npz"))
        ]
        hdr, mask, refb0, _ = loadmri(download_files(ref_file, dirpath=tmpdirname, file_ext=file_ext)[0])

    mask = morphology.binary_dilation(imagesegm(mask, method="default"), iterations=2, border_value=1)
    b0maps = [np.ma.array(median_filter(b0 - refb0, size=2), mask=mask) for b0 in b0maps]
    return hdr["coords"], b0maps

# ==============================================
#                   GUI
# ==============================================

st.title("Modeller")
st.sidebar.markdown("Modeller")

ref_file = st.file_uploader("Upload reference field map files", type=file_ext, accept_multiple_files=True)
data_file = st.file_uploader("Upload B0 field map files", type=file_ext, accept_multiple_files=True)

if ref_file and data_file:

    coords, b0maps = import_data_files(ref_file, data_file)
    st.success("Successfully imported files.")
    st.write("B0 maps size:", b0maps[0].shape)
    st.write(plot3dimage(b0maps[0]))
