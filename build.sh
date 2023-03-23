#!/bin/bash
test=true

rm /tmp/music-downloader/*.db
rm /tmp/music-downloader/*.sql

version=$(cut -d@ -f1 version)
echo version:  $version

git add .
git commit -am "ready for build $version"
git push

sudo python3 -m pip install -U twine wheel setuptools

python3 setup.py sdist bdist_wheel  
sudo python3 -m pip uninstall music-kraken -y

python3 -m pip install dist/music-kraken-$version.tar.gz --user
music-kraken

if [ "$test" = true ];
then
    echo "just a test"
    twine upload --repository testpypi dist/music_kraken*
    python3 -m pip install -i https://test.pypi.org/simple/ music-kraken -U
    exit
fi

twine upload dist/music_kraken*

echo "compiling............"
mkdir -p dist/build_files
mkdir -p dist/compiled

pyinstaller --onefile src/music_kraken_cli.py --specpath dist/build_files --workpath dist/build_files --distpath dist/compiled
exit

# https://packaging.python.org/en/latest/tutorials/packaging-projects/
#echo "building............"
#echo "python3 -m pip install --upgrade build"
# python3 -m pip install --upgrade pip
# python3 -m pip install --upgrade build
#echo "python3 -m build"
# python3 -m build
# python3 setup.py sdist bdist_wheel
# python3 setup.py install --user

# echo "python3 -m pip install dist/music_kraken-1.2.2-py3-none-any.whl --user --force-reinstall"
# python3 -m pip install dist/music_kraken-1.2.2.tar.gz --user --force-reinstall

# music-kraken

# open /home/lars/.local/lib/python3.10/site-packages/music_kraken
# echo "uploading............"
#python3 -m pip install --upgrade twine
#twine upload dist/music_kraken*

# twine upload --repository testpypi dist/music_kraken*
exit

echo "pushing............"
git add .
git commit -am "new build and upload"
git push

echo "compiling............"
mkdir -p dist/build_files
mkdir -p dist/compiled

pyinstaller --onefile src/music_kraken_cli.py --specpath dist/build_files --workpath dist/build_files --distpath dist/compiled
