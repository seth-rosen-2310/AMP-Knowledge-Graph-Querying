import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="AMPhionQA",
    version="1.0.0",
    author="Seth",
    author_email="sethrosen487@gmail.com",
    description="AMPhionQA Docker version",
    install_requires=required,
   
)