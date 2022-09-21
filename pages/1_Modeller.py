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
import mrshim

from pathlib import Path
from scipy.ndimage import median_filter, morphology
from fileio import loadmri
from imageproc import imagesegm
from shimutils import plot3dimage
from calibration import calib_circ

MAX_DIM = 60

file_ext = ["par", "rec", "npz"]
pkg_dir = Path(mrshim.__file__).parent

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
            loadmri(f, maxdim=MAX_DIM)[2] for f in b0maps
            if (f.suffix.lower() == ".par" and (f.with_suffix(".rec").name.lower() in [f.name.lower() for f in b0maps])) or \
                (f.suffix.lower().endswith(".npz"))
        ]
        hdr, magn, refb0, _ = loadmri(download_files(ref_file, dirpath=tmpdirname, file_ext=file_ext)[0], maxdim=MAX_DIM)

    mask = imagesegm(magn, method="default")
    b0maps = [median_filter(b0 - refb0, size=2) for b0 in b0maps]
    return hdr["coords"], magn, b0maps, mask


@st.cache
def run_calib(b0maps, coords, coil_radius, coil_curr, coil_turns):
    cpos, cnorm, shimmed = calib_circ(
        b0maps[0],
        coords,
        coil_radius=coil_radius,
        scale=coil_curr * coil_turns,
        libpath=str(pkg_dir / st.secrets.lib_calc),
    )
    return cpos, cnorm, shimmed


# ==============================================
#                   GUI
# ==============================================

st.title("Modeller")
st.sidebar.markdown("Modeller")

ref_file = st.file_uploader("Upload reference field map files", type=file_ext, accept_multiple_files=True)
data_file = st.file_uploader("Upload B0 field map files", type=file_ext, accept_multiple_files=True)
mask_dilations = st.slider("Mask contraction factor", value=1, min_value=1, max_value=10)

if ref_file and data_file:

    coords, magn, b0maps, mask = import_data_files(ref_file, data_file)
    b0maps = [np.ma.array(b0, mask=morphology.binary_dilation(mask, iterations=mask_dilations, border_value=1)) for b0 in b0maps]
    st.write(plot3dimage(b0maps[0], background=magn, alpha=0.7))

    coil_curr = st.number_input("Coil applied current [A]", value=0.0, min_value=-2.0, max_value=2.0, step=0.001, format="%.3f")
    coil_turns = st.number_input("Coil turns", min_value=1, max_value=30)
    coil_radius = st.number_input("Coil diameter [mm]", value=50, min_value=5, max_value=200)

    placeholder = st.empty()
    run_button_clicked = placeholder.button("Calculate", disabled=False, key="1")
    if run_button_clicked:
        placeholder.button("Calculate", disabled=True, key="2")
        cpos, cnorm, shimmed = run_calib(
            b0maps,
            coords,
            coil_radius=coil_radius * 0.5e-3,
            coil_curr=coil_curr,
            coil_turns=coil_turns,
        )

        st.write(f"Std. dev: Before={np.std(b0maps[0])}, After={np.std(shimmed)}")
        st.write(
            "Coil pos",
            np.round(cpos, 4),
            "norm",
            np.round(cnorm / np.linalg.norm(cnorm), 4),
        )
        st.write(plot3dimage(shimmed - np.mean(shimmed), vmin=-10, vmax=10, figsize=(7, 2)))
