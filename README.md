# C-V2XMsgExchangeProceossAssessmentTool
This repository is a software tool to automatically measure and assess C-V2X message exchanging process based on SAE J2735 and IEEE 1609.3 and 1609.2 standards. 

## How To Use
### Set-up
1. Install Python 3.12. If you already have it, skip to the next step. If not, install Python 3.12 depending on your operating system:
  - Windows: Install [here](https://www.python.org/downloads/release/python-31212/)
  - Ubuntu/Debian Linux — Run the following commands
      ```
      sudo apt update
      sudo apt install software-properties-common -y
      sudo add-apt-repository ppa:deadsnakes/ppa -y
      sudo apt update
      sudo apt install python3.12 python3.12-venv python3.12-dev -y
      ```
2. Install Git
  - Windows: Install [here](https://git-scm.com/install/windows)
  - Ubuntu/Debian Linux:
    ```
    sudo apt update
    sudo apt install git -y
    ```

3. Install Pandas:
  - Windows:
      ```pip install pandas```
  - Ubuntu/Debian Linux:
      ```
      sudo apt update
      sudo apt install python3-pandas
      ```

4. Clone this repository:
  - ```
    git clone https://github.com/eysong/C-V2XMsgExchangeAssessingTool.git
    cd C-V2XMsgExchangeAssessingTool
    ```

### Program Instructions
5. The input will be via Command Prompt and is formatted this way: python main.py *vendor1* *transmitter_file_name.pdml* *vendor2* *received_file_name.pdml* > output.csv
