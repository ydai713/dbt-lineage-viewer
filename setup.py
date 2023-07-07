from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dbt_lineage_viewer",
    version="1.0.3",
    author="Yang Dai",
    author_email="yang.dai2020@gmail.com",
    description="A DBT lineage viewer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ydai713/dbt-lineage-viewer",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
    ],
    entry_points={
        "console_scripts": [
            "dbt-lineage-viewer=dbt_lineage_viewer:main",
        ],
    },
)
