from setuptools import setup

setup(
    name="screenviz",
    version="0.0.3",
    author="Noam Teysser",
    author_email="Noam.Teyssier@ucsf.edu",
    packages=["screenviz"],
    description="a tool to assign an identity to a table of barcode guides",
    entry_points={'console_scripts': ['screenviz = screenviz.__main__:main_cli']},
    install_requires=[
        "numpy",
        "pandas",
        "plotly"]
)
