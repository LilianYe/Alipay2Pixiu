# Alipay2Pixiu
This Python script is used to read data from Alipay and WeChat payment transactions, and then classify the transactions based on pre-defined rules or using an AI model.

## Requirements

- Python 3.x
- pandas
- requests
- json
- openai

## Installation

1. Clone or download this repository to your local machine.
2. Install the required packages by running the following command: 

```
pip install pandas requests json openai
```

## Usage

1. Put your Alipay transaction CSV file in the same directory as the script, and change the `zfb_path` variable in the script to match your file name.
2. Put your WeChat payment transaction CSV file in the same directory as the script, and change the `wx_path` variable in the script to match your file name.
3. Run the script by entering the following command in your terminal:

```
python alipay_wechat_classifier.py
```

4. The script will read the data from your Alipay and WeChat payment transaction CSV files and classify the transactions based on pre-defined rules or using an AI model.
5. The script will output a CSV file named `my_data.csv` that contains the classified transactions.

## Customization

- You can customize the pre-defined rules for transaction classification by modifying the `rules` and `detail_rules` dictionaries in the script.
- You can customize the default expense type and the list of expense types by modifying the `default_expense` and `expense_types` variables in the script.
