# Malvinas GYM — Backend Django

## Puesta en marcha

```bash
python -m venv venv

venv\Scripts\activate en Windows
# o
source venv/bin/activate

pip install -r requirements.txt

copy .env.example .env 
o
cp .env.example .env            # completar credenciales de Postgres

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver
```
