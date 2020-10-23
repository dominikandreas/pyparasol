echo running python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/pyparasol-$(git tag | sort | tail -1)*
python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/pyparasol-$(git tag | sort | tail -1)*
