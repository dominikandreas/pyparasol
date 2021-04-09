export VERSION=$(git tag | sort | tail -1)
sed -i "s/version='.*'/version='$VERSION'/g" setup.py
python setup.py sdist

echo running python -m twine upload --repository-url "https://upload.pypi.org/legacy/" "dist/pyparasol-$VERSION*"
python -m twine upload --repository-url "https://upload.pypi.org/legacy/" "dist/pyparasol-$VERSION*"
