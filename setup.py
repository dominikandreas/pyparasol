from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyparasol',
    version='1.0b2',
    url='https://github.com/dominikandreas/pyparasol.git',
    author='Dominik Andreas',
    author_email='dominikandreas@users.noreply.github.com',
    description='Web-based visualization tool for hyper-parameters based on Parasol (parallel coordinates)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['pandas', 'numpy', 'flask'],
    entry_points={
            'console_scripts': [
                'pyparasol = pyparasol.main:main',
            ],
        },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Framework :: Flask",
        "Environment :: Web Environment",
        "Topic :: Scientific/Engineering :: Visualization"
    ],
    python_requires='>=3.6',
)
