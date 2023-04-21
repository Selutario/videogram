from setuptools import setup, find_packages

package_data_list = [
    "data/settings.yaml",
    "data/bot.db"
]

scripts_list = [
    'videogram=Videogram.main:main',
]

setup(
    name='Videogram',
    version='1.1.0',
    author='Selutario',
    packages=find_packages(),
    author_email='selutario@gmail.com',
    package_data={'wazuh_coordinator': package_data_list},
    include_package_data=True,
    install_requires=[
        "numpy==1.19.5",
        "python-telegram-bot==13.7",
        "cython==0.29.21",
        "pandas==1.3.1",
        "joblib==1.0.0",
        "scipy==1.5.4",
        "threadpoolctl==2.1.0",
        "scikit-learn==0.24.1",
        "pyyaml==5.3.1",
        "ruamel.yaml==0.17.4",
    ],
    python_requires=">=3.10.6"
)
