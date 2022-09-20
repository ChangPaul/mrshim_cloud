# -*- coding: utf-8 -*-
"""
 Copyright (C) MR Shim GmbH - All Rights Reserved
 Unauthorized copying of this file, via any medium is strictly prohibited
 proprietary and confidential

Created on Fri Aug 05 22:20:04 2022

@author: Paul
"""
import toml
import importlib, platform
import streamlit as st
from pathlib import Path

if importlib.util.find_spec("mrshim") is None:
    from pip._internal import main as pipmain
    pipmain(["install", "bin/mrshim-1.2.8-cp38-cp38-linux_x86_64.whl"])

import mrshim
pkg_dir = Path(mrshim.__file__).parent
for binfile in (pkg_dir / "bin/libs").iterdir():
    if binfile.suffix.lower() == ".so" and "lin64" not in binfile.stem:
        binfile.unlink()

with open(pkg_dir / "bin/libs/calcshim.lic", "w") as f:
    f.write(st.secrets.access_token)

# ==============================================
#                   GUI
# ==============================================

st.title("Introduction")
st.sidebar.markdown("Introduction")

st.write("OS:", platform.system())
st.write("Python: ver.", platform.python_version())
st.write("MRShim:", pkg_dir)

from fileio import loadmri
from imageproc import imagesegm
from shimutils import plot3dimage

print(loadmri.__doc__)
print(imagesegm.__doc__)
print(plot3dimage.__doc__)