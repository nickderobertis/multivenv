FROM python:3.10

WORKDIR app

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv sync

# Set up a sample folder for cli testing
RUN mkdir cli-testing

COPY . .
RUN pipenv run python upload.py --build-only
RUN pip install dist/multivenv*.whl
RUN mvenv --install-completion bash
COPY tests/input_files/requirements.in cli-testing

WORKDIR cli-testing