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
        'numpy==1.26.4',
        'pandas==1.3.5',
        'openpyxl>=3.1.5',
        'requests>=2.31.0',
        'google-cloud-speech>=2.26.0',
        'google-cloud-storage>=2.16.0',
        'gspread>=6.1.2',
        'oauth2client>=4.1.3',
        'pydub>=0.25.1',
        'openai>=1.30',
        'matplotlib>=3.5.1',
        'torch>=2.3.0',
        'transformers>=4.40.2',
        'ffmpeg-python>=0.2.0',
        'konlpy>=0.6.0',
        'jamo>=0.4.1',
        'beautifulsoup4==4.12.3',
    ],
    data_files=[
        ('key', key_files),
        ('public', public_files)
    ],
)