import subprocess
import sys

# Define the packages with specific version requirements
fixed_versions = {
    "Faker": "13.7.0",
    "pyyaml": "6.0",
    "deprecation": "2.1.0"
}

# Define the packages where the latest compatible version is needed
latest_versions = [
    "setuptools",
    "scipy",
    "pylcs",
    "spacy",
    "medspacy",
    "tqdm",
    "python-dateutil"
]

def install_packages():
    # Install packages with fixed versions
    for package, version in fixed_versions.items():
        subprocess.run([sys.executable, "-m", "pip", "install", f"{package}=={version}"], check=True)
    
    # Install packages with the latest version that's compatible with the specified one
    for package in latest_versions:
        subprocess.run([sys.executable, "-m", "pip", "install", f"{package}"], check=True)

if __name__ == "__main__":
    install_packages()
