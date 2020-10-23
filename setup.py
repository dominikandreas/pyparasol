from setuptools import setup, find_packages

setup(
    name='pyparasol',
    version='1.0.0',
    url='https://github.com/dominikandreas/pyparasol.git',
    author='Dominik Andreas',
    author_email='dominikandreas@users.noreply.github.com',
    description='Web-based visualization tool for hyper-parameters based on Parasol (parallel coordinates)',
    packages=find_packages(),
    install_requires=['pandas', 'numpy', 'flask'],
    entry_points={
            'console_scripts': [
                'pyparasol = pyparasol.main:main',
            ],
        }
)
