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

# Set up test cases
RUN mkdir cli-testing/single
COPY tests/input_files/requirements.in cli-testing/single
COPY tests/input_files/mvenv.yaml cli-testing/single
RUN mkdir cli-testing/multiple
COPY tests/input_files/requirements.in cli-testing/multiple
COPY tests/input_files/multiple/mvenv.yaml cli-testing/multiple

WORKDIR cli-testing