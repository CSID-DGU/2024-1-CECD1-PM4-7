from setuptools import setup, find_packages
import glob

key_files = glob.glob('key/*.json')
public_files = glob.glob('public/*')

setup(
    name="CECD",
    version="0.2",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
      'pandas',
      'google-cloud-speech',
      'google-cloud-storage',
      'pydub',
      'openai'
    ],
    data_files=[
        ('key', key_files),
        ('public', public_files)
    ],
)
