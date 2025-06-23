FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim

WORKDIR /app

COPY ["starter.py","./"]

RUN pip install pandas scikit-learn==1.5.0 pyarrow

CMD ["python", "starter.py", "2023", "5"]