@echo off
git submodule update --init --recursive
cd protocols
proto_compile.bat
