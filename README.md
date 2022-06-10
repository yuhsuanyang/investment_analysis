# investment_analysis

- Create virtual environment: `python3 -m venv investment-analysis`
- Activate virtual environment: `source investment-analysis/bin/activate`
- Switch to virtual environment: in `bin`, `source activate investment_analysis`
- Install packages: `pip install -r requirements.txt`
- Initialize db: `python3 manage.py makemigrations` then `python3 manage.py migrate`
- `sh run.sh`
- 名詞解釋:
  - 投資總額: 目前庫存的成本
  - 投資總損益: 庫存總損益+已實現損益
  - 報酬率: 庫存報酬率+已實現報酬率
  - 庫存報酬率: 庫存總損益/投資總額
  - 已實現報酬率: 已實現報酬/投資總額
