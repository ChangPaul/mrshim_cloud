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
    pipmain(["install", st.secrets.pkg_mrshim])

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

st.markdown("A *suite of web applications* provided by [MR Shim GmbH](https://www.mrshim.de).")
st.markdown(
    "These apps are used for **MRI** applications (see [magnetic resonance imaging](https://en.wikipedia.org/wiki/Magnetic_resonance_imaging)). " + 
    "More specifically for **active shimming** of the static the magnetic field of MRI scanners (see [B0 shimming](https://www.mriquestions.com/why-shimming.html))."
)

st.markdown("---")
st.write("OS:", platform.system())
st.write("Python: ver.", platform.python_version())
st.write("MRShim: ver.", mrshim.__version__)
