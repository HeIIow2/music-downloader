# https://packaging.python.org/en/latest/tutorials/packaging-projects/
cp ../README.md README.md

echo "building......"
python3 -m pip install --upgrade build
python3 -m build

echo "cleaning up......."
rm README.md
# shellcheck disable=SC2164
cd ../build
rm -rf dist
mv ../src/dist .

echo "uploading......."
# python3 -m pip install --upgrade twine
twine upload dist/*
