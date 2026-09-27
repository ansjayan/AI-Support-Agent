import os
import zipfile

root = "/work/runtime-package-313"
output = "/work/customer_support_agent_v10.zip"

with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
    for directory, _, files in os.walk(root):
        for filename in files:
            path = os.path.join(directory, filename)
            arcname = os.path.relpath(path, root)

            st = os.stat(path)

            info = zipfile.ZipInfo(arcname)
            info.create_system = 3
            info.external_attr = st.st_mode << 16
            info.compress_type = zipfile.ZIP_DEFLATED

            with open(path, "rb") as f:
                z.writestr(info, f.read())

print("Created:", output)
