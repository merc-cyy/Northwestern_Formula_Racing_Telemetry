## daq-analysis-25
NFR25 Vehicle Analysis 

## Installation

1. Clone this repo

```sh
git clone https://github.com/nu-formula-racing/daq-analysis-25
```

2. Create and active a python virtual enviornment

```sh
python -m venv venv
source venv/Scripts/Activate
pip install -r requirements.txt
```

3. Enjoy!

## Transforming Data
Copy your log files into a directory (like data), then run the command:
```sh
python daq.py transform <data_dir> <output_dir>
```
For example:
```
python daq.py transform data out
```

## Plotting Data
Our interface 
```sh
streamlit run app.py
```

   