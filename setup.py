try:
    from setuptools import setup, Command, find_packages
    setuptools_available = True
except ImportError:
    from distutils.core import setup, Command, find_packages
    setuptools_available = False

#     packages=['music_kraken'],

#packages = find_packages(where="src")
packages = ['music_kraken', 'music_kraken.lyrics', 'music_kraken.audio_source', 'music_kraken.target', 'music_kraken.metadata', 'music_kraken.tagging', 'music_kraken.utils', 'music_kraken.audio_source.sources', 'music_kraken.database']

print("packages")
print(packages)
# packages.extend(["music_kraken.database"])

setup(
    name='music-kraken',
    version='1.0',
    description='An extensive music downloader crawling the internet. It gets its metadata from a couple metadata '
                'provider, and it scrapes the audiofiles.',
    author='Hellow2',
    author_email='Hellow2@outlook.de',
    url='https://github.com/HeIIow2/music-downloader',
    packages=packages,
    package_dir={'': 'src'},
    install_requires=[
        "requests~=2.28.1",
        "mutagen~=1.46.0",
        "musicbrainzngs~=0.7.1",
        "jellyfish~=0.9.0",
        "pydub~=0.25.1",
        "youtube_dl", 
        "beautifulsoup4~=4.11.1", 
        "pycountry~=22.3.5"
    ],
    entry_points={'console_scripts': ['music-kraken = music_kraken:cli']}
)
