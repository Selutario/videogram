from setuptools import setup, find_packages

install_requires = []
with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='telegram_videos_bot',
    version='1.0.0',
    author='Selutario',
    author_email='selutario@gmail.com',
    install_requires=install_requires,
    packages=find_packages('telegram_videos_bot'),
)
