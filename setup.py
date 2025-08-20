from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Study Buddy AI - LLM",
    version="0.1",
    author="Prathap",
    packages=find_packages(),
    install_requires = requirements,
)