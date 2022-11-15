# https://packaging.python.org/en/latest/tutorials/packaging-projects/
echo "building............"
python3 -m pip install --upgrade build
python3 -m build

echo "uploading............"
python3 -m pip install --upgrade twine
twine upload dist/music_kraken*

# twine upload --repository testpypi dist/music_kraken*
# exit

echo "pushing............"
git add .
git commit -am "new build and upload"
git push

echo "compiling............"
mkdir -p dist/build_files
mkdir -p dist/compiled

pyinstaller --onefile src/music_kraken_cli.py --specpath dist/build_files --workpath dist/build_files --distpath dist/compiled
