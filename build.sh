echo "Installing dev deps\n"
pip3 install -r requirements-dev.txt
echo "Cleaning library build\n"
rm -r build/ dist/ pypods.egg-info
echo "Building library\n"
python setup.py sdist bdist_wheel
echo "Building docs\n"
pdoc pypods/ -o docs