# Nemo fix
## Step 1: Install Required Dependencies

bash

```bash
# Install basic build tools and shells
sudo apt update
sudo apt install -y build-essential gfortran git csh tcsh

# Install graphics and development libraries
sudo apt install -y libx11-dev libxt-dev libxext-dev libcairo-dev
sudo apt install -y pgplot5 libpgplot-dev libcfitsio-dev
sudo apt install -y libhdf4-dev libhdf5-dev hdf5-tools cmake pkg-config

# Install RPC library (critical for falcON)
sudo apt install libtirpc-dev
```

## Step 2: Download and Configure NEMO

bash

```bash
# Navigate to your working directory
cd ~/Astrophysics/NEMO\ Libraries/

# Clone NEMO repository
git clone https://github.com/teuben/nemo.git
cd nemo

# Configure with PGPLOT graphics
./configure --with-yapp=pgplot
```

## Step 3: Build NEMO

bash

```bash
# Build the main NEMO system
make build check bench5

# Source the environment (needed each session)
source nemo_start.sh
```

## Step 4: Fix falcON Compilation Issues

The key issue was the missing RPC headers. After installing `libtirpc-dev`, falcON compiled successfully during the main build.

## Step 5: Test falcON Installation

bash

```bash
# Check if gyrfalcON is available
which gyrfalcON
gyrfalcON --help

# Create test data
mkplummer falcon_test.dat 1000 seed=123

# Run falcON simulation
gyrfalcON in=falcon_test.dat out=falcon_out.dat tstop=0.5 eps=0.01 step=0.1 kmax=6
```
