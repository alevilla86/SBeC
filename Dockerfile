# docker buildx build ./sbec --platform=linux/amd64 -t alevilla86/sbec
# docker push alevilla86/sbec
# docker container run -i --name SBeC alevilla86/sbec

FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Copy the source code
COPY ./__init__.py /usr/local/sbec/

# Copy the dataseet
COPY ./cleaned_travel_dataset.csv /usr/local/sbec/

# Copy the requirements
COPY ./requirements.txt /usr/local/sbec/

WORKDIR /usr/local/sbec

# Install the dependencies
RUN pip install -r requirements.txt

# Run the application
CMD ["python3", "__init__.py"]