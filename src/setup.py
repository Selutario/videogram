from setuptools import setup, find_packages
from setuptools.command.install import install

package_data_list = [
    "data/settings.yaml",
    "locale/*/*/*.po"
]

scripts_list = [
    'videogram=videogram.main:main',
]


class InstallWithCompile(install):
    def run(self):
        from babel.messages.frontend import compile_catalog
        import glob
        import os

        for lang_path in glob.glob('**/locale/*/LC_MESSAGES/*.po'):
            compiler = compile_catalog(self.distribution)
            compiler.directory = 'build/lib/videogram/locale'
            compiler.locale = os.path.basename(lang_path).replace('.po', '')
            compiler.domain = [compiler.locale]
            compiler.use_fuzzy = True
            compiler.run()

        super().run()



setup(
    name='videogram',
    version='2.0.0',
    author='Selutario',
    author_email='selutario@gmail.com',
    packages=find_packages(),
    cmdclass={
        'install': InstallWithCompile
    },
    package_data={
        'videogram': package_data_list
    },
    include_package_data=True,
    entry_points={
        'console_scripts': scripts_list
    },
    setup_requires=[
        'wheel',
        'babel'
    ],
    install_requires=[
        "wheel==0.40.0",
        "babel==2.12.1",
        "SQLAlchemy==2.0.12",
        "numpy==1.24.3",
        "python-telegram-bot==20.2",
        "cython==0.29.21",
        "pandas==2.0.1",
        "joblib==1.2.0",
        "scipy==1.10.1",
        "threadpoolctl==2.1.0",
        "scikit-learn==1.2.2",
        "pyyaml==5.3.1",
        "ruamel.yaml==0.17.4",
        "appdirs==1.4.4"
    ],
    python_requires=">=3.8.10"
)
