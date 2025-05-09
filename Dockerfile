FROM python:3.12.6

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY okta_group_lister.py .

ENTRYPOINT ["python3", "okta_group_lister.py"]