# C-V2XMsgExchangeProcessAssessmentTool
This repository is a software tool to automatically measure and assess C-V2X message exchanging processes based on SAE J2735 and IEEE 1609.3 and 1609.2 standards. It compares the unique attributes of a transmitted packet with the received packet to confirm that the transmitted content is identical. Ultimately, this program determines if a packet was successfully sent from the sender and received by the receiver or, instead, lost during transmission. It also checks for any potential retransmitted V2X messages. The message exchange can be analyzed in three different ways involving a mix of on-board units (OBUs) and road-side units (RSUs). Specifically, it can be from OBU to OBU, OBU to RSU, or RSU to OBU, which are, respectively, vehicle-to-vehicle (V2V), vehicle-to-infrastructure (V2I), and infrastructure-to-vehicle (I2V).

## Supported Vendors/Manufacturers
- Cohda
- Commsignia
- Kapsch
- Qualcomm
- Ettifos
- MioVision
- Denso
- ITTelComm


## How To Use
### Set-up
1. Install Python 3.12. If you already have it, skip to the next step. If not, install Python 3.12 depending on your operating system:
  - Windows: Install [here](https://www.python.org/downloads/release/python-31212/)
  - Ubuntu/Debian Linux — For Ubuntu versions earlier than 24.04, run all the following lines. For users with Ubuntu 24.04 or newer, skip the first three lines.
      ```
      sudo apt update
      sudo apt install software-properties-common -y
      sudo add-apt-repository ppa:deadsnakes/ppa -y
      sudo apt update
      sudo apt install python3.12 python3.12-venv python3.12-dev -y
      ```
  - Red Hat Linux (RHEL)
    ```
    dnf install python3.12
    dnf install python3.12-pip
    ```
  - macOS
    ```
    /bin/bash -c "$(curl -fsSL https://githubusercontent.com)"
    brew install python@3.12
    ```
2. Install Git
  - Windows: Install [here](https://git-scm.com/install/windows)
  - Ubuntu/Debian Linux
    ```
    sudo apt update
    sudo apt install git -y
    ```
  - RHEL
    ```
    sudo dnf update -y
    sudo dnf install git -y
    ```
  - macOS
    ```
    brew install git
    ```

3. Install Pandas:
  - Windows:
      ```pip install pandas```
  - Ubuntu/Debian Linux
      ```
      sudo apt update
      sudo apt install python3-pandas
      ```
  - RHEL
    ```
    pip3.12 install pandas
    ```
  - macOS
    ```
    pip3 install --upgrade pip
    pip3 install pandas
    ```

4. Clone this repository:
  - ```
    git clone https://github.com/eysong/C-V2XMsgExchangeAssessingTool.git
    cd C-V2XMsgExchangeAssessingTool
    ```

### Program Instructions
There will be two different user input options: a pre-built user interface for simplicity or command line.
1. GUI instructions
2. The input will be via Command Prompt and is formatted this way: python main.py *vendor1* *transmitter_file_name.pdml* *vendor2* *received_file_name.pdml* > output.csv
  - For instance:
    ```
    python C-V2XMsgExchangeAssess.py cohda kap_obu2.pdml kap kap_rsu5.pdml > output.csv
    ```

## References
- NIST Public Repository [C-V2X Interoperability Testing Datasets](https://data.nist.gov/od/id/mds2-3541)
- 2026 OmniAir Maryland Plugfest Datasets
- NIST Communications Technology Laboratory Division 673 Testbed Datasets
