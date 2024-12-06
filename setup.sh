# setup.sh
# Skip rustup installation path check if Rust is already installed
curl https://sh.rustup.rs -sSf | sh -s -- -y

# Set the writable directories for Cargo and Rustup
export CARGO_HOME=/tmp/cargo
export RUSTUP_HOME=/tmp/rustup
mkdir -p $CARGO_HOME $RUSTUP_HOME

# Source the Rust environment variables
source $HOME/.cargo/env
