# Code Formatting with `clang-format`

## Installing `clang-format`

### Windows

- Click [here](https://github.com/llvm/llvm-project/releases/download/llvmorg-16.0.6/LLVM-16.0.6-win64.exe) to download the latest version of `llvm` for windows.
- Run the installer and follow the instructions.
- When prompted to choose to link to the system `PATH` skip this step, `link_llvm.bat` will do this for you.
- Once done run `link_llvm.bat` as administrator to link `clang-format` to the system `PATH`.  

### Linux

- Run the following commands to install `clang-format` on your system:

```Text
sudo wget -qO- https://apt.llvm.org/llvm-snapshot.gpg.key | sudo tee /etc/apt/trusted.gpg.d/apt.llvm.org.asc
sudo add-apt-repository "deb http://apt.llvm.org/jammy/  llvm-toolchain-jammy-16 main"
sudo apt-get update
sudo apt-get install -y clang-format-16
```

### MacOS

- Ensure you have [Homebrew](https://brew.sh/) installed.
- Run the following command to install `clang-format` on your system:

```Text
brew install clang-format
```

## How to run `clang-format` with the Visual Studio IDE

- Open the root project folder in Visual Studio.
- Ensure you are at the root of the project.
- Open the terminal in the IDE (`` Ctrl + ` `` by default) or press "View" and then "Terminal" in the menu bar.
- Copy and paste the following command into the terminal depending on your operating system:
  - Windows: `.\scripts\format\format_all.ps1`
  - OSX `./scripts/format/format_all.sh`

## How to run `clang-format` from the Command Line

- Open the root project folder in your terminal.
- Copy and paste the following command into the terminal depending on your os and press enter.
  - Windows: `.\scripts\format\format_all.ps1`
    - Note: If you do not have your `ExecutionPolicy` set to `RemoteSigned` or `Unrestricted` the powershell script will not work. Run `.\scripts\win\resolve_deps.bat` to fix this.
  - OSX / Linux: `./scripts/format/format_all.sh`
