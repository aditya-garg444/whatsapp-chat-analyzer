#!/bin/bash

# Skip the Rust installation if it's already present
echo "Skipping rustup installation since Rust is already installed."

# Set writable directories for Cargo and Rustup to avoid read-only file system errors
export CARGO_HOME=/tmp/cargo
export RUSTUP_HOME=/tmp/rustup

# Ensure that the directories are writable
mkdir -p $CARGO_HOME $RUSTUP_HOME

# Update the path to make sure we use the correct cargo
export PATH=$CARGO_HOME/bin:$PATH

# If the .cargo/env file exists, source it to set environment variables
if [ -f "$HOME/.cargo/env" ]; then
  source $HOME/.cargo/env
fi

# Confirm Rust installation and print version
rustc --version
cargo --version
