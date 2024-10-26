to build lib
python setup.py sdist bdist_wheel

to upload
twine upload dist/*

install on local ENV
pip install dist/your_api_name-0.1.0-py3-none-any.whl


