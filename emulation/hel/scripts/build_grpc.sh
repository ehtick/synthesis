#!/bin/bash

# Exit script if any command fails
set -e
set -o pipefail

cd $1 # GRPC folder

TOOLCHAIN=arm-frc2019-linux-gnueabi

ADDITIONAL_FLAGS="-Wno-error"
export CXXFLAGS="$CXXFLAGS $ADDITIONAL_FLAGS"
export CFLAGS="$CFLAGS $ADDITIONAL_FLAGS"

git submodule update --init

if [[ $(which grpc_cpp_plugin) == "" || $(which protoc) == "" ]] ; then
    printf "Installing native gRPC\n\n"
    make -j10 && \
        sudo make install && \
        sudo ldconfig
    make clean
else
    printf "Native gRPC installed. Skipping native build.\n\n"
fi

printf "Cross-compiling and installing gRPC\n\n"

export GRPC_CROSS_COMPILE=true
export GRPC_CROSS_AROPTS="cr --target=elf32-little"

make plugins static -j10 \
     HAS_PKG_CONFIG=false \
     CC=$TOOLCHAIN-gcc \
     CXX=$TOOLCHAIN-g++ \
     CPP=$TOOLCHAIN-cpp \
     RANLIB=$TOOLCHAIN-ranlib \
     LD=$TOOLCHAIN-ld \
     LDXX=$TOOLCHAIN-g++ \
     HOSTLD=$TOOLCHAIN-ld \
     AR=$TOOLCHAIN-ar \
     AS=$TOOLCHAIN-as \
     AROPTS='-r' \
     PROTOBUF_CONFIG_OPTS="--host=$TOOLCHAIN --with-protoc=$(find . -name protoc -print -quit)"