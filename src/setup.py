from setuptools import setup, find_packages
from setuptools.command.install import install

package_data_list = [
    "data/settings.yaml",
    "data/schema_db.sql",
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
    version='1.1.0',
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
    python_requires=">=3.8.10"
)
