pyinstaller --onefile src/run_cli.py

exit

# https://packaging.python.org/en/latest/tutorials/packaging-projects/
echo "building......"
python3 -m pip install --upgrade build
python3 -m build

echo "uploading......."
python3 -m pip install --upgrade twine
twine upload dist/music_kraken*
# twine upload --repository testpypi dist/*
