FROM python:3.10

WORKDIR /kitten_exhibition

COPY requirements.txt /kitten_exhibition/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /kitten_exhibition/

CMD ["sh", "-c", "sleep 10 && python manage.py runserver localhost:8000"]
