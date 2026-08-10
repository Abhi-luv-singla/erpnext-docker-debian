from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bin_tracking",
    version="0.0.1",
    author="ERPNext",
    author_email="admin@erpnext.com",
    description="Warehouse bin tracking system with QR code and barcode support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frappe/bin_tracking",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "frappe",
        "erpnext",
        "qrcode",
        "Pillow",
    ],
)
