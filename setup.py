from setuptools import setup, find_packages
import glob

key_files = glob.glob('key/*.json')
public_files = glob.glob('public/*')

setup(
    name="CECD",
    version="0.3",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas',
        'google-cloud-speech',
        'google-cloud-storage',
        'pydub',
        'openai>=1.30',
        'matplotlib',
        'torch',
        'transformers',
        'ffmpeg-python',
        'konlpy>=0.6.0',
        'jamo>=0.4.1'
    ],
    data_files=[
        ('key', key_files),
        ('public', public_files)
    ],
)