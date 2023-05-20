# Algorithmic Trading

This project focuses on developing an algorithmic trading system to automate trading decisions in financial markets. The goal is to leverage computer algorithms and mathematical models to execute trades efficiently, capitalize on market opportunities, and remove human biases from the decision-making process.

---

## Table of Contents

- [Algorithmic Trading](#algorithmic-trading)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Installation](#installation)
    - [Clone the repository:](#clone-the-repository)
    - [Navigate to the project directory:](#navigate-to-the-project-directory)
    - [Install the required python version](#install-the-required-python-version)
      - [Install the pyenv](#install-the-pyenv)
        - [Linux (Ubuntu, Debian, and similar)](#linux-ubuntu-debian-and-similar)
        - [macOS (using Homebrew)](#macos-using-homebrew)
        - [Windows](#windows)
      - [Install the required python version](#install-the-required-python-version-1)
    - [Set up a virtual environment](#set-up-a-virtual-environment)
      - [Activate the virtual environment:](#activate-the-virtual-environment)
    - [Install the project dependencies:](#install-the-project-dependencies)
    - [Execute the project setup](#execute-the-project-setup)
  - [Usage](#usage)
  - [Contributing](#contributing)
  - [License](#license)

---

## Introduction

The Algorithmic Trading Project aims to design and implement an automated trading system using cutting-edge algorithms and market analysis techniques. The project leverages the power of technology to analyze market data, identify trading opportunities, and execute trades with minimal latency. By automating trading decisions, we can enhance speed, accuracy, and consistency while reducing emotional biases.

---

## Installation

### Clone the repository:

```bash
git clone https://github.com/PedroFerreiraBento/MT5-Algorithmic-Trading.git
```

### Navigate to the project directory:

```bash
cd MT5-Algorithmic-Trading
```

### Install the required python version
   
#### Install the pyenv

##### Linux (Ubuntu, Debian, and similar)
  - Install prerequisites:
    ```bash
    sudo apt-get update 
    sudo apt-get install curl git
    ```
  - Install `pyenv`:
    ```bash
    curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
    ```
  - Add `pyenv` to your shell configuration file (e.g., `~/.bashrc` or `~/.bash_profile`):
    ```bash
    echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
    source ~/.bashrc
    ```
##### macOS (using Homebrew)
  - Install Homebrew (if not already installed):
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
  - Install `pyenv` using Homebrew:
    ```bash
    brew update
    brew install pyenv
    ```
  - Add `pyenv` to your shell configuration file (e.g., `~/.bash_profile` or `~/.zshrc`):
    ```bash
    echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
    echo 'eval "$(pyenv init -)"' >> ~/.zshrc
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
    source ~/.zshrc
    ```
##### Windows
  - Install the `pyenv-win` running the following command in a PowerShell terminal:
    ```PowerShell
    Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
    ```
  - If you are getting any `UnauthorizedAccess` error then start Windows PowerShell with the **"Run as administrator"** option and run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine`, now re-run the above installation command.

#### Install the required python version
```bash
pyenv install --skip-existing "$(cat .python-version)"
```

### Set up a virtual environment

```bash
python -m venv TradingEnvironment
```

#### Activate the virtual environment:

- ##### On Windows:

    ```bash
    .\TradingEnvironment\Scripts\activate
    ```

- ##### On macOS and Linux:

    ```bash
    source TradingEnvironment/bin/activate
    ```

### Install the project dependencies:

```bash
pip install -r requirements.txt
```

### Execute the project setup

```bash
python ./setup.py install
```

---

## Usage

1. Run the project:

    ```
    python main.py
    ```

---

## Contributing

Contributions are welcome! If you have any improvements or bug fixes, feel free to submit a pull request. Please make sure to follow the [contribution guidelines](CONTRIBUTING.md).

---

## License

This project is licensed under the [MIT License](LICENSE).
