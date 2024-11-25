from setuptools import setup, find_packages

# Membaca isi dari requirements.txt
with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="oims",  # Ganti dengan nama aplikasi Anda
    version="1.0.0",
    description="Custom App for OIMS",
    author="Your Name",
    author_email="youremail@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,  # Menautkan dependencies dari requirements.txt
)
