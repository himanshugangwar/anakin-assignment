**Anakin Assignment Project Setup**

Python Version: 3.x
Django: 4.x
DB: Django Built-in mysqllite


1. Install pip, Virtualenv and Virtualenvwrapper

- sudo apt-get install python3-pip
- pip3 install virtualenv virtualenvwrapper

2. Setup VirtualEnvWrapper

- mkdir .virtualenvs 
- Edit $HOME/.bash_profile
- Add following lines:

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_VIRTUALENV=/Users/{your_user}/Library/Python/3.8/bin/virtualenv
source /Users/{home_directory}/Library/Python/3.8/bin/virtualenvwrapper.sh

3. Make Virtualenv using Virtualenvwrapper

- mkvirtualenv anakin

4. Activate Virtualenv 

- workon anakin 

5. Git Clone Repository

- git clone https://github.com/himanshugangwar/anakin-assignment.git

6. Install requirements from requirements.txt
- cd anakin-assignment
- pip install -r requirements.txt

7. Migrate DB
./manage.py makemigrations

./manage.py migrate

8. Run Server

- python manage.py runserver


Check Server is running at http://127.0.0.1:8000/
