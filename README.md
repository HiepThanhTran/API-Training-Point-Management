# Training Point Management

Welcome to the Training Point Management Web API repository!

## Installation

1. Clone the project

```shell
git clone https://github.com/HiepThanhTran/TPM-API.git
cd TPM-API
```

2. Create venv for this project

```shell
python -m venv .venv
source .venv/bin/activate
```

3. Download packages in requirements.txt file

```shell
pip install -r requirements.txt
```

4. Environment Variables

    - Create a .env file in the root directory and add the following:

    ```shell
     CLOUDINARY_API_KEY=your-cloudinary-api-key
     CLOUDINARY_API_SECRET=your-cloudinary-api-secret
     CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name
     POSTGRES_DATABASE=your-postgres-database
     POSTGRES_HOST=your-postgres-host
     POSTGRES_PASSWORD=your-postgres-password
     POSTGRES_PRISMA_URL=your-postgres-prisma-url
     POSTGRES_URL=your-postgres-url
     POSTGRES_URL_NON_POOLING=your-postgres-url-non-pooling
     POSTGRES_URL_NO_SSL=your-postgres-url-no-ssl
     POSTGRES_USER=your-postgres-user
     SECRET_KEY=your-postgres-secret-key
    ```

5. Create mysql database in your computer or use your database

6. Change name, user, password of **DATABASES** variable in core/settings.py

7. Run makemigrations and migrate

```shell
python3 manage.py makemigrations
python3 manage.py migrate
```

8. Run a data collection if you want sample data **(This may take a while)**

```shell
python3 manage.py collectdata
```

    - This command will create a superuser with:
        - **username**: admin@gmail.com
        - **password**: admin@123

    - Note: Create superuser if you don't run collectdata command

    ```shell
    python3 manage.py createsuperuser
    ```

9. Run project

```shell
python3 manage.py runserver
```

    - Go to [admin page](http://127.0.0.1:8080/admin/) to view data
