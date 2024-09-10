# Training Point Management

Welcome to the Training Point Management Web API repository! This project is designed to provide a comprehensive backend solution for managing and tracking
training points for students. Developed using Django, this Web API offers a robust framework for handling user authentication, data management, and real-time
interactions with the [Frontend Application](https://github.com/HiepThanhTran/TPM-Mobile-App/), which is built using React Native.


## Installation

- Clone the project

```bash
git clone https://github.com/HiepThanhTran/TPM-API.git
cd TPM-API
```

- Create a virtual environment

```bash
python3 -m venv .venv
```

- Activate the environment

```bash
source venv/bin/activate   # On Windows: venv\Scripts\activate
``` 

- Install packages from requirements.txt

```shell
pip install -r requirements.txt
```
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`CLOUDINARY_API_KEY=your-cloudinary-api-key`

`CLOUDINARY_API_SECRET=your-cloudinary-api-secret`

`CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name`

`DATABASE_NAME=your-database-name`

`DATABASE_HOST=your-database-host`

`DATABASE_PASSWORD=your-database-password`

`DATABASE_PRISMA_URL=your-database-prisma-url`

`DATABASE_URL=your-database-url`

`DATABASE_URL_NON_POOLING=your-database-url-non-pooling`

`DATABASE_URL_NO_SSL=your-database-url-no-ssl`

`DATABASE_USER=your-database-user`

`SECRET_KEY=your-database-secret-key`
## Run Locally

- Create mysql database in your computer or use your database

- Change engine, name, user, password of DATABASES variable in core/settings.py

- Run makemigrations and migrate

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

- Run a data collection if you want sample data (This may take a while)

```bash
python3 manage.py collectdata
```

- This command will create a superuser with:
    - username: admin@gmail.com
    - password: admin@123
- Note: Create superuser if you don't run collectdata command

```bash
python3 manage.py createsuperuser
```

- Run project

```bash
python3 manage.py runserver
```
- Go to [admin page](http://127.0.0.1:8080/admin/) to view data
- Go to [swagger page](https://trainingpoint.vercel.app/swagger/) to view API documentation
